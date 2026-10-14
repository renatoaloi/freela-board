import React, { useState, useEffect } from 'react';
import { projetosAPI } from '../../services/api';
import Modal from '../Common/Modal';
import MarkdownEditor from '../Common/MarkdownEditor';

const initialState = {
  titulo: '',
  descricao: '',
  cliente_id: '',
  valor_por_hora: '',
};

export default function ProjetoForm({ isOpen, onClose, onSave, projeto, clientes = [] }) {
  const [form, setForm] = useState(initialState);
  const [errors, setErrors] = useState({});
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (projeto) {
      setForm({
        titulo: projeto.titulo || '',
        descricao: projeto.descricao || '',
        cliente_id: projeto.cliente_id || '',
        valor_por_hora: projeto.valor_por_hora ?? '',
      });
    } else {
      setForm(initialState);
    }
    setErrors({});
  }, [projeto, isOpen]);

  const validate = () => {
    const errs = {};
    if (!form.titulo.trim()) errs.titulo = 'Título é obrigatório.';
    if (!form.cliente_id) errs.cliente_id = 'Selecione um cliente.';
    const vph = parseFloat(form.valor_por_hora);
    if (!form.valor_por_hora || isNaN(vph) || vph <= 0) errs.valor_por_hora = 'Valor por hora deve ser maior que zero.';
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;
    setSaving(true);
    try {
      const payload = {
        ...form,
        valor_por_hora: parseFloat(form.valor_por_hora),
      };
      if (projeto) {
        await projetosAPI.update(projeto.id, payload);
      } else {
        await projetosAPI.create(payload);
      }
      onSave();
    } catch (err) {
      const detail = err.response?.data?.detail;
      let msg = 'Erro ao salvar projeto.';
      if (Array.isArray(detail)) {
        msg = detail.map((e) => e.msg).join('; ');
      } else if (typeof detail === 'string') {
        msg = detail;
      }
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
    <Modal isOpen={isOpen} onClose={onClose} title={projeto ? 'Editar Projeto' : 'Novo Projeto'} size="max-w-3xl">
      <form onSubmit={handleSubmit} className="space-y-5">
        {errors.submit && (
          <div className="p-3 rounded-lg bg-accent-pink/10 border border-accent-pink/30 text-accent-pink text-sm">
            {errors.submit}
          </div>
        )}

        <div className="space-y-1.5">
          <label className="text-sm font-medium text-gray-300">Título *</label>
          <input value={form.titulo} onChange={handleChange('titulo')} className="input-field" placeholder="Título do projeto" />
          {errors.titulo && <p className="text-xs text-accent-pink">{errors.titulo}</p>}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-1.5">
            <label className="text-sm font-medium text-gray-300">Cliente *</label>
            <select value={form.cliente_id} onChange={handleChange('cliente_id')} className="input-field">
              <option value="">Selecione um cliente...</option>
              {clientes.map((c) => (
                <option key={c.id} value={c.id}>{c.nome}</option>
              ))}
            </select>
            {errors.cliente_id && <p className="text-xs text-accent-pink">{errors.cliente_id}</p>}
          </div>
          <div className="space-y-1.5">
            <label className="text-sm font-medium text-gray-300">Valor por Hora (R$) *</label>
            <input
              value={form.valor_por_hora}
              onChange={handleChange('valor_por_hora')}
              className="input-field font-mono"
              type="number"
              step="0.01"
              min="0"
              placeholder="0.00"
            />
            {errors.valor_por_hora && <p className="text-xs text-accent-pink">{errors.valor_por_hora}</p>}
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
            {saving ? 'Salvando...' : projeto ? 'Atualizar' : 'Criar'}
          </button>
        </div>
      </form>
    </Modal>
  );
}
