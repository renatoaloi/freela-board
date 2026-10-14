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
printf 'VITE_API_BASE_URL=/api/v1\nVITE_API_KEY=freela-secret-key-2024\n' > .env
npm run dev

# Docker (alternative — frontend on :8080, backend on :8000, healthcheck-gated)
docker compose up --build
```

`frontend/.env` is **required and not in the repo** (gitignored). `src/services/api.js:4` builds axios from `import.meta.env.VITE_API_BASE_URL` / `VITE_API_KEY`; unset, the key is missing (→ 422) and requests bypass the `/api` proxy (→ HTML instead of JSON). Docker gets the same two vars as build args from `docker-compose.yml`.

All backend commands must run **from `backend/`**: `DATABASE_URL` (`sqlite:///../storage/freelaboard.db`), `STORAGE_PATH` (`../storage`) and the test DB (`sqlite:///./test_freelaboard.db`) are relative paths resolved against the CWD.

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
- Non-obvious route homes: `/dashboard`, `/relatorios` and `/relatorios/pdf` all live in `relatorio_controller.py` (there is no dashboard controller file); `dados-bancarios` is a singleton GET+PUT pair (no list/create/delete).
- `app/application/services/` — Business logic; each entity has a Service class instantiated via `Depends()` in its controller.
- `app/domain/` — `models.py` (SQLAlchemy), `schemas.py` (Pydantic v2), `enums.py`.
- `app/infrastructure/repositories/` — Data access; extends `BaseRepository[T]` (`backend/app/infrastructure/repositories/base_repository.py:1`) which provides `create/get_by_id/list_all/update/delete`. Add new entities by adding a model, schema, repository, service, and controller in that order, then register the router in `api/v1/api.py`.
- `app/core/` — `config.py` (pydantic-settings, reads `.env`), `database.py` (engine + `get_db` dep), `dependencies.py` (`get_api_key` header dep), `security.py` (CNPJ + API key helpers).

**Frontend** — React 18 + Vite 5 + Tailwind 3:
- `src/App.jsx:1` — Router (Dashboard / Clientes / Projetos / Kanban / Tarefas/:id / Relatorios / Configuracoes).
- `src/components/<Feature>/` — One folder per feature (Clientes, Projetos, Kanban, Tarefas, Apontamentos, Relatorios, Dashboard, Configuracoes, Layout, Common). Shared pieces (`Modal`, `ConfirmModal`, `AlertModal`, `FileUpload`, `MarkdownEditor`, `FilePreviewModal`, `Loading`) go in `Common/` — this codebase uses those modals instead of `window.confirm` / `alert`.
- `src/services/api.js:1` — Axios instance (baseURL + `X-API-Key` from Vite env; see Quick start) + per-entity helpers (`clientesAPI`, `projetosAPI`, `tarefasAPI`, `apontamentosAPI`, `uploadAPI`, `relatoriosAPI`, `dadosBancariosAPI`, `dashboardAPI`). Add new endpoints here, not with inline `fetch`.
- `src/hooks/usePersistedState.js:1` — `useState` wrapper that mirrors to `localStorage`. Use for filter state (Kanban uses it for `kanban.selectedCliente` / `kanban.selectedProjeto`).
- `src/utils/date.js:1` — `formatDateBR(iso)` (formata `YYYY-MM-DD` → `dd/MM/yyyy` sem conversão de fuso) e `getTodayLocalISO()` (data de hoje no fuso local). Regra: datas vindas do backend **sempre** passam por esses helpers; nunca `new Date(iso).toLocaleDateString(...)` (a spec ECMAScript trata `YYYY-MM-DD` como UTC e gera drift de D-1 em fusos a oeste do UTC) e nunca `new Date().toISOString().split('T')[0]` para defaults de form (avança um dia após 21h BRT).
- Vite dev server (`:5173`) proxies `/api` → `http://localhost:8000`. In Docker, nginx proxies `/api/` → `http://backend:8000/api/`.
- User-facing text (labels, empty states, reports) is pt-BR; keep new copy in Portuguese even though code/identifiers are English.

## Auth

All backend endpoints require `X-API-Key` header. Default: `freela-secret-key-2024` (defined in `backend/app/core/config.py:6`). Override via `API_KEY` env var. CORS is wide-open (`allow_origins=["*"]` in `app/main.py:24`) — fine for single-user local use, lock down before exposing publicly.

