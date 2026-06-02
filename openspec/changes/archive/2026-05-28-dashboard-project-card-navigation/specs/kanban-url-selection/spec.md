## ADDED Requirements

### Requirement: Kanban accepts projeto and cliente via URL query params

The system SHALL allow the Kanban view to receive `projeto` and `cliente` query parameters via the URL. When present, these parameters SHALL override any previously persisted selection on mount.

#### Scenario: Navigate from Dashboard project card

- **WHEN** user clicks a project card in "Últimos Projetos" on the Dashboard
- **THEN** the browser navigates to `/kanban?projeto={id}&cliente={cliente_id}`
- **THEN** Kanban mounts with that project pre-selected
- **THEN** the project dropdown shows the project's name
- **THEN** the client dropdown shows the client's name
- **THEN** the Kanban board loads tasks for that project

#### Scenario: Navigate from ProjetosList eye button

- **WHEN** user clicks the eye button next to a project on the ProjetosList
- **THEN** the browser navigates to `/kanban?projeto={id}&cliente={cliente_id}`
- **THEN** Kanban mounts with that project pre-selected
- **THEN** tasks for that project are loaded automatically

#### Scenario: Direct navigation without params restores persisted state

- **WHEN** user navigates to `/kanban` without query params
- **THEN** Kanban restores the last selected cliente and projeto from localStorage
- **THEN** no params are added to the URL

### Requirement: URL params persist to localStorage

The system SHALL write the values from URL query params to persisted state so that subsequent navigations without params still show the same project.

#### Scenario: First visit via params, second visit without

- **WHEN** user navigates to `/kanban?projeto=X&cliente=Y` (first visit)
- **AND** the Kanban loads tasks for project X
- **AND** user navigates away
- **AND** user returns to `/kanban` (no params)
- **THEN** the Kanban restores project X and client Y from localStorage
