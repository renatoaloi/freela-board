## Context

The frontend has zero state persistence — every component remounts fresh on navigation. State is managed exclusively via `useState` in each component, with no React Context, URL params, or localStorage usage. Five views are affected: Kanban (cliente/projeto), ProjetosList (filterCliente), ClientesList (search), RelatorioView (cliente/mês/ano). The codebase has no hooks directory yet; hooks live inline in components.

Constraints:
- React 18, no state management library
- Tailwind CSS, dark theme
- No backend changes allowed
- Must be a generic, reusable solution — not a one-off fix per component

## Goals / Non-Goals

**Goals:**
- Create a `usePersistedState(key, initialValue)` hook that mirrors `useState` but persists to `localStorage`
- Apply it to all four views where filter state is currently lost on navigation
- Ensure storage keys are scoped per-route to avoid collisions (e.g., `kanban.selectedCliente` vs `relatorios.selectedCliente`)
- Handle edge cases: corrupted localStorage, SSR safety, storage quota exceeded
- Keep the migration minimal — 1 new file, ~4 modified files with 1-line changes each

**Non-Goals:**
- Persisting every single `useState` in the app (only UI filter/sort state that matters across navigations)
- Persisting form input state (not relevant — forms should start clean)
- Cross-tab synchronization (out of scope)
- URL query param state (future consideration)

## Decisions

1. **Custom hook over Context/Provider** — A hook (`usePersistedState`) is the simplest abstraction: same API as `useState`, zero boilerplate, no Provider wrapper needed. Components that don't need persistence are unaffected. Alternatives: React Context + localStorage would require a Provider tree and more ceremony for the same result. URL query params would be bookmarkable but require routing changes and add URL bloat.

2. **`useSyncExternalStorage` not needed** — The hook only needs to read from localStorage on mount (initial render) and write on every update. Cross-tab sync (via `storage` event) is a non-goal; the hook won't listen for external changes.

3. **Storage key format `viewName.fieldName`** — e.g., `kanban.selectedCliente`, `projetos.filterCliente`. This prevents key collisions when different views store similar data (e.g., `selectedCliente` in both Kanban and Relatorios). Keys are passed explicitly by the consumer.

4. **Error-resilient JSON parsing** — If the stored value can't be parsed (corrupted data, schema migration), the hook silently falls back to the initial value. No error thrown, no user-facing crash.

5. **Same-view navigation preserves state** — Since the state is in localStorage, navigating within the app and back restores it on mount. This is the core benefit.

## Risks / Trade-offs

- **[localStorage quota]** A single project/client ID is ~50 bytes — far below the 5-10MB limit. No risk.
- **[Stale state]** If a client or project is deleted while the user is on another page, the persisted ID will point to nothing. → Mitigation: the dropdown will show the stale value, but selecting it will fail gracefully (API returns empty). Acceptable UX — user just re-selects.
- **[SSR incompatibility]** localStorage is browser-only. → Mitigation: the hook must check `typeof window !== 'undefined'` before accessing localStorage. React 18 + Vite is client-side rendered, so this is theoretical but good practice.