## Database

- SQLite at `storage/freelaboard.db` (default `DATABASE_URL=sqlite:///../storage/freelaboard.db`).
- Tables are created and managed via Alembic migrations, auto-applied on app startup (`alembic upgrade head` in the FastAPI lifespan at `app/main.py:13`). Schema changes must go through `alembic revision --autogenerate`.
- `alembic/env.py` overrides the URL in `alembic.ini` with `settings.DATABASE_URL` (editing `sqlalchemy.url` in the ini has no effect) and runs with `render_as_batch=True` — required for SQLite column changes.
- Test DB: `backend/test_freelaboard.db`. The `setup_database` autouse fixture in `backend/tests/conftest.py:30` drops and recreates all tables per test, so file persists but is empty.

## File uploads

Stored at `storage/{cliente_id}/{projeto_id}/{tarefa_id}/` with UUID filenames (extension preserved). Managed via `/api/v1/upload/{tarefa_id}`. `STORAGE_PATH` env var (`backend/app/core/config.py:7`) controls the root; in Docker compose it's set to `/storage` and bind-mounted to the host `./storage`.

## Key entities

- **Cliente** — `documento` must be 14 digits (CNPJ); schema validator strips non-digits, rejects all-equal digits. Duplicate documento → 409 (`cliente_service.py:14`).
- **Projeto** — `valor_por_hora` lives on the project, not the client.
- **Tarefa** — `status` enum: `nova` / `em_andamento` / `pronta` / `fechada` (`app/domain/enums.py:1`). `anexos` is a JSON list of UUID filenames.
- **Apontamento** — `hora_ini`/`hora_fim` are `HH:MM` strings validated by regex + a model validator in `schemas.py`. `total_horas` is computed server-side in `apontamento_service.py:19`; client must not send it. `hora_fim <= hora_ini` is rejected. `data` defaults to today server-side when omitted.
- **Relatorio** — Generated on-the-fly, not stored. Endpoints: `GET /api/v1/relatorios?cliente_id=...&mes=MM&ano=YYYY` (JSON) and `GET /api/v1/relatorios/pdf?...` (WeasyPrint render of `app/templates/relatorio_pdf.html`).
- **DadosBancarios** — Single row (self's bank/PIX data, shown on Configuracoes and injected into relatórios). `GET`/`PUT /api/v1/dados-bancarios`, no id in the path.

## Testing

- Tests live in `backend/tests/`. Conftest (`backend/tests/conftest.py`) provides: `client` (TestClient), `headers` (`X-API-Key`), `sample_cliente_data` / `created_cliente`, `sample_projeto_data` / `created_projeto`, `sample_tarefa_data` / `created_tarefa`, `sample_apontamento_data` / `created_apontamento`. Chain these in new tests instead of re-posting fixtures.
- Conftest also has `created_dados_bancarios`; `sample_*` fixtures already include the `cep` field required by Cliente.
- New entity → mirror this pattern: fixture in conftest, tests in `test_<entity>.py`.
- A green run is **50 passed, 3 skipped**: the three `/relatorios/pdf` tests are behind a `HAS_WEASYPRINT` guard (`tests/test_relatorios.py:151`) and skip when WeasyPrint isn't importable — it needs GTK/cairo, which the local Windows venv lacks. They do run in the backend Docker image (its Dockerfile installs the cairo/pango libs).
- WeasyPrint is imported lazily inside `RelatorioPdfService.generate` (`relatorio_pdf_service.py:118`), so the app boots fine without it; only the PDF endpoint breaks.
- Tests that touch uploads monkeypatch `settings.STORAGE_PATH` to a pytest `tmp_path` (`tests/test_upload.py:9`) — do the same instead of writing into `../storage`.
- No frontend tests.

## OpenSpec workflow

This project uses the [OpenSpec](https://github.com/Fission-AI/OpenSpec) spec-driven workflow. Active and archived changes live in `openspec/changes/`. Use the `openspec-propose`, `openspec-explore`, `openspec-apply-change`, and `openspec-archive-change` skills (under `.opencode/skills/`) for structured changes; don't manually edit specs under `openspec/specs/`.
