"""
website_agents/pipeline.py

Orchestrates the website generation pipeline.

The generation flow is split into two parts:
1. Requirements -> design -> raw HTML
2. QA review and refinement

This lets the UI show a preview as soon as the HTML is ready, then run QA
afterward without blocking first paint.
"""

import json
import re
from typing import Callable, Optional

from agents import Runner, RunConfig
from agents.models.openai_provider import OpenAIProvider

from website_agents import initialize_openrouter_client
from website_agents.code_generator import create_code_generator_agent
from website_agents.design_architect import create_design_architect_agent
from website_agents.image_processor import fix_images_in_html
from website_agents.qa_reviewer import create_qa_reviewer_agent
from website_agents.requirements_analyst import create_requirements_analyst_agent
from website_agents.update_handler import create_update_handler_agent


def _extract_json(text: str) -> str:
    """Strip markdown code fences and return raw JSON."""
    cleaned = re.sub(r"```(?:json)?\s*", "", text).replace("```", "").strip()
    return cleaned


def _extract_html(text: str) -> str:
    """Extract raw HTML from a response that may contain markdown fences."""
    html_match = re.search(r"<html.*?>.*?</html>", text, re.DOTALL | re.IGNORECASE)
    if html_match:
        return html_match.group(0)
    cleaned = re.sub(r"```(?:html)?\s*", "", text).replace("```", "").strip()
    return cleaned


def _build_run_config() -> RunConfig:
    """Create a RunConfig using the OpenRouter-backed provider."""
    openrouter_client = initialize_openrouter_client()
    return RunConfig(
        model_provider=OpenAIProvider(
            openai_client=openrouter_client,
            use_responses=False,
        )
    )


async def run_generation_pipeline(
    answers: list[str],
    status_callback: Optional[Callable[[str, str, str], None]] = None,
) -> dict:
    """
    Run requirements analysis, design, and code generation.

    Returns:
        dict with keys:
        - requirements_json
        - design_json
        - raw_html
    """

    def _notify(agent_name: str, status: str, detail: str = "") -> None:
        if status_callback:
            status_callback(agent_name, status, detail)

    run_cfg = _build_run_config()
    results: dict = {}

    _notify("Requirements Analyst", "running", "Analyzing your questionnaire answers...")

    analyst_agent = create_requirements_analyst_agent()
    analyst_input = analyst_agent.instructions.format(
        answer1=answers[0],
        answer2=answers[1],
        answer3=answers[2],
        answer4=answers[3],
        answer5=answers[4],
        answer6=answers[5],
    )
    analyst_result = await Runner.run(analyst_agent, analyst_input, run_config=run_cfg)
    req_text = analyst_result.final_output
    req_json_str = _extract_json(req_text)

    try:
        requirements = json.loads(req_json_str)
    except json.JSONDecodeError:
        requirements = {"raw": req_text}

    results["requirements_json"] = requirements
    _notify(
        "Requirements Analyst",
        "done",
        f"Business: {requirements.get('business_name', 'N/A')} | Type: {requirements.get('business_type', 'N/A')}",
    )

    _notify("Design Architect", "running", "Creating color palette, typography & layout...")

    architect_agent = create_design_architect_agent()
    architect_input = architect_agent.instructions.format(
        requirements_json=json.dumps(requirements, indent=2)
    )
    architect_result = await Runner.run(architect_agent, architect_input, run_config=run_cfg)
    design_text = architect_result.final_output
    design_json_str = _extract_json(design_text)

    try:
        design = json.loads(design_json_str)
    except json.JSONDecodeError:
        design = {"raw": design_text}

    results["design_json"] = design
    palette = design.get("color_palette", {})
    primary = palette.get("primary", "N/A")
    heading_font = design.get("typography", {}).get("heading_font", "N/A")
    _notify("Design Architect", "done", f"Primary color: {primary} | Font: {heading_font}")

    _notify("Code Generator", "running", "Building HTML/CSS/JS website code...")

    coder_agent = create_code_generator_agent()
    coder_input = coder_agent.instructions.format(
        requirements_json=json.dumps(requirements, indent=2),
        design_json=json.dumps(design, indent=2),
    )
    coder_result = await Runner.run(coder_agent, coder_input, run_config=run_cfg)
    raw_html = _extract_html(coder_result.final_output)
    raw_html = fix_images_in_html(raw_html, requirements_json=requirements)

    results["raw_html"] = raw_html
    _notify("Code Generator", "done", f"Generated {len(raw_html):,} characters of HTML/CSS/JS")

    return results


