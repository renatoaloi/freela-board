import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { relatoriosAPI } from '../../services/api';
import { formatDateBR } from '../../utils/date';
import Loading from '../Common/Loading';
import AlertModal from '../Common/AlertModal';
import ConfirmModal from '../Common/ConfirmModal';
import { DocumentTextIcon, ArrowDownTrayIcon, ArrowUturnLeftIcon } from '@heroicons/react/24/outline';

const meses = [
  'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
  'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro',
];

function formatHoras(horas) {
  if (!horas && horas !== 0) return '0,00';
  return Number(horas).toFixed(2).replace('.', ',');
}

function formatMoeda(valor) {
  if (!valor && valor !== 0) return 'R$ 0,00';
  return `R$ ${Number(valor).toFixed(2).replace('.', ',')}`;
}

export default function RelatoriosList() {
  const [relatorios, setRelatorios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [downloading, setDownloading] = useState(null);
  const [alertMsg, setAlertMsg] = useState(null);
  const [revertTarget, setRevertTarget] = useState(null);

  const fetchRelatorios = useCallback(async () => {
    setLoading(true);
    try {
      const res = await relatoriosAPI.list();
      setRelatorios(res.data || []);
    } catch {
      setError('Erro ao carregar relatórios.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchRelatorios();
  }, [fetchRelatorios]);

  const download = async (relatorio) => {
    setDownloading(relatorio.id);
    try {
      const res = await relatoriosAPI.downloadPdf(relatorio.id);
      const blob = new Blob([res.data], { type: 'application/pdf' });
      const url = URL.createObjectURL(blob);
      const disposition = res.headers?.['content-disposition'] || '';
      const match = disposition.match(/filename="?(.+?)"?$/);
      const filename = match?.[1] || `relatorio-${relatorio.ano}-${String(relatorio.mes).padStart(2, '0')}.pdf`;
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      setAlertMsg(err.response?.data?.detail || 'Erro ao baixar PDF.');
    } finally {
      setDownloading(null);
    }
  };

  const handleConfirmRevert = async () => {
    if (!revertTarget) return;
    try {
      await relatoriosAPI.reverter(revertTarget.id);
      await fetchRelatorios();
    } catch (err) {
      setAlertMsg(err.response?.data?.detail || 'Erro ao reverter o fechamento.');
    } finally {
      setRevertTarget(null);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-white">Relatórios</h1>
        <p className="text-sm text-gray-400 mt-1">Relatórios fechados por mês</p>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-accent-pink/10 border border-accent-pink/30 text-accent-pink text-sm">
          {error}
        </div>
      )}

      {loading ? (
        <Loading />
      ) : relatorios.length === 0 ? (
        <div className="text-center py-16">
          <DocumentTextIcon className="w-12 h-12 mx-auto text-gray-600 mb-3" />
          <p className="text-gray-500">Nenhum relatório fechado ainda.</p>
          <Link to="/fechamento" className="text-sm text-accent-green hover:underline">
            Fazer o fechamento mensal
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {relatorios.map((r) => (
            <div
              key={r.id}
              className="glass-card rounded-xl p-4 border border-primary-700/50 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4"
            >
              <div>
                <Link
                  to={`/relatorios/${r.id}`}
                  className="text-sm font-medium text-white hover:text-accent-green"
                >
                  {r.cliente_nome} — {meses[r.mes - 1]} / {r.ano}
                  {r.numero > 1 ? ` (fechamento ${r.numero})` : ''}
                </Link>
                <p className="text-xs text-gray-500 mt-1">
                  Fechado em {formatDateBR(r.data_fechamento?.slice(0, 10))}
                </p>
                <p className="text-xs text-gray-400 mt-1">
                  <span className="font-mono text-accent-green">{formatHoras(r.total_horas)}h</span>
                  {' · '}
                  <span className="font-mono text-accent-pinkLight">{formatMoeda(r.total_valor)}</span>
                </p>
              </div>
              <button
                onClick={() => download(r)}
                disabled={downloading === r.id}
                className="btn-primary flex items-center gap-2 text-sm self-start disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ArrowDownTrayIcon className="w-4 h-4" />
                {downloading === r.id ? 'Baixando...' : 'Baixar PDF'}
              </button>
              <button
                onClick={() => setRevertTarget(r)}
                className="btn-secondary flex items-center gap-2 text-sm self-start"
                title="Reverter fechamento"
              >
                <ArrowUturnLeftIcon className="w-4 h-4" />
                Reverter
              </button>
            </div>
          ))}
        </div>
      )}

      <ConfirmModal
        isOpen={!!revertTarget}
        title="Reverter fechamento"
        message={`O relatório de ${revertTarget?.cliente_nome} — ${revertTarget ? meses[revertTarget.mes - 1] : ''} / ${revertTarget?.ano} será excluído e as tarefas voltarão para o status Pronta, podendo ser fechadas novamente.`}
        confirmLabel="Reverter"
        onCancel={() => setRevertTarget(null)}
        onConfirm={handleConfirmRevert}
      />

      <AlertModal
        isOpen={!!alertMsg}
        title="Erro"
        message={alertMsg}
        onClose={() => setAlertMsg(null)}
      />
    </div>
  );
}
