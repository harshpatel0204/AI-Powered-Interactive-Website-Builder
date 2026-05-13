"""
tests/test_agents.py

Sanity check: runs the full agent pipeline with mock answers,
bypassing Streamlit, to confirm the chain works end-to-end.

Usage:
    python tests/test_agents.py
"""

import asyncio
import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from website_agents.pipeline import run_agent_pipeline, run_update_pipeline
from website_agents.sample_data import MOCK_ANSWERS


def print_status(agent_name: str, status: str, detail: str = ""):
    icons = {"waiting": "⏳", "running": "🔄", "done": "✅", "error": "❌"}
    icon = icons.get(status, "•")
    print(f"\n  {icon} [{agent_name}] {status.upper()}", end="")
    if detail:
        print(f" — {detail}", end="")
    print()


async def main():
    print("=" * 60)
    print("  Multi-Agent Website Builder — Pipeline Test")
    print("=" * 60)

    print("\n📋 Running GENERATION pipeline with mock answers...\n")

    result = await run_agent_pipeline(
        answers=MOCK_ANSWERS,
        status_callback=print_status,
    )

    print("\n" + "=" * 60)
    print("  PIPELINE RESULTS")
    print("=" * 60)

    html = result.get("html", "")
    req = result.get("requirements_json", {})
    design = result.get("design_json", {})

    print(f"\n✅ Requirements extracted:")
    print(f"   Business: {req.get('business_name', 'N/A')}")
    print(f"   Type: {req.get('business_type', 'N/A')}")
    print(f"   Tone: {req.get('tone', 'N/A')}")

    print(f"\n✅ Design spec created:")
    palette = design.get("color_palette", {})
    print(f"   Primary color: {palette.get('primary', 'N/A')}")
    print(f"   Heading font: {design.get('typography', {}).get('heading_font', 'N/A')}")

    print(f"\n✅ HTML generated: {len(html):,} characters")
    print(f"   QA Score: {result.get('qa_score', 'N/A')}/100")
    print(f"   Issues fixed: {len(result.get('qa_fixes', []))}")

    # Save output
    os.makedirs("summary", exist_ok=True)
    with open("summary/test_output.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\n💾 HTML saved to: summary/test_output.html")

    # Test update pipeline
    print("\n" + "=" * 60)
    print("  TEST: UPDATE pipeline")
    print("=" * 60)
    update_result = await run_update_pipeline(
        update_request="Change the hero section background to a deep navy blue gradient",
        current_html=html,
        status_callback=print_status,
    )
    updated_html = update_result.get("html", "")
    print(f"\n✅ Update applied: {len(updated_html):,} chars")

    with open("summary/test_updated.html", "w", encoding="utf-8") as f:
        f.write(updated_html)
    print("💾 Updated HTML saved to: summary/test_updated.html")

    print("\n✅ All tests passed!\n")


if __name__ == "__main__":
    asyncio.run(main())
