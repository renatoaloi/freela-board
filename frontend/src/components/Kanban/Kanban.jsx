import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import usePersistedState from '../../hooks/usePersistedState';
import { DragDropContext } from '@hello-pangea/dnd';
import { tarefasAPI, clientesAPI, projetosAPI } from '../../services/api';
import Loading from '../Common/Loading';
import TarefaForm from '../Tarefas/TarefaForm';
import KanbanColumn from './KanbanColumn';
import { PlusIcon } from '@heroicons/react/24/outline';

const statusList = ['nova', 'em_andamento', 'pronta', 'fechada'];

export default function Kanban() {
  const [searchParams] = useSearchParams();
  const [clientes, setClientes] = useState([]);
  const [projetos, setProjetos] = useState([]);
  const [tarefas, setTarefas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCliente, setSelectedCliente] = usePersistedState('kanban.selectedCliente', '');
  const [selectedProjeto, setSelectedProjeto] = usePersistedState('kanban.selectedProjeto', '');
  const [formOpen, setFormOpen] = useState(false);
  const [selectedStatus, setSelectedStatus] = useState('nova');

  const tarefasRef = useRef(tarefas);
  tarefasRef.current = tarefas;

  useEffect(() => {
    const projetoParam = searchParams.get('projeto');
    const clienteParam = searchParams.get('cliente');
    if (projetoParam) setSelectedProjeto(projetoParam);
    if (clienteParam) setSelectedCliente(clienteParam);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchClientes = useCallback(async () => {
    try {
      const res = await clientesAPI.list();
      setClientes(res.data || []);
    } catch {}
  }, []);

  const fetchProjetos = useCallback(async () => {
    if (!selectedCliente) {
      setProjetos([]);
      return;
    }
    try {
      const res = await projetosAPI.list(selectedCliente);
      setProjetos(res.data || []);
    } catch {}
  }, [selectedCliente]);

  const fetchTarefas = useCallback(async () => {
    if (!selectedProjeto) {
      setTarefas([]);
      setLoading(false);
      return;
    }
    setLoading(true);
    try {
      const res = await tarefasAPI.list({ projeto_id: selectedProjeto });
      setTarefas(res.data || []);
    } catch {
      setError('Erro ao carregar tarefas.');
    } finally {
      setLoading(false);
    }
  }, [selectedProjeto]);

  useEffect(() => { fetchClientes(); }, [fetchClientes]);
  useEffect(() => { fetchProjetos(); }, [fetchProjetos]);
  useEffect(() => { fetchTarefas(); }, [fetchTarefas]);

  const onDragEnd = async (result) => {
    const { source, destination, draggableId } = result;

    if (!destination) return;
    if (source.droppableId === destination.droppableId) return;

    const previousTarefas = tarefasRef.current;

    const updated = previousTarefas.map((t) => {
      if (t.id === draggableId) {
        return { ...t, status: destination.droppableId };
      }
      return t;
    });

    setTarefas(updated);

    try {
      await tarefasAPI.update(draggableId, { status: destination.droppableId });
      await fetchTarefas();
    } catch {
      setTarefas(previousTarefas);
      alert('Erro ao atualizar status da tarefa.');
    }
  };

  const grouped = {};
  statusList.forEach((s) => { grouped[s] = []; });
  tarefas.forEach((t) => {
    const key = t.status || 'nova';
    if (grouped[key]) grouped[key].push(t);
    else grouped[key] = [t];
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Kanban</h1>
          <p className="text-sm text-gray-400 mt-1">Gerencie suas tarefas visualmente</p>
        </div>
        <button
          onClick={() => { setSelectedStatus('nova'); setFormOpen(true); }}
          disabled={!selectedProjeto}
          className="btn-primary flex items-center gap-2 self-start disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <PlusIcon className="w-5 h-5" />
          Nova Tarefa
        </button>
      </div>

      <div className="flex flex-col sm:flex-row gap-4">
        <div className="w-full sm:w-64">
          <label className="block text-xs font-medium text-gray-400 mb-1.5">Cliente</label>
          <select
            value={selectedCliente}
            onChange={(e) => { setSelectedCliente(e.target.value); setSelectedProjeto(''); }}
            className="input-field"
          >
            <option value="">Selecione um cliente...</option>
            {clientes.map((c) => (
              <option key={c.id} value={c.id}>{c.nome}</option>
            ))}
          </select>
        </div>
        <div className="w-full sm:w-64">
          <label className="block text-xs font-medium text-gray-400 mb-1.5">Projeto</label>
          <select
            value={selectedProjeto}
            onChange={(e) => setSelectedProjeto(e.target.value)}
            className="input-field"
            disabled={!selectedCliente}
          >
            <option value="">Selecione um projeto...</option>
            {projetos.map((p) => (
              <option key={p.id} value={p.id}>{p.titulo}</option>
            ))}
          </select>
        </div>
      </div>

      {error && <div className="text-accent-pink text-sm">{error}</div>}

      {!selectedProjeto ? (
        <div className="text-center py-20">
          <p className="text-gray-500">Selecione um cliente e projeto para visualizar o Kanban.</p>
        </div>
      ) : loading ? (
        <Loading />
      ) : (
        <DragDropContext onDragEnd={onDragEnd}>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {statusList.map((status) => (
              <KanbanColumn
                key={status}
                status={status}
                tarefas={grouped[status] || []}
                loading={loading}
              />
            ))}
          </div>
        </DragDropContext>
      )}

      <TarefaForm
        isOpen={formOpen}
        onClose={() => setFormOpen(false)}
        onSave={() => { setFormOpen(false); fetchTarefas(); }}
        projetoId={selectedProjeto}
        initialStatus={selectedStatus}
      />
    </div>
  );
}
