import React, { useState, useEffect, useCallback } from 'react';
import usePersistedState from '../../hooks/usePersistedState';
import { relatoriosAPI, clientesAPI } from '../../services/api';
import Loading from '../Common/Loading';
import { DocumentTextIcon, ArrowDownTrayIcon } from '@heroicons/react/24/outline';

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
  return Number(horas).toFixed(2);
}

function formatMoeda(valor) {
  if (!valor && valor !== 0) return 'R$ 0,00';
  return `R$ ${Number(valor).toFixed(2).replace('.', ',')}`;
}

export default function RelatorioView() {
  const [clientes, setClientes] = useState([]);
  const [selectedCliente, setSelectedCliente] = usePersistedState('relatorios.selectedCliente', '');
  const [selectedMes, setSelectedMes] = usePersistedState('relatorios.selectedMes', new Date().getMonth() + 1);
  const [selectedAno, setSelectedAno] = usePersistedState('relatorios.selectedAno', currentYear);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const fetchClientes = useCallback(async () => {
    try {
      const res = await clientesAPI.list();
      setClientes(res.data || []);
    } catch {}
  }, []);

  useEffect(() => { fetchClientes(); }, [fetchClientes]);

  const handleGenerate = async () => {
    if (!selectedCliente) {
      setError('Selecione um cliente.');
      return;
    }
    setGenerating(true);
    setError(null);
    setResult(null);
    try {
      const res = await relatoriosAPI.generate(selectedCliente, selectedMes, selectedAno);
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao gerar relatório.');
    } finally {
      setGenerating(false);
    }
  };

  const handleDownloadPdf = async () => {
    if (!selectedCliente) return;
    setDownloading(true);
    setError(null);
    try {
      const res = await relatoriosAPI.generatePdf(selectedCliente, selectedMes, selectedAno);
      const blob = new Blob([res.data], { type: 'application/pdf' });
      const url = URL.createObjectURL(blob);
      const disposition = res.headers?.['content-disposition'] || '';
      const match = disposition.match(/filename="?(.+?)"?$/);
      const filename = match?.[1] || `relatorio-${selectedMes}-${selectedAno}.pdf`;
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao baixar PDF.');
    } finally {
      setDownloading(false);
    }
  };

  const mesLabel = meses.find((m) => m.value === selectedMes)?.label || '';

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-white">Relatórios</h1>
        <p className="text-sm text-gray-400 mt-1">Gere relatórios de horas por cliente</p>
      </div>

      <div className="glass-card rounded-xl p-6 border border-primary-700/50">
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1.5">Cliente</label>
            <select
              value={selectedCliente}
              onChange={(e) => setSelectedCliente(e.target.value)}
              className="input-field"
            >
              <option value="">Selecione...</option>
              {clientes.map((c) => (
                <option key={c.id} value={c.id}>{c.nome}</option>
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
          <div className="flex items-end">
            <button
              onClick={handleGenerate}
              disabled={generating}
              className="btn-primary flex items-center gap-2 w-full justify-center disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <DocumentTextIcon className="w-5 h-5" />
              {generating ? 'Gerando...' : 'Gerar Relatório'}
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-accent-pink/10 border border-accent-pink/30 text-accent-pink text-sm">
          {error}
        </div>
      )}

      {result && (
        <div className="space-y-6 print-area" id="relatorio-print">
          <div className="glass-card rounded-xl p-6 border border-primary-700/50">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-white">Relatório de Horas</h2>
              <div className="flex items-center gap-2">
                <button
                  onClick={handleDownloadPdf}
                  disabled={downloading}
                  className="btn-primary flex items-center gap-2 text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ArrowDownTrayIcon className="w-4 h-4" />
                  {downloading ? 'Baixando...' : 'Baixar PDF'}
                </button>
                <button
                  onClick={() => window.print()}
                  className="btn-secondary flex items-center gap-2 text-sm"
                >
                  <ArrowDownTrayIcon className="w-4 h-4" />
                  Imprimir
                </button>
              </div>
            </div>
            <p className="text-sm text-accent-cyan mb-4">
              Período: {mesLabel} / {selectedAno}
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
              <div className="bg-primary-800/50 rounded-lg p-4 border border-primary-700/50">
                <h3 className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-2">Dados do Cliente</h3>
                <p className="text-sm font-medium text-white">{result.cliente?.nome || '—'}</p>
                {result.cliente?.razao_social && (
                  <p className="text-xs text-gray-400">{result.cliente.razao_social}</p>
                )}
                <p className="text-xs text-gray-500 mt-1 font-mono">{result.cliente?.documento || ''}</p>
                {result.cliente?.endereco && (
                  <p className="text-xs text-gray-500 mt-1">
                    {result.cliente.endereco}
                    {result.cliente.complemento ? `, ${result.cliente.complemento}` : ''}
                    {result.cliente.bairro ? ` - ${result.cliente.bairro}` : ''}
                  </p>
                )}
                {result.cliente?.cep && (
                  <p className="text-xs text-gray-500">CEP {result.cliente.cep}</p>
                )}
                {result.cliente?.cidade && (
                  <p className="text-xs text-gray-500">
                    {result.cliente.cidade}{result.cliente.estado ? `/ ${result.cliente.estado}` : ''}
                  </p>
                )}
                {result.cliente?.email && (
                  <p className="text-xs text-gray-500 mt-1">{result.cliente.email}</p>
                )}
              </div>
              <div>
                {result.dados_bancarios && (result.dados_bancarios.banco_nome || result.dados_bancarios.banco_numero || result.dados_bancarios.agencia || result.dados_bancarios.conta || result.dados_bancarios.chave_pix) && (
                  <div className="bg-primary-800/50 rounded-lg p-4 border border-primary-700/50 mb-4">
                    <h3 className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-2">Dados Bancários</h3>
                    {result.dados_bancarios.banco_nome && (
                      <p className="text-sm text-white">{result.dados_bancarios.banco_nome}{result.dados_bancarios.banco_numero ? ` (${result.dados_bancarios.banco_numero})` : ''}</p>
                    )}
                    {result.dados_bancarios.agencia && (
                      <p className="text-xs text-gray-400 mt-1">Agência: {result.dados_bancarios.agencia}</p>
                    )}
                    {result.dados_bancarios.conta && (
                      <p className="text-xs text-gray-400">Conta: {result.dados_bancarios.conta}</p>
                    )}
                    {result.dados_bancarios.chave_pix && (
                      <p className="text-xs text-gray-400 mt-1">PIX: {result.dados_bancarios.chave_pix}{result.dados_bancarios.tipo_chave_pix ? ` (${result.dados_bancarios.tipo_chave_pix.toUpperCase()})` : ''}</p>
                    )}
                  </div>
                )}
                <div className="bg-primary-800/50 rounded-lg p-4 border border-primary-700/50">
                  <h3 className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-2">Resumo</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-400">Total de Horas</span>
                      <span className="text-sm font-mono text-accent-green font-medium">{formatHoras(result.totais?.total_horas)}h</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-400">Valor Total</span>
                      <span className="text-sm font-mono text-accent-pinkLight font-bold">{formatMoeda(result.totais?.total_valor)}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {result.projetos && result.projetos.length > 0 && (
              <div>
                <h3 className="text-sm font-medium text-gray-300 mb-3">Detalhamento por Projeto</h3>
                <div className="space-y-3">
                  {result.projetos.map((proj, i) => (
                    <div
                      key={proj.projeto_id || i}
                      className="bg-primary-800/30 rounded-lg p-4 border border-primary-700/50"
                    >
                      <h4 className="text-sm font-medium text-white mb-2">{proj.titulo}</h4>
                      <div className="grid grid-cols-3 gap-4 text-sm">
                        <div>
                          <span className="text-xs text-gray-500">Horas</span>
                          <p className="font-mono text-gray-200">{formatHoras(proj.total_horas)}h</p>
                        </div>
                        <div>
                          <span className="text-xs text-gray-500">Valor/hora</span>
                          <p className="font-mono text-gray-200">{formatMoeda(proj.valor_por_hora)}</p>
                        </div>
                        <div>
                          <span className="text-xs text-gray-500">Total</span>
                          <p className="font-mono text-accent-pinkLight font-medium">{formatMoeda(proj.valor_total)}</p>
                        </div>
                      </div>
                      {proj.tarefas && proj.tarefas.length > 0 && (
                        <div className="mt-3 pt-3 border-t border-primary-700/30">
                          <h5 className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-2">Tarefas</h5>
                          <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                              <thead>
                                <tr className="border-b border-primary-700/30">
                                  <th className="text-left px-2 py-1 text-xs text-gray-500">Tarefa</th>
                                  <th className="text-right px-2 py-1 text-xs text-gray-500">Horas</th>
                                </tr>
                              </thead>
                              <tbody className="divide-y divide-primary-700/20">
                                {proj.tarefas.map((tarefa, j) => (
                                  <tr key={tarefa.tarefa_id || j}>
                                    <td className="px-2 py-1 text-gray-200">{tarefa.titulo}</td>
                                    <td className="px-2 py-1 text-right font-mono text-accent-green">{formatHoras(tarefa.total_horas)}h</td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {!result && !generating && !error && (
        <div className="text-center py-16">
          <DocumentTextIcon className="w-12 h-12 mx-auto text-gray-600 mb-3" />
          <p className="text-gray-500">Selecione um cliente, mês e ano para gerar o relatório.</p>
        </div>
      )}
    </div>
  );
}
