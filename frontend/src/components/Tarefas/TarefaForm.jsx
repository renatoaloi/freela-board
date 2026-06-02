import React, { useState, useEffect } from 'react';
import { tarefasAPI } from '../../services/api';
import Modal from '../Common/Modal';
import MarkdownEditor from '../Common/MarkdownEditor';

const statusOptions = [
  { value: 'nova', label: 'Nova' },
  { value: 'em_andamento', label: 'Em Andamento' },
  { value: 'pronta', label: 'Pronta' },
  { value: 'fechada', label: 'Fechada' },
];

const initialState = {
  titulo: '',
  descricao: '',
  status: 'nova',
  projeto_id: '',
};

export default function TarefaForm({ isOpen, onClose, onSave, tarefa, projetoId, initialStatus = 'nova' }) {
  const [form, setForm] = useState(initialState);
  const [errors, setErrors] = useState({});
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (tarefa) {
      setForm({
        titulo: tarefa.titulo || '',
        descricao: tarefa.descricao || '',
        status: tarefa.status || 'nova',
        projeto_id: tarefa.projeto_id || projetoId || '',
      });
    } else {
      setForm({ ...initialState, status: initialStatus, projeto_id: projetoId || '' });
    }
    setErrors({});
  }, [tarefa, isOpen, projetoId, initialStatus]);

  const validate = () => {
    const errs = {};
    if (!form.titulo.trim()) errs.titulo = 'Título é obrigatório.';
    if (!form.projeto_id) errs.projeto_id = 'Projeto é obrigatório.';
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;
    setSaving(true);
    try {
      if (tarefa) {
        await tarefasAPI.update(tarefa.id, {
          titulo: form.titulo,
          descricao: form.descricao,
          status: form.status,
        });
      } else {
        await tarefasAPI.create({
          titulo: form.titulo,
          descricao: form.descricao,
          status: form.status,
          projeto_id: form.projeto_id,
        });
      }
      onSave();
    } catch (err) {
      const msg = err.response?.data?.detail || 'Erro ao salvar tarefa.';
      setErrors({ submit: msg });
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (field) => (e) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }));
    if (errors[field]) setErrors((prev) => ({ ...prev, [field]: null }));
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={tarefa ? 'Editar Tarefa' : 'Nova Tarefa'} size="max-w-3xl">
      <form onSubmit={handleSubmit} className="space-y-5">
        {errors.submit && (
          <div className="p-3 rounded-lg bg-accent-pink/10 border border-accent-pink/30 text-accent-pink text-sm">
            {errors.submit}
          </div>
        )}

        <div className="space-y-1.5">
          <label className="text-sm font-medium text-gray-300">Título *</label>
          <input value={form.titulo} onChange={handleChange('titulo')} className="input-field" placeholder="Título da tarefa" />
          {errors.titulo && <p className="text-xs text-accent-pink">{errors.titulo}</p>}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-1.5">
            <label className="text-sm font-medium text-gray-300">Status</label>
            <select value={form.status} onChange={handleChange('status')} className="input-field">
              {statusOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>
        </div>

        <MarkdownEditor
          label="Descrição"
          value={form.descricao}
          onChange={(val) => setForm((prev) => ({ ...prev, descricao: val }))}
          rows={8}
        />

        <div className="flex items-center justify-end gap-3 pt-2">
          <button type="button" onClick={onClose} className="btn-secondary">Cancelar</button>
          <button type="submit" disabled={saving} className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed">
            {saving ? 'Salvando...' : tarefa ? 'Atualizar' : 'Criar'}
          </button>
        </div>
      </form>
    </Modal>
  );
}
