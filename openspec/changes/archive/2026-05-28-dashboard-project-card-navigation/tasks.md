## 0. Add cliente_id to backend Dashboard API

- [x] 0.1 Add `cliente_id: str` field to `UltimoProjeto` Pydantic schema in `schemas.py`
- [x] 0.2 Add `ProjetoModel.cliente_id` to the query and `"cliente_id": r.cliente_id` to the result dict in `relatorio_repository.py`'s `get_ultimos_projetos`

## 1. Make Kanban read URL query params

- [x] 1.1 Import `useSearchParams` from `react-router-dom` in `Kanban.jsx`
- [x] 1.2 On mount, check for `projeto` and `cliente` URL params
- [x] 1.3 If params present, override persisted state with the param values (write to localStorage)
- [x] 1.4 Trigger data fetch for the project from params (triggers via selectedProjeto dependency chain)
- [x] 1.5 Reset `selectedProjeto` to `''` when changing client (existing behavior, ensure it still works)

## 2. Make Dashboard pass project ID via URL params

- [x] 2.1 Update `navigate('/kanban')` to include query params in Dashboard's "Últimos Projetos" section

## 3. Make ProjetosList pass project ID via URL params

- [x] 3.1 Update `navigate('/kanban')` to include query params in ProjetosList's eye button

## 4. Verify

- [x] 4.1 Run `npm run build` to verify no build errors
- [x] 4.2 Test Dashboard card click: should open Kanban with the clicked project
- [x] 4.3 Test ProjetosList eye button: should open Kanban with that project
- [x] 4.4 Test direct `/kanban` navigation: should restore last selection from localStorage
- [x] 4.5 Test switching to a different project manually in Kanban dropdowns still works

## Verification Notes

### 4.1 Build
- `npm run build` — 0 errors
- `python -m pytest -v` — 32/32 tests passed (backend schema change backward compatible)

### 4.2-4.5 Behavior
- **Dashboard → Kanban**: navigates to `/kanban?projeto={id}&cliente={cliente_id}`; Kanban reads params on mount and overrides persisted state
- **ProjetosList eye → Kanban**: same as above
- **Direct /kanban**: no query params → falls back to localStorage via `usePersistedState`
- **Manual selection**: `usePersistedState` still works; selecting a different client resets projeto as before
