import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import usePersistedState from '../../hooks/usePersistedState';
import { projetosAPI, clientesAPI } from '../../services/api';
import Loading from '../Common/Loading';
import ProjetoForm from './ProjetoForm';
import { formatDateBR } from '../../utils/date';
import { PlusIcon, PencilSquareIcon, TrashIcon, EyeIcon } from '@heroicons/react/24/outline';

export default function ProjetosList() {
  const [projetos, setProjetos] = useState([]);
  const [clientes, setClientes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterCliente, setFilterCliente] = usePersistedState('projetos.filterCliente', '');
  const [formOpen, setFormOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const navigate = useNavigate();

  const fetchProjetos = useCallback(async () => {
    try {
      const res = await projetosAPI.list(filterCliente || undefined);
      setProjetos(res.data || []);
    } catch {
      setError('Erro ao carregar projetos.');
    } finally {
      setLoading(false);
    }
  }, [filterCliente]);

  const fetchClientes = useCallback(async () => {
    try {
      const res = await clientesAPI.list();
      setClientes(res.data || []);
    } catch {}
  }, []);

  useEffect(() => {
    fetchClientes();
  }, [fetchClientes]);

  useEffect(() => {
    setLoading(true);
    fetchProjetos();
  }, [fetchProjetos]);

  const handleDelete = async (id) => {
    if (!confirm('Excluir este projeto? Todas as tarefas associadas serão removidas.')) return;
    try {
      await projetosAPI.delete(id);
      await fetchProjetos();
    } catch {
      alert('Erro ao excluir projeto.');
    }
  };

  const getClienteNome = (clienteId) => {
    const c = clientes.find((cl) => cl.id === clienteId);
    return c ? c.nome : '—';
  };

  if (loading && projetos.length === 0) return <Loading />;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Projetos</h1>
          <p className="text-sm text-gray-400 mt-1">Gerencie seus projetos</p>
        </div>
        <button onClick={() => { setEditing(null); setFormOpen(true); }} className="btn-primary flex items-center gap-2 self-start">
          <PlusIcon className="w-5 h-5" />
          Novo Projeto
        </button>
      </div>

      <div className="flex flex-col sm:flex-row gap-4">
        <div className="w-full sm:w-64">
          <select
            value={filterCliente}
            onChange={(e) => setFilterCliente(e.target.value)}
            className="input-field"
          >
            <option value="">Todos os clientes</option>
            {clientes.map((c) => (
              <option key={c.id} value={c.id}>{c.nome}</option>
            ))}
          </select>
        </div>
      </div>

      {error && <div className="text-accent-pink text-sm">{error}</div>}

      {projetos.length === 0 ? (
        <div className="text-center py-16">
          <p className="text-gray-500">
            {filterCliente ? 'Nenhum projeto para este cliente.' : 'Nenhum projeto cadastrado.'}
          </p>
        </div>
      ) : (
        <div className="glass-card rounded-xl border border-primary-700/50 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-primary-700/50 bg-primary-800/50">
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-400 uppercase tracking-wider">Título</th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-400 uppercase tracking-wider hidden sm:table-cell">Cliente</th>
                  <th className="text-right px-4 py-3 text-xs font-medium text-gray-400 uppercase tracking-wider hidden md:table-cell">Valor/hora</th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-400 uppercase tracking-wider hidden lg:table-cell">Criado em</th>
                  <th className="text-right px-4 py-3 text-xs font-medium text-gray-400 uppercase tracking-wider">Ações</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-primary-700/50">
                {projetos.map((p) => (
                  <tr key={p.id} className="hover:bg-primary-800/30 transition-colors">
                    <td className="px-4 py-3.5">
                      <p className="text-sm font-medium text-white">{p.titulo}</p>
                    </td>
                    <td className="px-4 py-3.5 hidden sm:table-cell">
                      <p className="text-sm text-gray-400">{getClienteNome(p.cliente_id)}</p>
                    </td>
                    <td className="px-4 py-3.5 hidden md:table-cell text-right">
                      <p className="text-sm font-mono text-accent-green">
                        {p.valor_por_hora ? `R$ ${Number(p.valor_por_hora).toFixed(2)}` : '—'}
                      </p>
                    </td>
                    <td className="px-4 py-3.5 hidden lg:table-cell">
                      <p className="text-sm text-gray-400">
                        {p.data_criacao ? formatDateBR(p.data_criacao) : '—'}
                      </p>
                    </td>
                    <td className="px-4 py-3.5 text-right">
                      <div className="flex items-center justify-end gap-1">
                        <button
                          onClick={() => navigate(`/kanban?projeto=${encodeURIComponent(p.id)}&cliente=${encodeURIComponent(p.cliente_id)}`)}
                          className="btn-icon text-gray-400 hover:text-accent-cyan"
                          title="Ver tarefas"
                        >
                          <EyeIcon className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => { setEditing(p); setFormOpen(true); }}
                          className="btn-icon text-gray-400 hover:text-accent-cyan"
                          title="Editar"
                        >
                          <PencilSquareIcon className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(p.id)}
                          className="btn-icon text-gray-400 hover:text-accent-pink"
                          title="Excluir"
                        >
                          <TrashIcon className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <ProjetoForm
        isOpen={formOpen}
        onClose={() => { setFormOpen(false); setEditing(null); }}
        onSave={() => { setFormOpen(false); setEditing(null); fetchProjetos(); }}
        projeto={editing}
        clientes={clientes}
      />
    </div>
  );
}
