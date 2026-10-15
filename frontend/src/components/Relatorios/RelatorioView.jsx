import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { relatoriosAPI, uploadAPI } from '../../services/api';
import { formatDateBR } from '../../utils/date';
import Loading from '../Common/Loading';
import { ArrowDownTrayIcon, ArrowLeftIcon } from '@heroicons/react/24/outline';

const IMAGE_EXTS = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'bmp', 'ico'];

function TaskImages({ tarefaId, anexos }) {
  const imagens = (anexos || []).filter((fn) =>
    IMAGE_EXTS.includes(String(fn).toLowerCase().split('.').pop()),
  );

  if (!tarefaId || imagens.length === 0) return null;

  return (
    <div className="mt-3 grid grid-cols-2 sm:grid-cols-3 gap-2">
      {imagens.map((nome, i) => (
        <TaskImage key={nome || i} tarefaId={tarefaId} nome={nome} />
      ))}
    </div>
  );
}

function TaskImage({ tarefaId, nome }) {
  const [url, setUrl] = useState(null);

  useEffect(() => {
    let ativo = true;
    let criado = null;
    uploadAPI
      .download(tarefaId, nome)
      .then((res) => {
        if (!ativo) return;
        criado = URL.createObjectURL(res.data);
        setUrl(criado);
      })
      .catch(() => ativo && setUrl(null));
    return () => {
      ativo = false;
      if (criado) URL.revokeObjectURL(criado);
    };
  }, [tarefaId, nome]);

  if (!url) return null;
  return (
    <a href={url} target="_blank" rel="noreferrer" className="block">
      <img
        src={url}
        alt={nome}
        className="w-full h-32 object-cover rounded-lg border border-primary-700/50 hover:border-accent-cyan/50 transition-colors"
      />
    </a>
  );
}

function formatHoras(horas) {
  if (!horas && horas !== 0) return '0,00';
  return Number(horas).toFixed(2).replace('.', ',');
}

function formatMoeda(valor) {
  if (!valor && valor !== 0) return 'R$ 0,00';
  return `R$ ${Number(valor).toFixed(2).replace('.', ',')}`;
}

export default function RelatorioView() {
  const { id } = useParams();
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [downloading, setDownloading] = useState(false);

  const fetchRelatorio = useCallback(async () => {
    setLoading(true);
    try {
      const res = await relatoriosAPI.get(id);
      setResult(res.data);
    } catch {
      setError('Relatório não encontrado.');
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchRelatorio();
  }, [fetchRelatorio]);

  const handleDownloadPdf = async () => {
    setDownloading(true);
    setError(null);
    try {
      const res = await relatoriosAPI.downloadPdf(id);
      const blob = new Blob([res.data], { type: 'application/pdf' });
      const url = URL.createObjectURL(blob);
      const disposition = res.headers?.['content-disposition'] || '';
      const match = disposition.match(/filename="?(.+?)"?$/);
      const filename = match?.[1] || 'relatorio.pdf';
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

  if (loading) return <Loading />;

  if (error || !result) {
    return (
      <div className="space-y-6 max-w-4xl mx-auto text-center py-16">
        <p className="text-gray-500">{error || 'Relatório não encontrado.'}</p>
        <Link to="/relatorios" className="text-sm text-accent-green hover:underline">
          Voltar para a lista
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <Link to="/relatorios" className="inline-flex items-center gap-2 text-sm text-gray-400 hover:text-accent-green">
        <ArrowLeftIcon className="w-4 h-4" />
        Voltar para a lista
      </Link>

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
                Imprimir
              </button>
            </div>
          </div>
          <p className="text-sm text-accent-cyan mb-4">
            Período: {result.mes_referencia}
            {result.numero > 1 ? ` · Fechamento ${result.numero}` : ''}
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
                      <div className="mt-3 pt-3 border-t border-primary-700/30 space-y-4">
                        <h5 className="text-xs font-medium text-gray-400 uppercase tracking-wider">Tarefas</h5>
                        {proj.tarefas.map((tarefa, j) => (
                          <div
                            key={tarefa.tarefa_id || j}
                            className="bg-primary-800/40 rounded-lg p-3 border border-primary-700/40"
                          >
                            <div className="flex items-start justify-between gap-3">
                              <h6 className="text-sm font-medium text-white">{tarefa.titulo}</h6>
                              <span className="text-sm font-mono text-accent-green">
                                {formatHoras(tarefa.total_horas)}h
                              </span>
                            </div>

                            {tarefa.descricao && (
                              <p className="text-xs text-gray-400 mt-2 whitespace-pre-line">
                                {tarefa.descricao}
                              </p>
                            )}

                            {tarefa.dias && tarefa.dias.length > 0 && (
                              <div className="mt-2 space-y-1">
                                {tarefa.dias.map((dia, k) => (
                                  <div key={dia.data || k}>
                                    <p className="text-xs font-medium text-gray-300">
                                      {formatDateBR(dia.data)}{' '}
                                      <span className="font-mono text-accent-green">
                                        {formatHoras(dia.total_horas)}h
                                      </span>
                                    </p>
                                    {dia.apontamentos?.length > 0 && (
                                      <p className="text-xs text-gray-500">
                                        {dia.apontamentos
                                          .map(
                                            (a) =>
                                              `${a.hora_ini} - ${a.hora_fim} (${formatHoras(a.total_horas)}h)`,
                                          )
                                          .join(' · ')}
                                      </p>
                                    )}
                                  </div>
                                ))}
                              </div>
                            )}

                            <TaskImages tarefaId={tarefa.tarefa_id} anexos={tarefa.anexos} />
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
