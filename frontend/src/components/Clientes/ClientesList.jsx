import React, { useState, useEffect, useCallback } from 'react';
import usePersistedState from '../../hooks/usePersistedState';
import { clientesAPI } from '../../services/api';
import Loading from '../Common/Loading';
import ClienteForm from './ClienteForm';
import { PlusIcon, PencilSquareIcon, TrashIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline';

export default function ClientesList() {
  const [clientes, setClientes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = usePersistedState('clientes.search', '');
  const [formOpen, setFormOpen] = useState(false);
  const [editing, setEditing] = useState(null);

  const fetchClientes = useCallback(async () => {
    try {
      const res = await clientesAPI.list();
      setClientes(res.data || []);
    } catch {
      setError('Erro ao carregar clientes.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchClientes();
  }, [fetchClientes]);

  const handleDelete = async (id) => {
    if (!confirm('Excluir este cliente? Todas os projetos e tarefas associados serão removidos.')) return;
    try {
      await clientesAPI.delete(id);
      await fetchClientes();
    } catch {
      alert('Erro ao excluir cliente.');
    }
  };

  const filtered = clientes.filter(
    (c) =>
      c.nome?.toLowerCase().includes(search.toLowerCase()) ||
      c.email?.toLowerCase().includes(search.toLowerCase()) ||
      c.documento?.includes(search) ||
      c.cep?.includes(search) ||
      c.cidade?.toLowerCase().includes(search.toLowerCase()),
  );

  if (loading) return <Loading />;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Clientes</h1>
          <p className="text-sm text-gray-400 mt-1">Gerencie seus clientes</p>
        </div>
        <button onClick={() => { setEditing(null); setFormOpen(true); }} className="btn-primary flex items-center gap-2 self-start">
          <PlusIcon className="w-5 h-5" />
          Novo Cliente
        </button>
      </div>

      <div className="relative">
        <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
        <input
          type="text"
          placeholder="Buscar por nome, email, documento ou cidade..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="input-field pl-10"
        />
      </div>

      {error && <div className="text-accent-pink text-sm">{error}</div>}

      {filtered.length === 0 ? (
        <div className="text-center py-16">
          <p className="text-gray-500">{search ? 'Nenhum cliente encontrado.' : 'Nenhum cliente cadastrado.'}</p>
        </div>
      ) : (
        <div className="glass-card rounded-xl border border-primary-700/50 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-primary-700/50 bg-primary-800/50">
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-400 uppercase tracking-wider">Nome</th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-400 uppercase tracking-wider hidden sm:table-cell">Email</th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-400 uppercase tracking-wider hidden md:table-cell">Documento</th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-400 uppercase tracking-wider hidden lg:table-cell">CEP</th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-400 uppercase tracking-wider hidden lg:table-cell">Cidade</th>
                  <th className="text-right px-4 py-3 text-xs font-medium text-gray-400 uppercase tracking-wider">Ações</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-primary-700/50">
                {filtered.map((c) => (
                  <tr key={c.id} className="hover:bg-primary-800/30 transition-colors">
                    <td className="px-4 py-3.5">
                      <p className="text-sm font-medium text-white">{c.nome}</p>
                    </td>
                    <td className="px-4 py-3.5 hidden sm:table-cell">
                      <p className="text-sm text-gray-400">{c.email || '-'}</p>
                    </td>
                    <td className="px-4 py-3.5 hidden md:table-cell">
                      <p className="text-sm font-mono text-gray-400">{c.documento || '-'}</p>
                    </td>
                    <td className="px-4 py-3.5 hidden lg:table-cell">
                      <p className="text-sm font-mono text-gray-400">{c.cep || '-'}</p>
                    </td>
                    <td className="px-4 py-3.5 hidden lg:table-cell">
                      <p className="text-sm text-gray-400">{c.cidade || '-'}</p>
                    </td>
                    <td className="px-4 py-3.5 text-right">
                      <div className="flex items-center justify-end gap-1">
                        <button
                          onClick={() => { setEditing(c); setFormOpen(true); }}
                          className="btn-icon text-gray-400 hover:text-accent-cyan"
                          title="Editar"
                        >
                          <PencilSquareIcon className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(c.id)}
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

      <ClienteForm
        isOpen={formOpen}
        onClose={() => { setFormOpen(false); setEditing(null); }}
        onSave={() => { setFormOpen(false); setEditing(null); fetchClientes(); }}
        cliente={editing}
      />
    </div>
  );
}
