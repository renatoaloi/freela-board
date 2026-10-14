import React, { useEffect, useState } from 'react';
import Modal from './Modal';
import { projetosAPI, tarefasAPI } from '../../services/api';

export default function MoverTarefaProjetoModal({ isOpen, onClose, onSuccess, tarefa }) {
  const [projetos, setProjetos] = useState([]);
  const [destino, setDestino] = useState('');
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [erro, setErro] = useState(null);

  useEffect(() => {
    if (!isOpen || !tarefa) return;
    let ativo = true;
    setLoading(true);
    setErro(null);
    projetosAPI
      .list(tarefa.cliente_id)
      .then((res) => {
        if (!ativo) return;
        const lista = (res.data || []).filter((p) => p.id !== tarefa.projeto_id);
        setProjetos(lista);
        setDestino(lista.length === 1 ? lista[0].id : '');
      })
      .catch(() => ativo && setErro('Erro ao carregar projetos.'))
      .finally(() => ativo && setLoading(false));
    return () => {
      ativo = false;
    };
  }, [isOpen, tarefa]);

  const confirmar = async () => {
    if (!destino) return;
    setSaving(true);
    setErro(null);
    try {
      await tarefasAPI.moverProjeto(tarefa.id, destino);
      onSuccess?.();
      onClose();
    } catch (err) {
      setErro(err.response?.data?.detail || 'Erro ao mover a tarefa.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Mover para outro projeto" size="max-w-md">
      <div className="space-y-4">
        <p className="text-sm text-gray-300">
          A tarefa <span className="text-white">{tarefa?.titulo}</span> será transferida com seus
          apontamentos e anexos.
        </p>

        {erro && (
          <div className="p-3 rounded-lg bg-accent-pink/10 border border-accent-pink/30 text-accent-pink text-sm">
            {erro}
          </div>
        )}

        <div>
          <label className="block text-xs font-medium text-gray-400 mb-1.5">Projeto de destino</label>
          <select
            value={destino}
            onChange={(e) => setDestino(e.target.value)}
            className="input-field"
            disabled={loading || projetos.length === 0}
          >
            <option value="">
              {loading ? 'Carregando...' : projetos.length === 0 ? 'Nenhum outro projeto' : 'Selecione...'}
            </option>
            {projetos.map((p) => (
              <option key={p.id} value={p.id}>{p.titulo}</option>
            ))}
          </select>
        </div>

        <div className="flex items-center justify-end gap-3 pt-2">
          <button type="button" onClick={onClose} className="btn-secondary">
            Cancelar
          </button>
          <button
            type="button"
            onClick={confirmar}
            disabled={!destino || saving}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {saving ? 'Movendo...' : 'Mover'}
          </button>
        </div>
      </div>
    </Modal>
  );
}
