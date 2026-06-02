import React, { useState, useEffect } from 'react';
import { clientesAPI } from '../../services/api';
import Modal from '../Common/Modal';

const estados = [
  'AC','AL','AP','AM','BA','CE','DF','ES','GO','MA','MT','MS','MG','PA','PB','PR','PE','PI','RJ','RN','RS','RO','RR','SC','SP','SE','TO',
];

const initialState = {
  nome: '',
  razao_social: '',
  email: '',
  documento: '',
  endereco: '',
  complemento: '',
  bairro: '',
  cidade: '',
  estado: '',
};

export default function ClienteForm({ isOpen, onClose, onSave, cliente }) {
  const [form, setForm] = useState(initialState);
  const [errors, setErrors] = useState({});
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (cliente) {
      setForm({
        nome: cliente.nome || '',
        razao_social: cliente.razao_social || '',
        email: cliente.email || '',
        documento: cliente.documento || '',
        endereco: cliente.endereco || '',
        complemento: cliente.complemento || '',
        bairro: cliente.bairro || '',
        cidade: cliente.cidade || '',
        estado: cliente.estado || '',
      });
    } else {
      setForm(initialState);
    }
    setErrors({});
  }, [cliente, isOpen]);

  const validate = () => {
    const errs = {};
    if (!form.nome.trim()) errs.nome = 'Nome é obrigatório.';
    if (form.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) errs.email = 'Email inválido.';
    if (!form.documento.trim()) errs.documento = 'CNPJ é obrigatório.';
    else {
      const digits = form.documento.replace(/\D/g, '');
      if (digits.length !== 14) errs.documento = 'CNPJ deve ter 14 dígitos.';
    }
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;
    setSaving(true);
    try {
      const payload = { ...form };
      payload.documento = form.documento.replace(/\D/g, '');
      if (cliente) {
        await clientesAPI.update(cliente.id, payload);
      } else {
        await clientesAPI.create(payload);
      }
      onSave();
    } catch (err) {
      const msg = err.response?.data?.detail || 'Erro ao salvar cliente.';
      setErrors({ submit: msg });
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (field) => (e) => {
    let val = e.target.value;
    if (field === 'documento') val = val.replace(/\D/g, '').slice(0, 14);
    setForm((prev) => ({ ...prev, [field]: val }));
    if (errors[field]) setErrors((prev) => ({ ...prev, [field]: null }));
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={cliente ? 'Editar Cliente' : 'Novo Cliente'} size="max-w-3xl">
      <form onSubmit={handleSubmit} className="space-y-5">
        {errors.submit && (
          <div className="p-3 rounded-lg bg-accent-pink/10 border border-accent-pink/30 text-accent-pink text-sm">
            {errors.submit}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-1.5">
            <label className="text-sm font-medium text-gray-300">Nome *</label>
            <input value={form.nome} onChange={handleChange('nome')} className="input-field" placeholder="Nome do cliente" />
            {errors.nome && <p className="text-xs text-accent-pink">{errors.nome}</p>}
          </div>
          <div className="space-y-1.5">
            <label className="text-sm font-medium text-gray-300">Razão Social</label>
            <input value={form.razao_social} onChange={handleChange('razao_social')} className="input-field" placeholder="Razão social" />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-1.5">
            <label className="text-sm font-medium text-gray-300">Email</label>
            <input value={form.email} onChange={handleChange('email')} className="input-field" type="email" placeholder="email@exemplo.com" />
            {errors.email && <p className="text-xs text-accent-pink">{errors.email}</p>}
          </div>
          <div className="space-y-1.5">
            <label className="text-sm font-medium text-gray-300">CNPJ *</label>
            <input value={form.documento} onChange={handleChange('documento')} className="input-field font-mono" placeholder="Apenas números" />
            {errors.documento && <p className="text-xs text-accent-pink">{errors.documento}</p>}
          </div>
        </div>

        <div className="space-y-1.5">
          <label className="text-sm font-medium text-gray-300">Endereço</label>
          <input value={form.endereco} onChange={handleChange('endereco')} className="input-field" placeholder="Rua, número" />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="space-y-1.5">
            <label className="text-sm font-medium text-gray-300">Complemento</label>
            <input value={form.complemento} onChange={handleChange('complemento')} className="input-field" placeholder="Apto, sala" />
          </div>
          <div className="space-y-1.5">
            <label className="text-sm font-medium text-gray-300">Bairro</label>
            <input value={form.bairro} onChange={handleChange('bairro')} className="input-field" placeholder="Bairro" />
          </div>
          <div className="space-y-1.5">
            <label className="text-sm font-medium text-gray-300">Cidade</label>
            <input value={form.cidade} onChange={handleChange('cidade')} className="input-field" placeholder="Cidade" />
          </div>
        </div>

        <div className="space-y-1.5">
          <label className="text-sm font-medium text-gray-300">Estado</label>
          <select value={form.estado} onChange={handleChange('estado')} className="input-field">
            <option value="">Selecione...</option>
            {estados.map((uf) => (
              <option key={uf} value={uf}>{uf}</option>
            ))}
          </select>
        </div>

        <div className="flex items-center justify-end gap-3 pt-2">
          <button type="button" onClick={onClose} className="btn-secondary">
            Cancelar
          </button>
          <button type="submit" disabled={saving} className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed">
            {saving ? 'Salvando...' : cliente ? 'Atualizar' : 'Criar'}
          </button>
        </div>
      </form>
    </Modal>
  );
}
