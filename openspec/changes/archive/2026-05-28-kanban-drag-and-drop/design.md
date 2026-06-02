## Context

The Kanban board renders tasks in four status columns (`nova`, `em_andamento`, `pronta`, `fechada`) using a CSS grid layout. Cards are simple `<div>` elements with an `onClick` handler that navigates to the task detail page. The `Kanban.jsx` component already defines a `handleStatusChange(tarefaId, newStatus)` function that calls `tarefasAPI.update(id, { status })`, but it is never invoked — there is no UI to trigger it.

The codebase has no drag-and-drop library installed. The existing API (`PUT /api/v1/tarefas/{id}`) accepts a partial update body and supports changing the `status` field. No backend changes are needed.

Constraints:
- React 18, Tailwind CSS, dark theme
- All styling uses Tailwind utility classes (no CSS modules)
- The project follows a feature-based component structure

## Goals / Non-Goals

**Goals:**
- Allow users to drag a task card from one status column and drop it into another
- Update the task status in the database via the existing PUT endpoint
- Move the card visually in the UI immediately (optimistic update) with rollback on failure
- Keep existing card click behavior (navigate to detail page) — clicks must not interfere with drag
- Minimal bundle size impact — use a lightweight, maintained DnD library

**Non-Goals:**
- Reordering cards within a column (not requested)
- Drag-and-drop for anything other than task cards
- Backend changes (status updates already work via PUT)
- Touch/mobile drag support (defer to future if needed)

## Decisions

1. **`@hello-pangea/dnd` over other DnD libraries** — This is the actively maintained fork of `react-beautiful-dnd` (which is deprecated). It provides a simple, declarative API (`DragDropContext`, `Droppable`, `Draggable`) that maps cleanly to the Kanban's column/card structure. Alternatives considered: `dnd-kit` (more flexible but heavier API for this use case), native HTML5 Drag and Drop (too low-level, cross-browser quirks). `@hello-pangea/dnd` is the lightest well-maintained option for this exact use case.

2. **Optimistic update with refetch** — On `onDragEnd`, immediately update local state to show the card in its new column, then call `PUT /api/v1/tarefas/{id}`. On success, refetch all tasks to sync with server. On failure, revert the local change and show an error toast. This gives instant visual feedback while keeping data consistent.

3. **No separate backend endpoint** — The existing `PUT /api/v1/tarefas/{id}` already handles partial updates including `status`. Creating a dedicated PATCH endpoint for status-only changes would add unnecessary surface area.

4. **`onClick` remains on card** — `@hello-pangea/dnd` allows both drag and click on the same element without conflict (it uses pointer events internally). No need to change navigation behavior.

5. **Column-level drop target, not individual card slots** — Each `KanbanColumn` is a single `Droppable` area. Cards are `Draggable` items. This keeps the implementation simple and matches the current column structure.

## Risks / Trade-offs

- **[Library maintenance]** `@hello-pangea/dnd` is community-maintained. If it falls behind, we may need to migrate to `dnd-kit` later → Mitigation: The DnD logic is isolated to three components (`Kanban`, `KanbanColumn`, `KanbanCard`), making migration straightforward.
- **[Drag vs click interference]** Users might accidentally drag when intending to click → Mitigation: `@hello-pangea/dnd` handles this with a small drag distance threshold; casual clicks are not interpreted as drags.
- **[Performance with many cards]** If a column has 50+ cards, re-renders on drag could be slow → Mitigation: Add `React.memo` to `KanbanCard` if needed; `@hello-pangea/dnd` supports `shouldComponentUpdate` optimization.
