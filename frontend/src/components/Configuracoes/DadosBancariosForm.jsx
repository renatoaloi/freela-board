import React, { useState, useEffect } from 'react';
import { dadosBancariosAPI } from '../../services/api';
import { BanknotesIcon } from '@heroicons/react/24/outline';

const tiposChavePix = [
  { value: '', label: 'Selecione...' },
  { value: 'cpf', label: 'CPF' },
  { value: 'cnpj', label: 'CNPJ' },
  { value: 'email', label: 'E-mail' },
  { value: 'telefone', label: 'Telefone' },
];

const initialState = {
  banco_nome: '',
  banco_numero: '',
  agencia: '',
  conta: '',
  chave_pix: '',
  tipo_chave_pix: '',
};

export default function DadosBancariosForm() {
  const [form, setForm] = useState(initialState);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadDados();
  }, []);

  const loadDados = async () => {
    setLoading(true);
    try {
      const res = await dadosBancariosAPI.get();
      const d = res.data;
      setForm({
        banco_nome: d.banco_nome || '',
        banco_numero: d.banco_numero || '',
        agencia: d.agencia || '',
        conta: d.conta || '',
        chave_pix: d.chave_pix || '',
        tipo_chave_pix: d.tipo_chave_pix || '',
      });
    } catch (err) {
      setError('Erro ao carregar dados bancários.');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field) => (e) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }));
    if (error) setError(null);
    if (success) setSuccess(false);
  };

  const hasAnyField = form.banco_nome || form.banco_numero || form.agencia || form.conta || form.chave_pix;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    setSuccess(false);
    try {
      await dadosBancariosAPI.update(form);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail)) {
        setError(detail.map((e) => e.msg).join('; '));
      } else if (typeof detail === 'string') {
        setError(detail);
      } else {
        setError('Erro ao salvar dados bancários.');
      }
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="glass-card rounded-xl p-6 border border-primary-700/50">
        <p className="text-gray-400 text-sm">Carregando...</p>
      </div>
    );
  }

  return (
    <div className="glass-card rounded-xl p-6 border border-primary-700/50">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-accent-green to-accent-cyan flex items-center justify-center">
          <BanknotesIcon className="w-5 h-5 text-primary-900" />
        </div>
        <div>
          <h2 className="text-lg font-semibold text-white">Dados Bancários</h2>
          <p className="text-xs text-gray-400">Informe seus dados para recebimento</p>
        </div>
      </div>

      {success && (
        <div className="mb-4 p-3 rounded-lg bg-accent-green/10 border border-accent-green/30 text-accent-green text-sm">
          Dados bancários salvos com sucesso!
        </div>
      )}

      {error && (
        <div className="mb-4 p-3 rounded-lg bg-accent-pink/10 border border-accent-pink/30 text-accent-pink text-sm">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-5">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-1.5">
            <label className="text-sm font-medium text-gray-300">Banco</label>
            <input
              value={form.banco_nome}
              onChange={handleChange('banco_nome')}
              className="input-field"
              placeholder="Nome do banco"
            />
          </div>
          <div className="space-y-1.5">
            <label className="text-sm font-medium text-gray-300">Nº do Banco</label>
            <input
              value={form.banco_numero}
              onChange={handleChange('banco_numero')}
              className="input-field"
              placeholder="Ex: 260"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-1.5">
            <label className="text-sm font-medium text-gray-300">Agência</label>
            <input
              value={form.agencia}
              onChange={handleChange('agencia')}
              className="input-field"
              placeholder="Número da agência"
            />
          </div>
          <div className="space-y-1.5">
            <label className="text-sm font-medium text-gray-300">Conta</label>
            <input
              value={form.conta}
              onChange={handleChange('conta')}
              className="input-field"
              placeholder="Número da conta"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-1.5">
            <label className="text-sm font-medium text-gray-300">Chave PIX</label>
            <input
              value={form.chave_pix}
              onChange={handleChange('chave_pix')}
              className="input-field"
              placeholder="CPF, CNPJ, e-mail ou telefone"
            />
          </div>
          <div className="space-y-1.5">
            <label className="text-sm font-medium text-gray-300">Tipo da Chave PIX</label>
            <select
              value={form.tipo_chave_pix}
              onChange={handleChange('tipo_chave_pix')}
              className="input-field"
            >
              {tiposChavePix.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="flex items-center justify-end pt-2">
          <button
            type="submit"
            disabled={saving}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {saving ? 'Salvando...' : 'Salvar'}
          </button>
        </div>
      </form>
    </div>
  );
}