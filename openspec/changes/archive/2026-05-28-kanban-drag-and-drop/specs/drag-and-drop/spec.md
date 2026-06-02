## ADDED Requirements

### Requirement: Drag task card between status columns

The system SHALL allow users to pick up a task card from one Kanban column and drop it into another column, changing the task's status and persisting the change to the database.

#### Scenario: Successful drag from Nova to Em Andamento

- **WHEN** user drags a task card from the "Nova" column and drops it onto the "Em Andamento" column
- **THEN** the card moves visually to the "Em Andamento" column immediately
- **THEN** the system calls `PUT /api/v1/tarefas/{id}` with `{"status": "em_andamento"}`
- **THEN** the task's status is updated to `em_andamento` in the database
- **THEN** the card count badge on both columns is updated

#### Scenario: Successful drag from Em Andamento to Pronta

- **WHEN** user drags a task card from "Em Andamento" column and drops it onto "Pronta" column
- **THEN** the card moves visually to the "Pronta" column immediately
- **THEN** the system calls `PUT /api/v1/tarefas/{id}` with `{"status": "pronta"}`
- **THEN** the task's status is updated to `pronta` in the database

#### Scenario: Successful drag from Pronta to Fechada

- **WHEN** user drags a task card from "Pronta" column and drops it onto "Fechada" column
- **THEN** the card moves visually to the "Fechada" column immediately
- **THEN** the system calls `PUT /api/v1/tarefas/{id}` with `{"status": "fechada"}`
- **THEN** the task's status is updated to `fechada` in the database

#### Scenario: API failure during drag-and-drop

- **WHEN** user drags a task card to a different column
- **AND** the API call to update the status fails (network error, 5xx, etc.)
- **THEN** the card returns to its original column visually
- **THEN** the user sees an error message
- **THEN** the task's status in the database remains unchanged

#### Scenario: Drag to the same column (no change)

- **WHEN** user drags a task card and drops it back into the same column it came from
- **THEN** the card stays in that column
- **THEN** no API call is made
- **THEN** the task's status is NOT modified

### Requirement: Task card remains clickable for navigation

The system SHALL preserve the existing click-to-navigate behavior on task cards so that users can still click a card to view its details.

#### Scenario: Clicking a card navigates to detail page

- **WHEN** user clicks (without dragging) a task card on the Kanban board
- **THEN** the browser navigates to `/tarefas/{id}`
- **THEN** the card is not moved between columns

#### Scenario: Click after drag is not interpreted as navigation

- **WHEN** user drags a card and releases it (without clicking)
- **THEN** the click-to-navigate behavior is not triggered
- **THEN** the drag destination determines the card's new position

### Requirement: Visual feedback during drag

The system SHALL provide visual cues during the drag operation to indicate what is happening.

#### Scenario: Card appears lifted while dragging

- **WHEN** user starts dragging a task card
- **THEN** the card appears elevated / with a shadow effect
- **THEN** the original column slot shows a placeholder indicating the card's original position

#### Scenario: Drop target column highlights on hover

- **WHEN** user drags a card over a droppable column
- **THEN** that column's background changes to indicate it is a valid drop target
- **THEN** when the card leaves the column area, the highlight is removed

### Requirement: Drag disabled while tasks are loading

The system SHALL disable drag interactions while the Kanban board is in a loading state to prevent race conditions.

#### Scenario: No drag during loading

- **WHEN** the Kanban board is fetching tasks (loading state is true)
- **THEN** all cards are not draggable
- **THEN** all columns are not droppable
