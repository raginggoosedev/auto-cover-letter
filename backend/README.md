# Backend

The Flask API validates PDF uploads, extracts resume text in memory, retrieves
the LinkedIn job description, requests factual LaTeX from the OpenAI Responses
API, and compiles reviewed LaTeX into a PDF.

Setup and API documentation live in the [repository README](../README.md).

```bash
uv sync --project backend --extra dev
uv run --project backend python -m backend.routes.main
```

Run the backend checks from the repository root:

```bash
uv run --project backend pylint backend/llm backend/routes backend/scraping backend/latex
uv run --project backend pytest backend/tests --cov=backend --cov-config=backend/pyproject.toml --cov-report=term-missing --cov-fail-under=90
```
