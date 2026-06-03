## Why

The "Melhores Projetos" board on the Dashboard renders project names as blank because the frontend reads `p.titulo` but the backend returns the project name under the key `projeto_titulo`. This field name mismatch causes the project name column to appear empty, leaving only the rank position and total hours visible.

## What Changes

- Fix the field name accessed in the `Dashboard.jsx` component when rendering the "Melhores Projetos" section
- Change `p.titulo` to `p.projeto_titulo` in the map iteration, aligning it with the backend's response schema

## Capabilities

### New Capabilities

*(none – this is a bug fix, not a new feature)*

### Modified Capabilities

*(none – no spec-level requirement changes)*

## Impact

- **Frontend**: One line change in `Dashboard.jsx` to read the correct property name
- **No API changes**: Backend response is already correct
- **No schema changes**: `MelhorProjeto` Pydantic schema field `projeto_titulo` is already the correct name
