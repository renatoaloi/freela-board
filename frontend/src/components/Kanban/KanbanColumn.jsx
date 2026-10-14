import React from 'react';
import { Droppable } from '@hello-pangea/dnd';
import KanbanCard from './KanbanCard';

const columnStyles = {
  nova: {
    header: 'border-blue-500/30 bg-blue-500/10',
    dot: 'bg-blue-400',
    label: 'text-blue-400',
  },
  em_andamento: {
    header: 'border-yellow-500/30 bg-yellow-500/10',
    dot: 'bg-yellow-400',
    label: 'text-yellow-400',
  },
  pronta: {
    header: 'border-accent-green/30 bg-accent-green/10',
    dot: 'bg-accent-green',
    label: 'text-accent-green',
  },
  fechada: {
    header: 'border-gray-500/30 bg-gray-500/10',
    dot: 'bg-gray-400',
    label: 'text-gray-400',
  },
};

const statusLabels = {
  nova: 'Nova',
  em_andamento: 'Em Andamento',
  pronta: 'Pronta',
  fechada: 'Fechada',
};

export default function KanbanColumn({ status, tarefas, loading, onMover }) {
  const style = columnStyles[status] || columnStyles.nova;

  return (
    <div className="glass-card rounded-xl border border-primary-700/50 flex flex-col h-full">
      <div className={`px-4 py-3 border-b ${style.header} rounded-t-xl flex items-center justify-between`}>
        <div className="flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${style.dot}`} />
          <h3 className={`text-sm font-semibold ${style.label}`}>{statusLabels[status] || status}</h3>
        </div>
        <span className={`text-xs font-mono font-medium ${style.label}`}>{tarefas.length}</span>
      </div>

      <Droppable droppableId={status} isDropDisabled={loading}>
        {(provided, snapshot) => (
          <div
            ref={provided.innerRef}
            {...provided.droppableProps}
            className={`flex-1 p-3 space-y-3 overflow-y-auto min-h-[200px] max-h-[calc(100vh-320px)] transition-colors duration-200 ${
              snapshot.isDraggingOver ? 'bg-accent-cyan/5 border border-dashed border-accent-cyan/30 rounded-lg' : ''
            }`}
          >
            {tarefas.length === 0 && !snapshot.isDraggingOver ? (
              <div className="text-center py-8">
                <p className="text-xs text-gray-600">Nenhuma tarefa</p>
              </div>
            ) : tarefas.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-xs text-accent-cyan/60">Solte aqui</p>
              </div>
            ) : (
              tarefas.map((tarefa, index) => <KanbanCard key={tarefa.id} tarefa={tarefa} index={index} onMover={onMover} />)
            )}
            {provided.placeholder}
          </div>
        )}
      </Droppable>
    </div>
  );
}
