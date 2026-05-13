"""
streamlit_demo.py — Multi-Agent AI Website Builder
Powered by OpenAI Agents SDK + OpenRouter
"""

import asyncio
import re
import time
import logging
import sys

import streamlit as st
import nest_asyncio
nest_asyncio.apply()

from website_agents.pipeline import run_agent_pipeline, run_update_pipeline
from website_agents.sample_data import MOCK_ANSWERS

# ─── Logging Config ───────────────────────────────────────────────────────────
try:
    import os
    log_path = os.path.join(os.getcwd(), "website_builder.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(sys.stdout)
        ],
        force=True # Force override any existing logging config
    )
    logger = logging.getLogger("streamlit_app")
    logger.info("Logging initialized at %s", log_path)
except Exception as e:
    st.error(f"Logging initialization failed: {str(e)}")
    logger = logging.getLogger("streamlit_app")

logger.info("AI Website Builder Streamlit app started.")

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Website Builder",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* General font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Agent status card styles */
    .agent-card {
        border-radius: 10px;
        padding: 10px 14px;
        margin-bottom: 8px;
        font-size: 0.85rem;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 10px;
        border: 1px solid transparent;
    }
    .agent-waiting {
        background: #1e1e2e;
        border-color: #3a3a5c;
        color: #a0a0b8;
    }
    .agent-running {
        background: #1a2840;
        border-color: #3b82f6;
        color: #93c5fd;
        animation: pulse 1.8s ease-in-out infinite;
    }
    .agent-done {
        background: #0f2d1f;
        border-color: #22c55e;
        color: #86efac;
    }
    .agent-error {
        background: #2d1010;
        border-color: #ef4444;
        color: #fca5a5;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.65; }
    }

    /* Reasoning block */
    .reasoning-block {
        background: #0d1117;
        border-left: 3px solid #3b82f6;
        border-radius: 4px;
        padding: 10px 14px;
        font-size: 0.8rem;
        color: #8b97b0;
        white-space: pre-wrap;
        font-family: monospace;
    }

    /* QA score badge */
    .qa-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
    }

    /* Step badge */
    .step-badge {
        background: #312e81;
        color: #c7d2fe;
        font-size: 0.72rem;
        padding: 2px 8px;
        border-radius: 12px;
        font-weight: 600;
    }

    /* Override default button styling */
    div.stButton > button[kind="primary"] {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# ─── Questions ────────────────────────────────────────────────────────────────
questions = [
    "👋 Hi! Let's build your website. Could you tell me what your site will be about?",
    "That sounds exciting! What's the **name** of your store or business?",
    "Lovely name! What types of **products or services** are you planning to offer?",
    "Great selection! What are your **key goals** for this website? _(e.g. drive traffic, build brand, newsletter)_",
    "Impressive! What makes you **stand out** from the competition? _(Your unique selling proposition)_",
    "Almost done! Could you share a little about the **story or background** behind your business?",
]

AGENT_NAMES = [
    "Requirements Analyst",
    "Design Architect",
    "Code Generator",
    "QA Reviewer",
]

# ─── Session State ─────────────────────────────────────────────────────────────
_defaults = {
    "current_question": 0,
    "answers": [],
    "chat_history": [],
    "completed": False,
    "generated_html": "",
    "website_generated": False,
    "update_chat_history": [],
    "agent_statuses": {n: {"status": "waiting", "detail": ""} for n in AGENT_NAMES},
    "agent_reasoning": {},   # agent_name → output detail
    "qa_score": None,
    "qa_issues": [],
    "qa_fixes": [],
    "design_json": None,
    "requirements_json": None,
    "pipeline_running": False,
    "show_test_data": False,
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─── Helpers ──────────────────────────────────────────────────────────────────

def reset_agent_statuses():
    st.session_state.agent_statuses = {n: {"status": "waiting", "detail": ""} for n in AGENT_NAMES}
    st.session_state.agent_reasoning = {}
    st.session_state.qa_score = None
    st.session_state.qa_issues = []
    st.session_state.qa_fixes = []


def reset_chat():
    for k, v in _defaults.items():
        st.session_state[k] = v if not callable(v) else v()
    st.session_state.agent_statuses = {n: {"status": "waiting", "detail": ""} for n in AGENT_NAMES}
    st.session_state.agent_reasoning = {}


def agent_status_icon(status: str) -> str:
    return {"waiting": "⏳", "running": "🔄", "done": "✅", "error": "❌"}.get(status, "⏳")


def agent_status_css(status: str) -> str:
    return {"waiting": "agent-waiting", "running": "agent-running", "done": "agent-done", "error": "agent-error"}.get(status, "agent-waiting")


def render_agent_panel():
    """Renders the agent activity panel in the sidebar."""
    st.sidebar.markdown("### 🤖 Agent Activity")
    for name in AGENT_NAMES:
        info = st.session_state.agent_statuses.get(name, {"status": "waiting", "detail": ""})
        icon = agent_status_icon(info["status"])
        css = agent_status_css(info["status"])
        detail_html = f"<br><small style='opacity:0.75'>{info['detail']}</small>" if info["detail"] else ""
        st.sidebar.markdown(
            f'<div class="agent-card {css}">'
            f'{icon} <span>{name}</span>{detail_html}'
            f'</div>',
            unsafe_allow_html=True,
        )

    if st.session_state.qa_score is not None:
        score = st.session_state.qa_score
        color = "#22c55e" if score >= 80 else "#f59e0b" if score >= 60 else "#ef4444"
        st.sidebar.markdown(
            f'<div style="margin-top:8px;text-align:center">'
            f'<span class="qa-badge" style="background:{color}20;color:{color};border:1px solid {color}60">'
            f'QA Score: {score}/100'
            f'</span></div>',
            unsafe_allow_html=True,
        )


def status_callback(agent_name: str, status: str, detail: str = ""):
    """Called by the pipeline to update per-agent statuses in session_state."""
    st.session_state.agent_statuses[agent_name] = {"status": status, "detail": detail}
    if detail:
        st.session_state.agent_reasoning[agent_name] = detail


# ─── Async runner helper (works on Windows/Streamlit) ─────────────────────────

def run_async(coro):
    """Run an async coroutine synchronously, compatible with Streamlit's event loop."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            logger.info("Event loop is already running. Using ThreadPoolExecutor.")
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, coro)
                return future.result()
        else:
            logger.info("Starting new event loop for coroutine.")
            return loop.run_until_complete(coro)
    except RuntimeError:
        logger.info("RuntimeError while getting event loop. Using asyncio.run.")
        return asyncio.run(coro)
    except Exception as e:
        logger.exception("Unexpected error in run_async: %s", str(e))
        raise


# ─── Main Functions ───────────────────────────────────────────────────────────

def load_mock_answers():
    """Populate the setup chat with the same answers used by tests/test_agents.py."""
    st.session_state.answers = MOCK_ANSWERS.copy()
    st.session_state.current_question = len(questions)
    st.session_state.completed = True
    st.session_state.chat_history = []
    for question, answer in zip(questions, MOCK_ANSWERS):
        st.session_state.chat_history.append({"role": "assistant", "content": question})
        st.session_state.chat_history.append({"role": "user", "content": answer})
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": "Test answers loaded. Generating the website now...",
    })


def generate_website_from_answers(answers, source_label="user answers"):
    """Run the main generation pipeline and store outputs in session state."""
    reset_agent_statuses()
    st.session_state.pipeline_running = True

    try:
        logger.info("Starting main agent pipeline with %s.", source_label)
        result = run_async(
            run_agent_pipeline(
                answers=answers,
                status_callback=status_callback,
            )
        )

        st.session_state.generated_html = result["html"]
        st.session_state.requirements_json = result.get("requirements_json", {})
        st.session_state.design_json = result.get("design_json", {})
        st.session_state.qa_score = result.get("qa_score")
        st.session_state.qa_issues = result.get("qa_issues", [])
        st.session_state.qa_fixes = result.get("qa_fixes", [])

        if st.session_state.generated_html:
            st.session_state.website_generated = True
            return True

        st.error("Agents did not produce valid HTML. Please try again.")
        logger.warning("Agent pipeline completed but returned no HTML.")
        return False

    except Exception as e:
        logger.exception("Critical error in main agent pipeline: %s", str(e))
        st.error(f"Pipeline error: {str(e)}")
        return False

    finally:
        st.session_state.pipeline_running = False


# ─── App Layout ───────────────────────────────────────────────────────────────
st.title("🏗️ AI-Powered Website Builder")
st.markdown("Powered by **multiple specialized AI agents** — each one experts in their domain.")

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("📊 Progress")

    if not st.session_state.website_generated:
        progress = len(st.session_state.answers) / len(questions)
        st.progress(progress)
        st.write(f"Questions answered: **{len(st.session_state.answers)}/{len(questions)}**")
        st.divider()
        render_agent_panel()
    else:
        st.success("✅ Website Generated!")
        st.write("Use the chat below to refine your site.")
        st.divider()
        render_agent_panel()

    st.divider()
    if st.button("🔄 Start Over", use_container_width=True):
        reset_chat()
        st.rerun()

    # ── Testing Section ───────────────────────────────────────────────────
    st.divider()
    st.subheader("🧪 Testing & Demo")
    st.info("Quickly test the pipeline with pre-filled answers.")
    
    if st.button("🚀 Use Test Answers", use_container_width=True, type="secondary"):
        st.session_state.show_test_data = True
        load_mock_answers()
        with st.spinner("Generating from test answers..."):
            if generate_website_from_answers(MOCK_ANSWERS, "test answers"):
                st.rerun()

    if st.session_state.show_test_data:
        with st.expander("📝 View Test Q&A", expanded=True):
            for i, (q, a) in enumerate(zip(questions, MOCK_ANSWERS)):
                st.markdown(f"**Q{i+1}:** {q}")
                st.markdown(f"*{a}*")
                if i < len(questions) - 1:
                    st.divider()

# ── Main Area ─────────────────────────────────────────────────────────────────
if not st.session_state.website_generated:

    st.subheader("💬 Setup Chat")

    # Render existing chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if not st.session_state.completed:
        if st.session_state.current_question < len(questions):
            current_q = questions[st.session_state.current_question]

            # Post first/next question if not already shown
            if (
                not st.session_state.chat_history
                or st.session_state.chat_history[-1]["content"] != current_q
            ):
                st.session_state.chat_history.append({"role": "assistant", "content": current_q})
                with st.chat_message("assistant"):
                    st.markdown(current_q)

            user_input = st.chat_input("Type your answer here...")
            if user_input:
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                st.session_state.answers.append(user_input)
                st.session_state.current_question += 1

                if st.session_state.current_question >= len(questions):
                    st.session_state.completed = True
                    done_msg = "🎉 All questions answered! Click **Generate Website** to watch the AI agents build your site."
                    st.session_state.chat_history.append({"role": "assistant", "content": done_msg})

                st.rerun()

    else:
        # Show generate button
        st.info("✨ The agents are ready to build your website. This takes ~30–60 seconds.")

        col1, col2 = st.columns([2, 1])
        with col1:
            generate_btn = st.button("🚀 Generate Website with AI Agents", type="primary", use_container_width=True)

        if generate_btn:
            with st.spinner("AI agents are collaborating to build your website..."):
                if generate_website_from_answers(st.session_state.answers, "user answers"):
                    st.rerun()

else:
    # ── Website Generated View ─────────────────────────────────────────────────
    st.subheader("🎨 Your AI-Generated Website")

    tab1, tab2, tab3, tab4 = st.tabs([
        "🖥️ Preview",
        "💬 Update Website",
        "📋 HTML Code",
        "🧠 Agent Reasoning",
    ])

    # ── Tab 1: Live Preview ────────────────────────────────────────────────────
    with tab1:
        st.markdown("### Live Preview")
        try:
            st.components.v1.html(
                st.session_state.generated_html,
                height=800,
                scrolling=True,
            )
        except Exception as e:
            logger.exception("Error rendering HTML preview: %s", str(e))
            st.error(f"Error rendering HTML: {str(e)}")

    # ── Tab 2: Update via Chat ────────────────────────────────────────────────
    with tab2:
        st.markdown("### 💬 Request Changes")
        st.write("Describe what you want to change — the Update Handler agent will apply it:")
        st.info(
            "• \"Change the primary color to deep purple\"\n"
            "• \"Add a testimonials section with 3 reviews\"\n"
            "• \"Make the hero section taller with a gradient background\"\n"
            "• \"Add a sticky WhatsApp chat button\"\n"
            "• \"Change the font to Poppins\""
        )

        # Render update history
        for message in st.session_state.update_chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if update_request := st.chat_input("What would you like to change?"):
            st.session_state.update_chat_history.append({"role": "user", "content": update_request})
            with st.chat_message("user"):
                st.markdown(update_request)

            with st.spinner("Update Handler agent is applying your changes..."):
                try:
                    logger.info("Starting update pipeline for request: %s", update_request)
                    update_result = run_async(
                        run_update_pipeline(
                            update_request=update_request,
                            current_html=st.session_state.generated_html,
                            status_callback=status_callback,
                        )
                    )
                    new_html = update_result.get("html", "")
                    if new_html:
                        st.session_state.generated_html = new_html
                        msg = "✅ Your website has been updated! Check the **Preview** tab to see the changes."
                    else:
                        msg = "⚠️ The agent couldn't extract clean HTML. The existing site is unchanged."

                    st.session_state.update_chat_history.append({"role": "assistant", "content": msg})
                    with st.chat_message("assistant"):
                        st.markdown(msg)
                    logger.info("Update pipeline completed successfully.")

                except Exception as e:
                    logger.exception("Error in update pipeline: %s", str(e))
                    err_msg = f"❌ Update failed: {str(e)}"
                    st.session_state.update_chat_history.append({"role": "assistant", "content": err_msg})
                    st.error(err_msg)

            st.rerun()

    # ── Tab 3: HTML Source ────────────────────────────────────────────────────
    with tab3:
        st.markdown("### 📋 HTML Source Code")

        col1, col2 = st.columns([3, 1])
        with col2:
            st.download_button(
                label="📥 Download HTML",
                data=st.session_state.generated_html,
                file_name="ai_generated_website.html",
                mime="text/html",
                use_container_width=True,
            )

        st.code(st.session_state.generated_html, language="html", line_numbers=True)

    # ── Tab 4: Agent Reasoning ────────────────────────────────────────────────
    with tab4:
        st.markdown("### 🧠 Agent Reasoning & Outputs")
        st.caption("See what each agent produced during your website generation.")

        # QA Summary
        if st.session_state.qa_score is not None:
            score = st.session_state.qa_score
            color = "green" if score >= 80 else "orange" if score >= 60 else "red"
            st.markdown(f"**Quality Score**: :{color}[{score}/100]")

            if st.session_state.qa_issues:
                with st.expander(f"🐛 Issues Found ({len(st.session_state.qa_issues)})", expanded=False):
                    for issue in st.session_state.qa_issues:
                        st.write(f"• {issue}")

            if st.session_state.qa_fixes:
                with st.expander(f"🔧 Fixes Applied ({len(st.session_state.qa_fixes)})", expanded=False):
                    for fix in st.session_state.qa_fixes:
                        st.write(f"• {fix}")

        st.divider()

        # Per-agent detail + intermediate JSON
        for i, name in enumerate(AGENT_NAMES):
            info = st.session_state.agent_statuses.get(name, {})
            detail = st.session_state.agent_reasoning.get(name, "")
            icon = agent_status_icon(info.get("status", "waiting"))

            with st.expander(f"{icon} {name}", expanded=(i == 0)):
                st.markdown(f'<span class="step-badge">Step {i+1}</span>', unsafe_allow_html=True)
                st.markdown(f"**Status**: {info.get('status', 'waiting').capitalize()}")
                if detail:
                    st.markdown(f"**Summary**: {detail}")

                # Show structured output if available
                if name == "Requirements Analyst" and st.session_state.requirements_json:
                    import json
                    st.markdown("**Extracted Requirements:**")
                    st.json(st.session_state.requirements_json)

                elif name == "Design Architect" and st.session_state.design_json:
                    import json
                    palette = st.session_state.design_json.get("color_palette", {})
                    typo = st.session_state.design_json.get("typography", {})
                    if palette:
                        st.markdown("**Color Palette:**")
                        cols = st.columns(len(palette))
                        for idx, (role, hex_val) in enumerate(palette.items()):
                            safe_hex = hex_val if hex_val.startswith("#") else "#cccccc"
                            cols[idx].markdown(
                                f'<div style="background:{safe_hex};height:50px;border-radius:6px;margin-bottom:4px"></div>'
                                f'<div style="font-size:0.7rem;text-align:center">{role}<br>{safe_hex}</div>',
                                unsafe_allow_html=True,
                            )
                    if typo:
                        st.markdown(f"**Fonts**: `{typo.get('heading_font', 'N/A')}` (headings) / `{typo.get('body_font', 'N/A')}` (body)")

                elif name == "Code Generator":
                    st.markdown(f"**Generated**: `{len(st.session_state.generated_html):,}` characters of HTML/CSS/JS")

                elif name == "QA Reviewer" and st.session_state.qa_score:
                    st.markdown(f"**Final Score**: `{st.session_state.qa_score}/100`")

        # Q&A summary at the bottom
        st.divider()
        with st.expander("📋 Your Original Answers", expanded=False):
            for i, (q, a) in enumerate(zip(questions, st.session_state.answers)):
                st.markdown(f"**Q{i+1}:** {q}")
                st.markdown(f"*A{i+1}:* {a}")
                st.divider()
