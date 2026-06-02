## Context

The Kanban view persists `selectedCliente` and `selectedProjeto` via `usePersistedState` (localStorage). Two places navigate to Kanban without passing context: `Dashboard.jsx` (project cards in "Últimos Projetos") and `ProjetosList.jsx` (eye button in the actions column). Both call `navigate('/kanban')` with no route state or query params. When the user clicks a different project, Kanban mounts and restores whichever project was last stored in localStorage — typically the wrong one.

The `react-router-dom` v6 `useSearchParams` hook is already available as a dependency. No new packages needed.

## Goals / Non-Goals

**Goals:**
- Clicking a project card on Dashboard navigates to Kanban with that project pre-selected
- Clicking the eye button on ProjetosList navigates to Kanban with that project pre-selected
- Kanban reads query params `?projeto=X&cliente=Y` on mount and persists them to localStorage
- If no query params are present, Kanban falls back to the previously persisted state

**Non-Goals:**
- Adding query params to every navigation in the app (only Kanban entry points)
- Changing the existing persistence hook behavior
- Making the client/project selections in Kanban affect the URL (URL is for input, not output)

## Decisions

1. **URL query params over React Router state** — `navigate('/kanban', { state })` would only work within the same session and is not bookmarkable. Query params (`/kanban?projeto=X&cliente=Y`) are visible, shareable, and survive page refreshes. Since Kanban is the destination, the params are a natural fit for route-based input.

2. **Params win over persisted state** — On mount, Kanban checks for query params first. If `projeto` is present, it uses that value AND writes it to persisted state (so subsequent navigations without params still work correctly). If absent, it reads from persisted state. This gives the best of both worlds: external navigation works, and manual selections persist.

3. **Both `projeto` and `cliente` in params** — The Dashboard API returns both `p.id` and `p.cliente_id` in the "Últimos Projetos" data. Passing both avoids an extra API call in Kanban to look up the client from the project.

## Risks / Trade-offs

- **[Stale params]** If a user bookmarks a URL with a project ID that's later deleted, they'll see an empty Kanban. → Mitigation: same as the existing behavior — the dropdown will show the ID but no projects will load. User can re-select.
- **[URL clutter]** Query params in the URL are cosmetic. → Mitigation: only present when navigated from Dashboard/ProjetosList; manual selections don't update the URL.
