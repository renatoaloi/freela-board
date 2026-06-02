## Why

The "Últimos Projetos" cards on the Dashboard and the "eye" button on ProjetosList both navigate to `/kanban` without passing which project was selected. Since Kanban now persists its state in localStorage, it always opens the last viewed project instead of the one the user clicked. The navigation is effectively broken — clicking a different project always shows the same board.

## What Changes

- Make `Dashboard.jsx` pass the project ID (and its client ID) when navigating to Kanban via URL query params
- Make `ProjetosList.jsx` pass the project ID (and its client ID) when clicking the "eye" button
- Make `Kanban.jsx` read `?projeto=X&cliente=Y` from the URL on mount; if present, override persisted state and save the new selection

## Capabilities

### New Capabilities
- `kanban-url-selection`: The Kanban view accepts `projeto` and `cliente` query parameters in the URL to pre-select a project on navigation, overriding any previously persisted selection.

### Modified Capabilities
- `persisted-state-hook`: No requirement changes — the hook itself stays the same. The Kanban component's behavior around initialization changes (check URL params before falling back to localStorage).

## Impact

- **Frontend**: Modify `Kanban.jsx` (read URL params), `Dashboard.jsx` (pass params), `ProjetosList.jsx` (pass params)
- **Dependencies**: None — `useSearchParams` from `react-router-dom` is already available
- **Backend**: No changes
