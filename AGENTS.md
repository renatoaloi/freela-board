# FreelaBoard — AGENTS.md

## Quick start

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev

# Docker (alternative — frontend on :8080, backend on :8000, healthcheck-gated)
docker compose up --build
```

## Commands

| What | How |
|---|---|
| Run backend dev | `cd backend && uvicorn app.main:app --reload --port 8000` |
| Run all backend tests | `cd backend && pytest -v` |
| Run one test file | `cd backend && pytest tests/test_clientes.py -v` |
| Run tests by name | `cd backend && pytest -v -k "duplicate_cnpj"` |
| Run frontend dev | `cd frontend && npm run dev` |
| Build frontend | `cd frontend && npm run build` |
| Preview build | `cd frontend && npm run preview` |
| Create new migration | `cd backend && python -m alembic revision --autogenerate -m "description"` |
| Apply migrations | `cd backend && python -m alembic upgrade head` (auto-run on app startup) |
| Check migration status | `cd backend && python -m alembic current` |
| Reset dev DB | delete `storage/freelaboard.db` (recreated via migration on next start) |
| Stop Docker | `docker compose down` (uploads + SQLite live in `./storage`) |

There is **no lint, formatter, or typecheck config** in this repo (no ruff/black/eslint/prettier/mypy). Do not invent one without asking.

## Architecture

**Monorepo**: `backend/` (Python FastAPI), `frontend/` (React Vite), `storage/` (SQLite + uploads), `openspec/` (spec-driven change workflow).

**Backend** — Clean Architecture, sync SQLAlchemy 2.0:
- `app/api/v1/` — Controllers (`*_controller.py`) + `api.py` aggregator. Routes share `prefix="/api/v1"` and an `X-API-Key` dependency.
- `app/application/services/` — Business logic; each entity has a Service class instantiated via `Depends()` in its controller.
- `app/domain/` — `models.py` (SQLAlchemy), `schemas.py` (Pydantic v2), `enums.py`.
- `app/infrastructure/repositories/` — Data access; extends `BaseRepository[T]` (`backend/app/infrastructure/repositories/base_repository.py:1`) which provides `create/get_by_id/list_all/update/delete`. Add new entities by adding a model, schema, repository, service, and controller in that order.
- `app/core/` — `config.py` (pydantic-settings, reads `.env`), `database.py` (engine + `get_db` dep), `dependencies.py` (`get_api_key` header dep), `security.py` (CNPJ + API key helpers).

**Frontend** — React 18 + Vite 5 + Tailwind 3:
- `src/App.jsx:1` — Router (Dashboard / Clientes / Projetos / Kanban / Tarefas/:id / Relatorios).
- `src/components/<Feature>/` — One folder per feature (Clientes, Projetos, Kanban, Tarefas, Apontamentos, Relatorios, Dashboard, Layout, Common).
- `src/services/api.js:1` — Axios instance with hardcoded `X-API-Key` + per-entity helpers (`clientesAPI`, `projetosAPI`, `tarefasAPI`, `apontamentosAPI`, `uploadAPI`, `relatoriosAPI`, `dashboardAPI`).
- `src/hooks/usePersistedState.js:1` — `useState` wrapper that mirrors to `localStorage`. Use for filter state (Kanban uses it for `kanban.selectedCliente` / `kanban.selectedProjeto`).
- `src/utils/date.js:1` — `formatDateBR(iso)` (formata `YYYY-MM-DD` → `dd/MM/yyyy` sem conversão de fuso) e `getTodayLocalISO()` (data de hoje no fuso local). Regra: datas vindas do backend **sempre** passam por esses helpers; nunca `new Date(iso).toLocaleDateString(...)` (a spec ECMAScript trata `YYYY-MM-DD` como UTC e gera drift de D-1 em fusos a oeste do UTC) e nunca `new Date().toISOString().split('T')[0]` para defaults de form (avança um dia após 21h BRT).
- Vite dev server (`:5173`) proxies `/api` → `http://localhost:8000`. In Docker, nginx proxies `/api/` → `http://backend:8000/api/`.

## Auth

All backend endpoints require `X-API-Key` header. Default: `freela-secret-key-2024` (defined in `backend/app/core/config.py:6`). Override via `API_KEY` env var. CORS is wide-open (`allow_origins=["*"]` in `app/main.py:24`) — fine for single-user local use, lock down before exposing publicly.

## Database

- SQLite at `storage/freelaboard.db` (default `DATABASE_URL=sqlite:///../storage/freelaboard.db`).
- Tables are created and managed via Alembic migrations, auto-applied on app startup (`alembic upgrade head` in the FastAPI lifespan at `app/main.py:13`). Schema changes must go through `alembic revision --autogenerate`.
- Test DB: `backend/test_freelaboard.db`. The `setup_database` autouse fixture in `backend/tests/conftest.py:30` drops and recreates all tables per test, so file persists but is empty.

## File uploads

Stored at `storage/{cliente_id}/{projeto_id}/{tarefa_id}/` with UUID filenames (extension preserved). Managed via `/api/v1/upload/{tarefa_id}`. `STORAGE_PATH` env var (`backend/app/core/config.py:7`) controls the root; in Docker compose it's set to `/storage` and bind-mounted to the host `./storage`.

## Key entities

- **Cliente** — `documento` must be 14 digits (CNPJ); schema validator strips non-digits, rejects all-equal digits. Duplicate documento → 409 (`cliente_service.py:14`).
- **Projeto** — `valor_por_hora` lives on the project, not the client.
- **Tarefa** — `status` enum: `nova` / `em_andamento` / `pronta` / `fechada` (`app/domain/enums.py:1`). `anexos` is a JSON list of UUID filenames.
- **Apontamento** — `hora_ini`/`hora_fim` are `HH:MM` strings. `total_horas` is computed server-side in `apontamento_service.py:19`; client must not send it. `hora_fim <= hora_ini` is rejected.
- **Relatorio** — Generated on-the-fly, not stored. Endpoint: `GET /api/v1/relatorios?cliente_id=...&mes=MM&ano=YYYY`.

## Testing

- Tests live in `backend/tests/`. Conftest (`backend/tests/conftest.py`) provides: `client` (TestClient), `headers` (`X-API-Key`), `sample_cliente_data` / `created_cliente`, `sample_projeto_data` / `created_projeto`, `sample_tarefa_data` / `created_tarefa`, `sample_apontamento_data` / `created_apontamento`. Chain these in new tests instead of re-posting fixtures.
- New entity → mirror this pattern: fixture in conftest, tests in `test_<entity>.py`.
- No frontend tests.

## OpenSpec workflow

This project uses the [OpenSpec](https://github.com/Fission-AI/OpenSpec) spec-driven workflow. Active and archived changes live in `openspec/changes/`. Use the `openspec-propose`, `openspec-explore`, `openspec-apply-change`, and `openspec-archive-change` skills (under `.opencode/skills/`) for structured changes; don't manually edit specs under `openspec/specs/`.
