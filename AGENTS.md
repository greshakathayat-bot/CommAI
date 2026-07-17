# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Project Overview

CommAi is a sales intelligence platform. It takes meeting transcripts, extracts client updates/requirements via a LangChain AI agent, and matches them to watsonx Orchestrate product capabilities via a remote MCP server.

Stack: **React 19 + Carbon Design System** (frontend) · **FastAPI + SQLAlchemy + PostgreSQL** (backend) · **LangChain + ChatWxO + MCP** (AI pipeline)

---

## Commands

### Backend (run from `backend/`)
```bash
# First-time setup (creates .venv, installs deps, seeds DB)
bash backend/setup_dev.sh

# Start API server
bash backend/start.sh
# OR manually:
source backend/.venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Seed/re-seed mock data (run from backend/ with venv active)
python -m app.data.seed
```

### Frontend (run from `frontend/`)
```bash
npm run dev       # Vite dev server on :5173
npm run build     # tsc -b && vite build
npm run lint      # oxlint (NOT eslint)
```

### Database
```bash
docker-compose up -d   # Start PostgreSQL on :5432 (run from project root)
```

> **No test framework is configured** — there are no test files or test commands in this project.

---

## Critical Architecture Notes

- **DB tables are created automatically on startup** via `Base.metadata.create_all()` in [`backend/app/main.py`](backend/app/main.py). There are no Alembic migrations in use despite `alembic` being in `requirements.txt`.
- **AI analysis runs as a FastAPI `BackgroundTask`**, not blocking the HTTP response. The endpoint `POST /api/agent/analyze` returns immediately with `"Analysis started"`. Poll `GET /api/transcripts/{id}` for `status` changes: `pending → processing → completed | failed`.
- **MCP tools are loaded per-analysis call** in `_get_mcp_tools()` via `uvx mcp-proxy`. If `uvx` is not on PATH or the remote MCP server is unreachable, the agent silently falls back (no MCP enrichment, only LLM extraction).
- **`get_settings()` is cached with `@lru_cache`** — changes to `.env` after the first call require a process restart to take effect.
- **Settings read `.env` from the CWD**, not from `backend/`. The `.env` file must be in the **project root** (same level as `docker-compose.yml`).
- **Vite proxies `/api/*` to `localhost:8000`** in dev. The axios client in [`frontend/src/api/client.ts`](frontend/src/api/client.ts) uses `VITE_API_URL` env var or falls back to `http://localhost:8000/api` directly — no `/api` prefix stripping needed.

---

## Backend Code Style

- **Imports**: stdlib → third-party → local (`from app.xxx import ...`). Local imports always use `app.*` package paths.
- **Settings**: always access via `get_settings()` (cached singleton), never import env vars directly.
- **DB session**: inject via `Depends(get_db)` in route handlers; never instantiate `SessionLocal` directly in routes.
- **Schemas**: all Pydantic response models use `model_config = {"from_attributes": True}` (Pydantic v2 style — **not** `class Config: orm_mode = True`).
- **Enum values** (e.g. `TranscriptStatus`, `UpdateCategory`, `OpportunityStatus`) are defined in [`backend/app/models.py`](backend/app/models.py) as `str, enum.Enum` so they serialise as strings.
- **All PKs are UUIDs** using `postgresql.UUID(as_uuid=True)` with `default=uuid.uuid4`.
- **Logging**: use `logger = logging.getLogger(__name__)` per module; root logging configured in `main.py`.

## Frontend Code Style

- **Linter**: `oxlint` (not ESLint). Config in [`frontend/.oxlintrc.json`](frontend/.oxlintrc.json). Rules: `react/rules-of-hooks` (error), `react/only-export-components` (warn).
- **TypeScript**: `verbatimModuleSyntax` is on — use `import type` for type-only imports. `noUnusedLocals` and `noUnusedParameters` are errors.
- **All shared API types and fetch functions** live in [`frontend/src/api/client.ts`](frontend/src/api/client.ts) — add new types and endpoints there, not in component files.
- **Carbon theme**: outer shell uses `Theme theme="g100"` (dark), page content uses `Theme theme="white"`. See [`frontend/src/components/Layout.tsx`](frontend/src/components/Layout.tsx).
- **Carbon typography classes** are applied directly via `className="cds--type-*"` (e.g. `cds--type-productive-heading-05`, `cds--type-body-long-01`).
- **No `useState` + `useEffect` abstraction layer** — data fetching is done inline in each page component with `Promise.all`.

---

## Environment Variables

Copy `.env.example` to `.env` in the project root. Key non-obvious vars:

| Variable | Notes |
|---|---|
| `WXO_INSTANCE_URL` | Full instance URL: `https://api.us-south.watson-orchestrate.cloud.ibm.com/instances/<id>` |
| `WXO_MODEL` | Default: `watsonx/ibm/granite-3-8b-instruct` |
| `WXO_MCP_URL` | Default: `https://developer.watson-orchestrate.ibm.com/mcp` — remote MCP via `uvx mcp-proxy` |
| `DATABASE_URL` | Must match docker-compose credentials: `postgresql://commai:commai_secret@localhost:5432/commai` |
