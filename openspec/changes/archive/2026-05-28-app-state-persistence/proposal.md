## Why

Every view in the app loses its filter/selections when the user navigates away and back. The Kanban resets client and project, the Projetos list loses its filter, and Relatorios defaults to the current month — forcing the user to re-select everything. This creates friction in every multi-step workflow. Adding a generic `localStorage`-backed hook solves this for all views at once, making navigation feel seamless.

## What Changes

- Create a reusable `usePersistedState` hook (same API as `useState`, but persists to `localStorage`)
- Replace `useState` calls with `usePersistedState` in Kanban (client/project selection)
- Replace `useState` calls with `usePersistedState` in ProjetosList (filter cliente)
- Replace `useState` calls with `usePersistedState` in ClientesList (search text)
- Replace `useState` calls with `usePersistedState` in RelatorioView (cliente, mês, ano)
- Ensure saved state is scoped per-route to avoid key collisions

## Capabilities

### New Capabilities
- `persisted-state-hook`: A drop-in replacement for `useState` that automatically persists and restores state via `localStorage`, keyed by a unique storage key per field.

### Modified Capabilities

*(None — no existing spec-level requirements are changing.)*

## Impact

- **Frontend**: Create `src/hooks/usePersistedState.js`, modify `Kanban.jsx`, `ProjetosList.jsx`, `ClientesList.jsx`, `RelatorioView.jsx`
- **Dependencies**: None — `localStorage` is native to the browser
- **Backend**: No changes
- **Tests**: No backend tests needed; behavior is visual/storage-based
