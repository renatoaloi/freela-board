import React, { useState, useEffect, useCallback } from 'react';
import usePersistedState from '../../hooks/usePersistedState';
import { fechamentoAPI, clientesAPI, projetosAPI } from '../../services/api';
import ConfirmModal from '../Common/ConfirmModal';
import AlertModal from '../Common/AlertModal';
import { CheckIcon } from '@heroicons/react/24/outline';

const meses = [
  { value: 1, label: 'Janeiro' },
  { value: 2, label: 'Fevereiro' },
  { value: 3, label: 'Março' },
  { value: 4, label: 'Abril' },
  { value: 5, label: 'Maio' },
  { value: 6, label: 'Junho' },
  { value: 7, label: 'Julho' },
  { value: 8, label: 'Agosto' },
  { value: 9, label: 'Setembro' },
  { value: 10, label: 'Outubro' },
  { value: 11, label: 'Novembro' },
  { value: 12, label: 'Dezembro' },
];

const currentYear = new Date().getFullYear();
const anos = Array.from({ length: 5 }, (_, i) => currentYear - i);

function formatHoras(horas) {
  if (!horas && horas !== 0) return '0,00';
  return Number(horas).toFixed(2).replace('.', ',');
}

function formatMoeda(valor) {
  if (!valor && valor !== 0) return 'R$ 0,00';
  return `R$ ${Number(valor).toFixed(2).replace('.', ',')}`;
}

