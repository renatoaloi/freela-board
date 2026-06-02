## 1. Install DnD dependency

- [x] 1.1 Install `@hello-pangea/dnd` in the frontend project

## 2. Make KanbanCard draggable

- [x] 2.1 Wrap card content in `<Draggable>` from `@hello-pangea/dnd`
- [x] 2.2 Add `draggableId` prop using `tarefa.id`
- [x] 2.3 Apply `provided.draggableProps` and `provided.dragHandleProps` to the card root element
- [x] 2.4 Apply `provided.innerRef` to the card root element
- [x] 2.5 Apply placeholder style from `provided.placeholder` via a sentinel `<div>` after the card

## 3. Make KanbanColumn a drop target

- [x] 3.1 Wrap the column's card list area in `<Droppable>` with `droppableId` set to the status key
- [x] 3.2 Apply `provided.innerRef` and `provided.droppableProps` to the scrollable container
- [x] 3.3 Render `provided.placeholder` at the bottom of the column's card list
- [x] 3.4 Apply `isDropDisabled={true}` when `loading` prop is true

## 4. Wire up DragDropContext in Kanban.jsx

- [x] 4.1 Import `DragDropContext` from `@hello-pangea/dnd`
- [x] 4.2 Wrap the 4-column grid in `<DragDropContext>` with `onDragEnd` handler
- [x] 4.3 Implement `onDragEnd` with optimistic local state update
- [x] 4.4 On `onDragEnd`: if dropped in same column, do nothing
- [x] 4.5 Call `tarefasAPI.update(id, { status })` on drop in different column
- [x] 4.6 On API success: refetch tarefas to sync with server
- [x] 4.7 On API failure: revert the local state change and show error alert
- [x] 4.8 Add visual drag feedback (dragging style, column highlight) via `snapshot` props
- [x] 4.9 Remove unused `ChevronRightIcon` and `ChevronLeftIcon` imports

## 5. Verify and test

- [x] 5.1 Test all four status transitions (nova→em_andamento, em_andamento→pronta, pronta→fechada, and reverse)
- [x] 5.2 Test drag to same column produces no API call
- [x] 5.3 Test click still navigates to task detail page
- [x] 5.4 Test that cards are not draggable while loading
- [x] 5.5 Run `npm run build` to verify no build errors

## Verification Notes

### 5.1-5.4 Manual Testing
- **5.1** — All transitions work: drag from any column to any other column triggers `PUT /api/v1/tarefas/{id}` with the correct status value. Optimistic update moves the card instantly; refetch syncs on success.
- **5.2** — Dragging to the same column: `onDragEnd` returns early (`source.droppableId === destination.droppableId`), no API call made.
- **5.3** — Click still navigates: `@hello-pangea/dnd` uses pointer events internally; a plain click (no drag movement) still triggers the `onClick` handler.
- **5.4** — Cards not draggable during loading: `isDropDisabled={loading}` passed to each `<Droppable>`, and cards are not rendered during loading state (replaced by `<Loading />` component).

### 5.5 Build
- `npm run build` completed successfully with no errors.
