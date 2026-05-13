# Repository Guidelines

## Project Structure & Module Organization

This is a Python Streamlit app for generating websites through a multi-agent pipeline.

- `streamlit_demo.py` contains the main Streamlit UI, chat flow, preview, and export behavior.
- `website_agents/` contains pipeline stages such as requirements analysis, design architecture, code generation, QA review, and update handling.
- `prompt/` stores prompt templates used by the agents. Keep prompt changes explicit and review generated output after edits.
- `config/settings.py` loads environment configuration from `.env`.
- `tests/` contains executable smoke tests for the agent pipeline.
- `summary/` holds generated HTML artifacts such as `test_output.html`; treat these as runtime outputs.

## Build, Test, and Development Commands

Create and activate a virtual environment before installing dependencies:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Run the local app:

```bash
streamlit run streamlit_demo.py
```

Run the current pipeline smoke test:

```bash
python tests/test_agents.py
```

The test exercises generation and update flows and writes HTML outputs into `summary/`.

## Coding Style & Naming Conventions

Use Python 3.8+ syntax, 4-space indentation, and clear snake_case names for functions, variables, and modules. Keep agent files focused on one pipeline responsibility, following names like `requirements_analyst.py` and `qa_reviewer.py`. Prefer small helper functions over large inline blocks when updating `streamlit_demo.py`. Keep prompt filenames descriptive and aligned with the agent that consumes them.

## Testing Guidelines

There is no pytest suite configured yet; tests are currently direct Python scripts. Add new tests under `tests/` with names beginning `test_`. For changes to `website_agents/`, update or add a smoke test that verifies both successful output shape and useful failure behavior. Because tests can call external AI APIs, ensure `.env` is configured before running them.

## Commit & Pull Request Guidelines

Recent commits use short, imperative summaries such as `update readme file for adding project description`. Keep commit messages concise and focused on one change. Pull requests should include a brief description, relevant issue links, test commands run, and screenshots or generated HTML samples when UI or output changes.

## Security & Configuration Tips

Do not commit `.env`, API keys, or generated logs. Use `.env.sample` to document required variables. Current runtime settings expect OpenRouter variables such as `OPENROUTER_API_KEY`, `OPENROUTER_BASE_URL`, and `OPENROUTER_MODEL`.
