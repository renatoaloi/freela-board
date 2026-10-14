import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { dashboardAPI } from '../../services/api';
import Loading from '../Common/Loading';
import { formatDateBR } from '../../utils/date';
import {
  InboxArrowDownIcon,
  ArrowPathIcon,
  CheckCircleIcon,
  LockClosedIcon,
  ClockIcon,
  TrophyIcon,
  StarIcon,
} from '@heroicons/react/24/outline';

const statusConfig = {
  nova: { label: 'Nova', icon: InboxArrowDownIcon, color: 'blue', gradient: 'from-blue-500/20 to-blue-500/5' },
  em_andamento: { label: 'Em Andamento', icon: ArrowPathIcon, color: 'yellow', gradient: 'from-yellow-500/20 to-yellow-500/5' },
  pronta: { label: 'Pronta', icon: CheckCircleIcon, color: 'green', gradient: 'from-accent-green/20 to-accent-green/5' },
  fechada: { label: 'Fechada', icon: LockClosedIcon, color: 'gray', gradient: 'from-gray-500/20 to-gray-500/5' },
};

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await dashboardAPI.get();
        setData(res.data);
      } catch (err) {
        setError('Erro ao carregar dados do dashboard.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <Loading />;
  if (error) return <div className="text-center py-20 text-accent-pink">{error}</div>;

  const { tarefas_por_status, horas_por_cliente, melhores_clientes, melhores_projetos, ultimos_projetos } = data || {};

  const maxHoras = horas_por_cliente && horas_por_cliente.length > 0
    ? Math.max(...horas_por_cliente.map((h) => h.total_horas || 0))
    : 1;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Dashboard</h1>
        <p className="text-sm text-gray-400 mt-1">Visão geral do seu negócio</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {Object.entries(statusConfig).map(([key, cfg]) => {
          const Icon = cfg.icon;
          const count = (tarefas_por_status && tarefas_por_status[key]) || 0;
          const colorMap = {
            blue: { text: 'text-blue-400', bg: 'bg-blue-500/10', border: 'border-blue-500/30' },
            yellow: { text: 'text-yellow-400', bg: 'bg-yellow-500/10', border: 'border-yellow-500/30' },
            green: { text: 'text-accent-green', bg: 'bg-accent-green/10', border: 'border-accent-green/30' },
            gray: { text: 'text-gray-400', bg: 'bg-gray-500/10', border: 'border-gray-500/30' },
          };
          const cc = colorMap[cfg.color];
          return (
            <div
              key={key}
              className={`glass-card rounded-xl p-5 ${cc.border} bg-gradient-to-br ${cfg.gradient}`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-3xl font-bold text-white">{count}</p>
                  <p className={`text-sm font-medium mt-1 ${cc.text}`}>{cfg.label}</p>
                </div>
                <div className={`p-3 rounded-lg ${cc.bg}`}>
                  <Icon className={`w-6 h-6 ${cc.text}`} />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {horas_por_cliente && horas_por_cliente.length > 0 && (
        <div className="glass-card rounded-xl p-6 border border-primary-700/50">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <ClockIcon className="w-5 h-5 text-accent-cyan" />
            Horas por Cliente (últimos 6 meses)
          </h2>
          <div className="space-y-3">
            {horas_por_cliente.map((item, i) => {
              const pct = maxHoras > 0 ? ((item.total_horas || 0) / maxHoras) * 100 : 0;
              return (
                <div key={i} className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-300">{item.cliente_nome || item.cliente_id}</span>
                    <span className="text-accent-cyan font-mono font-medium">
                      {Number(item.total_horas || 0).toFixed(1)}h
                    </span>
                  </div>
                  <div className="w-full h-2 bg-primary-800 rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-500"
                      style={{
                        width: `${Math.min(pct, 100)}%`,
                        background: 'linear-gradient(90deg, #00ffab, #00e5ff)',
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {melhores_clientes && melhores_clientes.length > 0 && (
          <div className="glass-card rounded-xl p-6 border border-primary-700/50">
            <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <TrophyIcon className="w-5 h-5 text-yellow-400" />
              Melhores Clientes
            </h2>
            <div className="space-y-3">
              {melhores_clientes.map((c, i) => (
                <div
                  key={c.cliente_id || i}
                  className="flex items-center justify-between px-4 py-3 bg-primary-800/50 rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                      i === 0 ? 'bg-yellow-500/20 text-yellow-400' :
                      i === 1 ? 'bg-gray-400/20 text-gray-300' :
                      i === 2 ? 'bg-orange-500/20 text-orange-400' :
                      'bg-primary-700 text-gray-500'
                    }`}>
                      {i + 1}
                    </span>
                    <span className="text-sm text-gray-200">{c.cliente_nome}</span>
                  </div>
                  <span className="text-sm text-accent-green font-medium">
                    {Number(c.total_horas || 0).toFixed(1)}h
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {melhores_projetos && melhores_projetos.length > 0 && (
          <div className="glass-card rounded-xl p-6 border border-primary-700/50">
            <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <StarIcon className="w-5 h-5 text-accent-pink" />
              Melhores Projetos
            </h2>
            <div className="space-y-3">
              {melhores_projetos.map((p, i) => (
                <div
                  key={p.projeto_id || i}
                  className="flex items-center justify-between px-4 py-3 bg-primary-800/50 rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                      i === 0 ? 'bg-yellow-500/20 text-yellow-400' :
                      i === 1 ? 'bg-gray-400/20 text-gray-300' :
                      i === 2 ? 'bg-orange-500/20 text-orange-400' :
                      'bg-primary-700 text-gray-500'
                    }`}>
                      {i + 1}
                    </span>
                    <span className="text-sm text-gray-200">{p.projeto_titulo}</span>
                  </div>
                  <span className="text-sm text-accent-pinkLight font-medium">
                    {Number(p.total_horas || 0).toFixed(1)}h
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {ultimos_projetos && ultimos_projetos.length > 0 && (
        <div className="glass-card rounded-xl p-6 border border-primary-700/50">
          <h2 className="text-lg font-semibold text-white mb-4">Últimos Projetos</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {ultimos_projetos.map((p) => (
              <div
                key={p.id}
                onClick={() => navigate(`/kanban?projeto=${encodeURIComponent(p.id)}&cliente=${encodeURIComponent(p.cliente_id)}`)}
                className="glass-card rounded-xl p-4 border border-primary-700/50 cursor-pointer hover:border-accent-green/30 hover:bg-gradient-card transition-all duration-200"
              >
                <h3 className="font-medium text-white mb-1 truncate">{p.titulo}</h3>
                <p className="text-xs text-gray-500">{p.cliente_nome || 'Sem cliente'}</p>
                <p className="text-xs text-gray-600 mt-2">
                  {p.data_criacao ? formatDateBR(p.data_criacao) : ''}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {!tarefas_por_status && !horas_por_cliente && (
        <div className="text-center py-16">
          <p className="text-gray-500">Nenhum dado disponível no dashboard.</p>
        </div>
      )}
    </div>
  );
}
