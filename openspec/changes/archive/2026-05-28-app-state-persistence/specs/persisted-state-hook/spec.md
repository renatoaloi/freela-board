## ADDED Requirements

### Requirement: Hook provides useState-compatible API

The system SHALL provide a `usePersistedState(key, initialValue)` custom hook that has the same API surface as React's `useState` — returns a state value and a setter function.

#### Scenario: Basic usage returns state and setter

- **WHEN** a component calls `usePersistedState('myKey', 'default')`
- **THEN** the return value is a tuple `[value, setValue]` where `setValue` is a function
- **THEN** the initial `value` is `'default'` when no value exists in localStorage

### Requirement: State persists to localStorage

The system SHALL write every state update to `localStorage` under the specified key so that the value survives page navigation and full page reloads.

#### Scenario: Setter persists value immediately

- **WHEN** a component calls `setValue('novo_valor')` from the hook
- **THEN** `localStorage.getItem('myKey')` returns `'"novo_valor"'` (JSON-stringified)
- **THEN** the component re-renders with the new value

#### Scenario: Value restored from localStorage on mount

- **WHEN** `localStorage` contains `'{"selectedCliente":"abc-123"}'` under key `'kanban.selectedCliente'`
- **AND** a component mounts with `usePersistedState('kanban.selectedCliente', '')`
- **THEN** the initial value is `'abc-123'` (restored from storage)

### Requirement: Graceful fallback on corrupted data

The system SHALL fall back to the initial value when the stored data cannot be parsed as valid JSON.

#### Scenario: Corrupted localStorage falls back to initial

- **WHEN** `localStorage` under the hook's key contains invalid JSON (e.g., `'{broken'`)
- **AND** a component mounts with `usePersistedState('myKey', 'fallback')`
- **THEN** the initial value is `'fallback'`
- **THEN** no error is thrown

### Requirement: Storage keys are unique per view

The system SHALL accept an explicit string key so that different views can store different values under the same conceptual field name.

#### Scenario: Different keys for same-field in different views

- **WHEN** Kanban calls `usePersistedState('kanban.selectedCliente', '')`
- **AND** Relatorios calls `usePersistedState('relatorios.selectedCliente', '')`
- **AND** the user sets different values in each view
- **THEN** `localStorage` contains both `kanban.selectedCliente` and `relatorios.selectedCliente` with independent values

### Requirement: Kanban remembers client and project selections

The system SHALL persist `selectedCliente` and `selectedProjeto` in the Kanban view so that navigating away and back restores the previous selections.

#### Scenario: Kanban restores client on return

- **WHEN** user selects a client and project in Kanban
- **AND** navigates to another page
- **AND** returns to `/kanban`
- **THEN** the client dropdown shows the previously selected client
- **THEN** the project dropdown shows the previously selected project
- **THEN** tasks for that project are loaded automatically

### Requirement: ProjetosList remembers filter cliente

The system SHALL persist `filterCliente` in the Projetos list view.

#### Scenario: Projetos filter restores on return

- **WHEN** user selects a client filter in the Projetos list
- **AND** navigates away and back
- **THEN** the client filter dropdown shows the previously selected client
- **THEN** the project list is filtered to that client

### Requirement: ClientesList remembers search text

The system SHALL persist the `search` text in the Clientes list view.

#### Scenario: Clientes search restores on return

- **WHEN** user types a search term in the Clientes list
- **AND** navigates away and back
- **THEN** the search input contains the previously typed text
- **THEN** the client list is filtered to show matching results

### Requirement: RelatorioView remembers cliente, mês, ano

The system SHALL persist `selectedCliente`, `selectedMes`, and `selectedAno` in the Relatorio view.

#### Scenario: Relatorio filters restores on return

- **WHEN** user selects a client, month, and year in Relatorios
- **AND** navigates away and back
- **THEN** all three filter values are restored
- **THEN** the report is generated for the restored filters