export default function FechamentoMensal() {
  const [clientes, setClientes] = useState([]);
  const [projetos, setProjetos] = useState([]);
  const [selectedCliente, setSelectedCliente] = usePersistedState('fechamento.selectedCliente', '');
  const [selectedProjeto, setSelectedProjeto] = usePersistedState('fechamento.selectedProjeto', '');
  const [selectedMes, setSelectedMes] = usePersistedState('fechamento.selectedMes', new Date().getMonth() + 1);
  const [selectedAno, setSelectedAno] = usePersistedState('fechamento.selectedAno', currentYear);
  const [tarefas, setTarefas] = useState([]);
  const [valorHoraPorProjeto, setValorHoraPorProjeto] = useState({});
  const [selecionadas, setSelecionadas] = useState([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [alertMsg, setAlertMsg] = useState(null);
  const [confirmOpen, setConfirmOpen] = useState(false);

  const fetchClientes = useCallback(async () => {
    try {
      const res = await clientesAPI.list();
      setClientes(res.data || []);
    } catch {
      setError('Erro ao carregar clientes.');
    }
  }, []);

  useEffect(() => {
    fetchClientes();
  }, [fetchClientes]);

  const fetchProjetos = useCallback(async () => {
    if (!selectedCliente) {
      setProjetos([]);
      return;
    }
    try {
      const res = await projetosAPI.list(selectedCliente);
      setProjetos(res.data || []);
    } catch {
      setError('Erro ao carregar projetos.');
    }
  }, [selectedCliente]);

  useEffect(() => {
    fetchProjetos();
  }, [fetchProjetos]);

  const fetchElegiveis = useCallback(async () => {
    if (!selectedCliente) {
      setTarefas([]);
      setSelecionadas([]);
      return;
    }
    setLoading(true);
    setError(null);
    setSelecionadas([]);
    try {
      const params = [selectedCliente, selectedMes, selectedAno, selectedProjeto || undefined];
      const res = await fechamentoAPI.tarefasElegiveis(...params);
      setTarefas(res.data || []);
    } catch {
      setError('Erro ao carregar tarefas elegíveis.');
      setTarefas([]);
    } finally {
      setLoading(false);
    }
  }, [selectedCliente, selectedProjeto, selectedMes, selectedAno]);

  useEffect(() => {
    fetchElegiveis();
  }, [fetchElegiveis]);

  useEffect(() => {
    const map = {};
    projetos.forEach((p) => {
      map[p.id] = p.valor_por_hora;
    });
    setValorHoraPorProjeto(map);
  }, [projetos]);

  const toggleTarefa = (tarefaId) => {
    setSelecionadas((prev) =>
      prev.includes(tarefaId)
        ? prev.filter((id) => id !== tarefaId)
        : [...prev, tarefaId],
    );
  };

  const totalHoras = tarefas
    .filter((t) => selecionadas.includes(t.tarefa_id))
    .reduce((acc, t) => acc + t.total_horas_periodo, 0);

  const totalValor = tarefas
    .filter((t) => selecionadas.includes(t.tarefa_id))
    .reduce((acc, t) => acc + t.total_horas_periodo * (valorHoraPorProjeto[t.projeto_id] || 0), 0);

  const handleConfirmarFechamento = async () => {
    setConfirmOpen(false);
    setSaving(true);
    setError(null);
    try {
      await fechamentoAPI.fechar({
        cliente_id: selectedCliente,
        mes: selectedMes,
        ano: selectedAno,
        tarefa_ids: selecionadas,
      });
      setSelecionadas([]);
      setAlertMsg('Fechamento realizado com sucesso.');
      await fetchElegiveis();
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao fechar o mês.');
    } finally {
      setSaving(false);
    }
  };

  const mesLabel = meses.find((m) => m.value === selectedMes)?.label || '';

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-white">Fechamento Mensal</h1>
        <p className="text-sm text-gray-400 mt-1">
          Consolide as tarefas prontas do período em um relatório do mês
        </p>
      </div>

      <div className="glass-card rounded-xl p-6 border border-primary-700/50">
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1.5">Cliente</label>
            <select
              value={selectedCliente}
              onChange={(e) => {
                setSelectedCliente(e.target.value);
                setSelectedProjeto('');
              }}
              className="input-field"
            >
              <option value="">Selecione...</option>
              {clientes.map((c) => (
                <option key={c.id} value={c.id}>{c.nome}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1.5">Projeto</label>
            <select
              value={selectedProjeto}
              onChange={(e) => setSelectedProjeto(e.target.value)}
              className="input-field"
              disabled={!selectedCliente}
            >
              <option value="">Todos os projetos</option>
              {projetos.map((p) => (
                <option key={p.id} value={p.id}>{p.titulo}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1.5">Mês</label>
            <select
              value={selectedMes}
              onChange={(e) => setSelectedMes(Number(e.target.value))}
              className="input-field"
            >
              {meses.map((m) => (
                <option key={m.value} value={m.value}>{m.label}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1.5">Ano</label>
            <select
              value={selectedAno}
              onChange={(e) => setSelectedAno(Number(e.target.value))}
              className="input-field"
            >
              {anos.map((a) => (
                <option key={a} value={a}>{a}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-accent-pink/10 border border-accent-pink/30 text-accent-pink text-sm">
          {error}
        </div>
      )}

      {!selectedCliente ? (
        <div className="text-center py-16">
          <CheckIcon className="w-12 h-12 mx-auto text-gray-600 mb-3" />
          <p className="text-gray-500">Selecione um cliente para ver as tarefas do período.</p>
        </div>
      ) : loading ? (
        <div className="text-center py-16 text-gray-500">Carregando tarefas...</div>
      ) : tarefas.length === 0 ? (
        <div className="text-center py-16">
          <CheckIcon className="w-12 h-12 mx-auto text-gray-600 mb-3" />
          <p className="text-gray-500">
            Nenhuma tarefa pronta com apontamentos em {mesLabel} / {selectedAno}.
          </p>
        </div>
      ) : (
        <>
          <div className="space-y-2">
            {tarefas.map((t) => (
              <label
                key={t.tarefa_id}
                className="flex items-start gap-3 glass-card rounded-lg p-4 border border-primary-700/50 cursor-pointer hover:border-accent-green/40 transition-colors"
              >
                <input
                  type="checkbox"
                  checked={selecionadas.includes(t.tarefa_id)}
                  onChange={() => toggleTarefa(t.tarefa_id)}
                  className="mt-1 h-4 w-4 accent-accent-green"
                />
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-white">{t.titulo}</p>
                  <p className="text-xs text-gray-500">{t.projeto_titulo}</p>
                </div>
                <span className="text-sm font-mono text-accent-green">
                  {formatHoras(t.total_horas_periodo)}h
                </span>
              </label>
            ))}
          </div>

          <div className="glass-card rounded-xl p-6 border border-primary-700/50">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div className="space-y-1">
                <p className="text-xs text-gray-400 uppercase tracking-wider">
                  Seleção — {mesLabel} / {selectedAno}
                </p>
                <p className="text-sm text-gray-300">
                  {selecionadas.length} de {tarefas.length} tarefas ·{' '}
                  <span className="font-mono text-accent-green">{formatHoras(totalHoras)}h</span> ·{' '}
                  <span className="font-mono text-accent-pinkLight">{formatMoeda(totalValor)}</span>
                </p>
              </div>
              <button
                onClick={() => setConfirmOpen(true)}
                disabled={selecionadas.length === 0 || saving}
                className="btn-primary flex items-center gap-2 self-start disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {saving ? 'Fechando...' : 'Fechar mês'}
              </button>
            </div>
          </div>
        </>
      )}

      <ConfirmModal
        isOpen={confirmOpen}
        title="Fechar mês"
        message={`Confirma o fechamento de ${mesLabel} / ${selectedAno} com ${selecionadas.length} tarefa(s)? As tarefas selecionadas vão para o status Fechada.`}
        confirmLabel="Fechar"
        onCancel={() => setConfirmOpen(false)}
        onConfirm={handleConfirmarFechamento}
      />

      <AlertModal
        isOpen={!!alertMsg}
        title="Fechamento"
        message={alertMsg}
        onClose={() => setAlertMsg(null)}
      />
    </div>
  );
}
