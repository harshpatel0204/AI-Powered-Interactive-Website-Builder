# AI-Powered Interactive Website Builder

This is a Python-based Streamlit application that utilizes a multi-agent pipeline to generate complete, responsive websites based on user requirements gathered through a conversational interface.

## Project Overview

- **Core Technology:** [Streamlit](https://streamlit.io/) for the UI, [Google Gemini AI](https://ai.google.dev/) (via OpenAI-compatible API) for the agent logic.
- **Architecture:** Multi-agent pipeline consisting of:
    1. **Requirements Analyst:** Extracts structured data from user answers.
    2. **Design Architect:** Creates visual specifications (palette, typography).
    3. **Code Generator:** Produces the HTML/CSS/JS code.
    4. **QA Reviewer:** Validates and refines the generated code.
    5. **Update Handler:** Handles iterative changes requested by the user.
- **Key Libraries:** `openai`, `streamlit`, `openai-agents`, `python-dotenv`.

## Building and Running

### Prerequisites
- Python 3.8+
- API Key (Gemini/OpenRouter)

### Setup
1. **Virtual Environment:**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```
2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configuration:**
   Create a `.env` file based on `.env.sample`:
   ```env
   OPENROUTER_API_KEY=your_key
   OPENROUTER_MODEL=openai/gpt-4o-mini
   ```

### Execution
- **Run the App:**
  ```bash
  streamlit run streamlit_demo.py
  ```
- **Run Tests:**
  ```bash
  python tests/test_agents.py
  ```

## Development Conventions

- **Module Organization:**
    - `streamlit_demo.py`: Main entry point and UI logic.
    - `website_agents/`: Core pipeline logic and individual agent definitions.
    - `prompt/`: System prompts for each agent.
    - `config/`: Application settings and environment loading.
- **Coding Style:** Follow PEP 8 (snake_case, 4-space indentation). Use typing hints for clarity.
- **Agent Patterns:** Each agent should have a clear, single responsibility. Use `website_agents/pipeline.py` to orchestrate them.
- **Async Logic:** The pipeline uses `asyncio`. In Streamlit, use `nest_asyncio` and a helper like `run_async` (found in `streamlit_demo.py`) to bridge the sync/async gap.

## Key Files
- `streamlit_demo.py`: Streamlit frontend with chat interface and live preview.
- `website_agents/pipeline.py`: Orchestrator for the generation and update flows.
- `website_agents/image_processor.py`: Post-processes HTML to ensure valid image placeholders.
- `prompt/*.txt`: Instructional prompts that define agent behavior.
- `AGENTS.md`: High-level repository guidelines and architecture notes.
