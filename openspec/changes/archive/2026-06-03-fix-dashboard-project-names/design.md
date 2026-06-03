## Context

The "Melhores Projetos" section on the Dashboard queries the backend `GET /api/v1/dashboard` endpoint, which returns an array of top projects. Each object in the `melhores_projetos` array includes the project name under the key `projeto_titulo` (as defined by the `MelhorProjeto` Pydantic schema and the repository query). The frontend component `Dashboard.jsx` mistakenly accesses `p.titulo` instead of `p.projeto_titulo` when rendering the project name.

Other sections of the same dashboard (e.g., "Últimos Projetos") use `p.titulo` correctly because their backend response key is `titulo`.

## Goals / Non-Goals

**Goals:**
- Display project names correctly in the "Melhores Projetos" dashboard card
- Touch only the minimum surface area to fix the bug

**Non-Goals:**
- Renaming backend response keys or Pydantic schemas (would be a breaking change)
- Refactoring the dashboard component beyond the fix
- Adding new fields or features to the dashboard

## Decisions

- **Fix frontend, not backend**: The backend response key `projeto_titulo` is consistent with the `MelhorProjeto` schema (`schemas.py:275`) and the repository (`relatorio_repository.py:189`). Changing the frontend to match the existing API is the minimal, safest approach — no API consumers are affected, no migration needed, no schema change.
- **One-line change**: Only `Dashboard.jsx:176` — replace `{p.titulo}` with `{p.projeto_titulo}`.

## Risks / Trade-offs

- **Fragile coupling**: If a future refactor renames backend keys without updating all consumers, this could break again. Mitigated by the existing schema validation and the fact that only one frontend file accesses this field.
- **Inconsistency between sections**: "Melhores Projetos" uses `projeto_titulo` while "Últimos Projetos" uses `titulo`. This is intentional — they come from different queries. No action needed.
