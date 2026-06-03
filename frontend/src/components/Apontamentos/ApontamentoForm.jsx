import React, { useState, useRef } from 'react';
import { apontamentosAPI } from '../../services/api';
import { PlusIcon } from '@heroicons/react/24/outline';
import { getTodayLocalISO } from '../../utils/date';

function calcHoras(ini, fim) {
  if (!ini || !fim) return 0;
  const [h1, m1] = ini.split(':').map(Number);
  const [h2, m2] = fim.split(':').map(Number);
  const total = h2 * 60 + m2 - (h1 * 60 + m1);
  return total > 0 ? total / 60 : 0;
}

function formatHoras(horas) {
  const h = Math.floor(horas);
  const m = Math.round((horas - h) * 60);
  return `${h}h ${m}m`;
}

export default function ApontamentoForm({ tarefaId, onSave }) {
  const [data, setData] = useState(getTodayLocalISO());
  const [horaIni, setHoraIni] = useState('');
  const [horaFim, setHoraFim] = useState('');
  const dataRef = useRef(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  const totalHoras = calcHoras(horaIni, horaFim);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!data || !horaIni || !horaFim) {
      setError('Preencha todos os campos.');
      return;
    }
    if (totalHoras <= 0) {
      setError('Hora fim deve ser maior que hora início.');
      return;
    }
    setSaving(true);
    setError(null);
    try {
      await apontamentosAPI.create({
        tarefa_id: tarefaId,
        data,
        hora_ini: horaIni,
        hora_fim: horaFim,
        total_horas: totalHoras,
      });
      setHoraIni('');
      setHoraFim('');
      setData(getTodayLocalISO());
      dataRef.current?.focus();
      if (onSave) onSave();
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao salvar apontamento.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="glass-card rounded-xl p-4 border border-primary-700/50 space-y-3">
      <h4 className="text-sm font-medium text-gray-300">Novo Apontamento</h4>

      {error && <div className="text-xs text-accent-pink">{error}</div>}

      <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
        <div>
          <label className="block text-xs text-gray-400 mb-1">Data</label>
          <input
            ref={dataRef}
            type="date"
            value={data}
            onChange={(e) => setData(e.target.value)}
            className="input-field text-sm"
            autoFocus
          />
        </div>
        <div>
          <label className="block text-xs text-gray-400 mb-1">Hora Início</label>
          <input
            type="time"
            value={horaIni}
            onChange={(e) => setHoraIni(e.target.value)}
            className="input-field text-sm"
          />
        </div>
        <div>
          <label className="block text-xs text-gray-400 mb-1">Hora Fim</label>
          <input
            type="time"
            value={horaFim}
            onChange={(e) => setHoraFim(e.target.value)}
            className="input-field text-sm"
          />
        </div>
        <div className="flex items-end gap-2">
          <div className="flex-1">
            <label className="block text-xs text-gray-400 mb-1">Total</label>
            <div className="input-field text-sm text-accent-green font-mono flex items-center h-[42px] bg-primary-800/50">
              {totalHoras > 0 ? formatHoras(totalHoras) : '0h 0m'}
            </div>
          </div>
          <button
            type="submit"
            disabled={saving}
            className="btn-primary p-2.5 mb-0 disabled:opacity-50 disabled:cursor-not-allowed"
            title="Adicionar"
          >
            <PlusIcon className="w-5 h-5" />
          </button>
        </div>
      </div>
    </form>
  );
}