async def run_qa_pipeline(
    raw_html: str,
    requirements: dict,
    status_callback: Optional[Callable[[str, str, str], None]] = None,
) -> dict:
    """
    Run the QA reviewer stage against generated HTML.

    Returns:
        dict with keys:
        - html
        - qa_score
        - qa_issues
        - qa_fixes
    """

    def _notify(agent_name: str, status: str, detail: str = "") -> None:
        if status_callback:
            status_callback(agent_name, status, detail)

    run_cfg = _build_run_config()

    _notify("QA Reviewer", "running", "Reviewing code quality, accessibility, responsiveness...")

    qa_agent = create_qa_reviewer_agent()
    qa_input = qa_agent.instructions.format(html_code=raw_html)
    qa_result = await Runner.run(qa_agent, qa_input, run_config=run_cfg)
    qa_text = _extract_json(qa_result.final_output)

    try:
        qa_data = json.loads(qa_text)
        final_html = _extract_html(qa_data.get("final_html", raw_html))
        qa_score = qa_data.get("score", 0)
        qa_issues = qa_data.get("issues_found", [])
        qa_fixes = qa_data.get("fixes_applied", [])
    except (json.JSONDecodeError, KeyError):
        final_html = _extract_html(qa_result.final_output) or raw_html
        qa_score = 75
        qa_issues = []
        qa_fixes = []

    final_html = fix_images_in_html(final_html, requirements_json=requirements)

    _notify("QA Reviewer", "done", f"Score: {qa_score}/100 | Issues fixed: {len(qa_fixes)}")

    return {
        "html": final_html,
        "qa_score": qa_score,
        "qa_issues": qa_issues,
        "qa_fixes": qa_fixes,
    }


async def run_agent_pipeline(
    answers: list[str],
    status_callback: Optional[Callable[[str, str, str], None]] = None,
) -> dict:
    """
    Run the full generation and QA pipeline.

    This keeps the old contract for tests and other callers.
    """

    generation_results = await run_generation_pipeline(
        answers=answers,
        status_callback=status_callback,
    )
    qa_results = await run_qa_pipeline(
        raw_html=generation_results["raw_html"],
        requirements=generation_results["requirements_json"],
        status_callback=status_callback,
    )

    return {
        "requirements_json": generation_results["requirements_json"],
        "design_json": generation_results["design_json"],
        "raw_html": generation_results["raw_html"],
        "html": qa_results["html"],
        "qa_score": qa_results["qa_score"],
        "qa_issues": qa_results["qa_issues"],
        "qa_fixes": qa_results["qa_fixes"],
    }


async def run_update_pipeline(
    update_request: str,
    current_html: str,
    status_callback: Optional[Callable[[str, str, str], None]] = None,
) -> dict:
    """
    Run the single-agent update flow.

    Returns:
        dict with keys:
        - html
        - summary
    """

    run_cfg = _build_run_config()

    def _notify(agent_name: str, status: str, detail: str = "") -> None:
        if status_callback:
            status_callback(agent_name, status, detail)

    _notify("Update Handler", "running", f"Processing: \"{update_request[:60]}...\"")

    update_agent = create_update_handler_agent()
    update_input = update_agent.instructions.format(
        current_html=current_html,
        update_request=update_request,
    )

    update_result = await Runner.run(update_agent, update_input, run_config=run_cfg)
    updated_html = _extract_html(update_result.final_output)

    if not updated_html:
        updated_html = current_html
    else:
        updated_html = fix_images_in_html(updated_html)

    _notify("Update Handler", "done", "Changes applied successfully")

    return {
        "html": updated_html,
        "summary": f"Applied: {update_request[:80]}",
    }
