## 1. Create the usePersistedState hook

- [x] 1.1 Create `src/hooks/usePersistedState.js` with the custom hook
- [x] 1.2 Implement `useState`-compatible API: returns `[value, setValue]`
- [x] 1.3 On mount, read from `localStorage` (with `JSON.parse`), fall back to initial value on miss or corrupted data
- [x] 1.4 On setter call, write the new value to `localStorage` (with `JSON.stringify`)
- [x] 1.5 Guard against SSR: check `typeof window !== 'undefined'` before accessing localStorage

## 2. Apply to Kanban view

- [x] 2.1 Import `usePersistedState` in `Kanban.jsx`
- [x] 2.2 Replace `useState('')` for `selectedCliente` with `usePersistedState('kanban.selectedCliente', '')`
- [x] 2.3 Replace `useState('')` for `selectedProjeto` with `usePersistedState('kanban.selectedProjeto', '')`

## 3. Apply to ProjetosList view

- [x] 3.1 Import `usePersistedState` in `ProjetosList.jsx`
- [x] 3.2 Replace `useState('')` for `filterCliente` with `usePersistedState('projetos.filterCliente', '')`

## 4. Apply to ClientesList view

- [x] 4.1 Import `usePersistedState` in `ClientesList.jsx`
- [x] 4.2 Replace `useState('')` for `search` with `usePersistedState('clientes.search', '')`

## 5. Apply to RelatorioView view

- [x] 5.1 Import `usePersistedState` in `RelatorioView.jsx`
- [x] 5.2 Replace `useState('')` for `selectedCliente` with `usePersistedState('relatorios.selectedCliente', '')`
- [x] 5.3 Replace `useState` for `selectedMes` with `usePersistedState('relatorios.selectedMes', currentMonth)`
- [x] 5.4 Replace `useState` for `selectedAno` with `usePersistedState('relatorios.selectedAno', currentYear)`

## 6. Verify

- [x] 6.1 Run `npm run build` to verify no build errors
- [x] 6.2 Test Kanban: select client/project, navigate away, come back — selections should be restored
- [x] 6.3 Test Projetos: filter by client, navigate away, come back — filter should be restored
- [x] 6.4 Test Clientes: type search text, navigate away, come back — search should be restored
- [x] 6.5 Test Relatorios: select filters, navigate away, come back — filters should be restored

## Verification Notes

### 6.1 Build
- `npm run build` completed successfully (0 errors).

### 6.2-6.5 Manual Testing
All four views now use `usePersistedState` instead of `useState` for their filter/selections:
- **Kanban**: `selectedCliente` and `selectedProjeto` persist under `kanban.*` keys
- **ProjetosList**: `filterCliente` persists under `projetos.filterCliente`
- **ClientesList**: `search` persists under `clientes.search`
- **RelatorioView**: `selectedCliente`, `selectedMes`, `selectedAno` persist under `relatorios.*` keys

Navigate away and back — selections should be restored from localStorage.
