import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Draggable } from '@hello-pangea/dnd';
import { ArrowsRightLeftIcon } from '@heroicons/react/24/outline';

export default function KanbanCard({ tarefa, index, onMover }) {
  const navigate = useNavigate();

  const descricaoPreview = tarefa.descricao
    ? tarefa.descricao.replace(/[#*_>`~\[\]]/g, '').substring(0, 80) + (tarefa.descricao.length > 80 ? '...' : '')
    : 'Sem descrição';

  return (
    <Draggable draggableId={tarefa.id} index={index}>
      {(provided, snapshot) => (
        <div
          ref={provided.innerRef}
          {...provided.draggableProps}
          {...provided.dragHandleProps}
          onClick={() => navigate(`/tarefas/${tarefa.id}`)}
          className={`relative glass-card rounded-lg p-3.5 border border-primary-600/50 cursor-pointer hover:border-accent-cyan/30 hover:bg-primary-800/60 transition-all duration-200 group ${
            snapshot.isDragging ? 'shadow-lg shadow-accent-cyan/20 border-accent-cyan/50 rotate-2 scale-105' : ''
          }`}
        >
          <h4 className="text-sm font-medium text-white group-hover:text-accent-cyan transition-colors leading-tight">
            {tarefa.titulo}
          </h4>
          {onMover && (
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                e.preventDefault();
                onMover(tarefa);
              }}
              className="absolute top-2.5 right-2.5 p-1 rounded-md text-gray-500 hover:text-accent-cyan hover:bg-primary-700/60 opacity-0 group-hover:opacity-100 transition-opacity"
              title="Mover para outro projeto"
            >
              <ArrowsRightLeftIcon className="w-4 h-4" />
            </button>
          )}
          {tarefa.descricao && (
            <p className="text-xs text-gray-500 mt-1.5 line-clamp-2 leading-relaxed">
              {descricaoPreview}
            </p>
          )}
          {tarefa.total_horas > 0 && (
            <div className="flex items-center gap-1 mt-2">
              <span className="text-xs font-mono text-accent-green">{Number(tarefa.total_horas).toFixed(1)}h</span>
            </div>
          )}
        </div>
      )}
    </Draggable>
  );
}
