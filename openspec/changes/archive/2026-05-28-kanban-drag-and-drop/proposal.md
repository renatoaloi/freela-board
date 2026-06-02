## Why

The Kanban board currently has no way to change a task's status directly from the board view. Users must open a task form or navigate to the detail page to update status, breaking the visual workflow that Kanban boards are meant to provide. Adding drag-and-drop will let users move cards between columns, updating the status immediately — making the board truly interactive and saving significant time during daily task management.

## What Changes

- Add a drag-and-drop library (`@hello-pangea/dnd`) to the frontend
- Make `KanbanCard` draggable with drag handles/behavior
- Make `KanbanColumn` a drop target that accepts cards from other columns
- Wire up `onDragEnd` in `Kanban.jsx` to call `PUT /api/v1/tarefas/{id}` with the new status
- Show optimistic UI update (move card immediately) and refetch on success, rollback on failure
- Remove unused `ChevronRightIcon` and `ChevronLeftIcon` imports from `Kanban.jsx`

## Capabilities

### New Capabilities
- `drag-and-drop`: Core drag-and-drop interaction on the Kanban board — cards can be picked up from one status column and dropped into another, triggering a backend update and visual repositioning of the card.

### Modified Capabilities

*(None — no existing spec-level requirements are changing.)*

## Impact

- **Frontend**: `Kanban.jsx`, `KanbanColumn.jsx`, `KanbanCard.jsx` — add drag-and-drop event handlers and state management
- **Dependencies**: Add `@hello-pangea/dnd` (or similar maintained fork of `react-beautiful-dnd`)
- **Backend**: No changes needed — the existing `PUT /api/v1/tarefas/{id}` endpoint already supports status updates
- **Tests**: No backend test changes needed; may add frontend interaction tests if test infrastructure exists
