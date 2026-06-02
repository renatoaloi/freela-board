import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { tarefasAPI, apontamentosAPI, uploadAPI } from '../../services/api';
import Loading from '../Common/Loading';
import TarefaForm from './TarefaForm';
import ApontamentoForm from '../Apontamentos/ApontamentoForm';
import FileUpload from '../Common/FileUpload';
import FilePreviewModal from '../Common/FilePreviewModal';
import {
  ArrowLeftIcon,
  PencilSquareIcon,
  ClockIcon,
  PaperClipIcon,
  TrashIcon,
} from '@heroicons/react/24/outline';

const statusBadge = {
  nova: 'status-nova',
  em_andamento: 'status-em_andamento',
  pronta: 'status-pronta',
  fechada: 'status-fechada',
};

const statusLabels = {
  nova: 'Nova',
  em_andamento: 'Em Andamento',
  pronta: 'Pronta',
  fechada: 'Fechada',
};

const COVER_IMAGE_EXTS = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'bmp', 'ico'];

function formatHoras(horas) {
  if (!horas && horas !== 0) return '0h 0m';
  const h = Math.floor(horas);
  const m = Math.round((horas - h) * 60);
  return `${h}h ${m}m`;
}

function pickCoverImage(anexos) {
  if (!anexos) return null;
  return anexos.find((fn) => {
    const ext = fn.toLowerCase().split('.').pop();
    return COVER_IMAGE_EXTS.includes(ext);
  }) || null;
}

function TaskCover({ tarefaId, filename, onOpen }) {
  const [blobUrl, setBlobUrl] = useState(null);

  useEffect(() => {
    if (!filename) return undefined;
    let active = true;
    let created = null;
    uploadAPI
      .download(tarefaId, filename)
      .then((res) => {
        if (!active) return;
        const url = URL.createObjectURL(res.data);
        created = url;
        setBlobUrl(url);
      })
      .catch(() => {
        if (active) setBlobUrl(null);
      });
    return () => {
      active = false;
      if (created) URL.revokeObjectURL(created);
    };
  }, [tarefaId, filename]);

  if (!filename || !blobUrl) return null;
  return (
    <button
      type="button"
      onClick={() => onOpen(filename)}
      className="block w-full rounded-xl overflow-hidden border border-primary-700/50 bg-primary-800/30 hover:border-accent-cyan/50 transition-colors"
      title="Abrir capa"
    >
      <img
        src={blobUrl}
        alt="capa da tarefa"
        className="w-full max-h-64 object-cover"
      />
    </button>
  );
}

export default function TarefaDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [tarefa, setTarefa] = useState(null);
  const [apontamentos, setApontamentos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [formOpen, setFormOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('apontamentos');
  const [coverModalFile, setCoverModalFile] = useState(null);

  const fetchTarefa = useCallback(async () => {
    try {
      const res = await tarefasAPI.get(id);
      setTarefa(res.data);
    } catch {
      setError('Erro ao carregar tarefa.');
    }
  }, [id]);

  const fetchApontamentos = useCallback(async () => {
    try {
      const res = await apontamentosAPI.listByTarefa(id);
      setApontamentos(res.data || []);
    } catch {}
  }, [id]);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      await fetchTarefa();
      await fetchApontamentos();
      setLoading(false);
    };
    load();
  }, [fetchTarefa, fetchApontamentos]);

  const handleDeleteApontamento = async (apId) => {
    if (!confirm('Excluir este apontamento?')) return;
    try {
      await apontamentosAPI.delete(apId);
      await fetchApontamentos();
    } catch {
      alert('Erro ao excluir apontamento.');
    }
  };

  const totalHoras = apontamentos.reduce((sum, a) => sum + (a.total_horas || 0), 0);

  if (loading) return <Loading />;
  if (error) return <div className="text-center py-20 text-accent-pink">{error}</div>;
  if (!tarefa) return <div className="text-center py-20 text-gray-500">Tarefa não encontrada.</div>;

  const coverImage = pickCoverImage(tarefa.anexos);

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-colors"
      >
        <ArrowLeftIcon className="w-4 h-4" />
        Voltar
      </button>

      <TaskCover
        tarefaId={id}
        filename={coverImage}
        onOpen={setCoverModalFile}
      />

      <div className="glass-card rounded-xl p-6 border border-primary-700/50">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-3 flex-wrap">
              <h1 className="text-xl font-bold text-white">{tarefa.titulo}</h1>
              <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${statusBadge[tarefa.status] || 'status-nova'}`}>
                {statusLabels[tarefa.status] || tarefa.status}
              </span>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Criada em {tarefa.data_criacao ? new Date(tarefa.data_criacao).toLocaleDateString('pt-BR') : '—'}
            </p>
          </div>
          <button
            onClick={() => setFormOpen(true)}
            className="btn-icon text-gray-400 hover:text-accent-cyan"
            title="Editar tarefa"
          >
            <PencilSquareIcon className="w-5 h-5" />
          </button>
        </div>

        {tarefa.descricao && (
          <div className="mt-5 pt-5 border-t border-primary-700/50 prose prose-invert prose-sm max-w-none">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{tarefa.descricao}</ReactMarkdown>
          </div>
        )}
      </div>

      <div className="flex gap-1 border-b border-primary-700/50">
        {['apontamentos', 'anexos'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ${
              activeTab === tab
                ? 'text-accent-cyan border-accent-cyan'
                : 'text-gray-500 border-transparent hover:text-gray-300'
            }`}
          >
            {tab === 'apontamentos' ? 'Apontamentos' : 'Anexos'}
          </button>
        ))}
      </div>

      {activeTab === 'apontamentos' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-gray-300 flex items-center gap-2">
              <ClockIcon className="w-4 h-4" />
              Registros de Horas
            </h3>
            <span className="text-sm font-mono text-accent-green font-medium">
              Total: {formatHoras(totalHoras)}
            </span>
          </div>

          <ApontamentoForm tarefaId={id} onSave={fetchApontamentos} />

          {apontamentos.length === 0 ? (
            <div className="text-center py-8 text-gray-600 text-sm">
              Nenhum apontamento registrado.
            </div>
          ) : (
            <div className="space-y-2">
              {apontamentos.map((ap) => (
                <div
                  key={ap.id}
                  className="flex items-center justify-between px-4 py-3 bg-primary-800/50 rounded-lg border border-primary-700/50"
                >
                  <div className="flex items-center gap-4 text-sm">
                    <span className="text-gray-200">
                      {ap.data ? new Date(ap.data).toLocaleDateString('pt-BR') : '—'}
                    </span>
                    <span className="font-mono text-gray-400">
                      {ap.hora_ini ? ap.hora_ini.substring(0, 5) : '--:--'}
                    </span>
                    <span className="text-gray-600">→</span>
                    <span className="font-mono text-gray-400">
                      {ap.hora_fim ? ap.hora_fim.substring(0, 5) : '--:--'}
                    </span>
                    <span className="font-mono text-accent-green font-medium">
                      {formatHoras(ap.total_horas)}
                    </span>
                  </div>
                  <button
                    onClick={() => handleDeleteApontamento(ap.id)}
                    className="p-1.5 text-gray-500 hover:text-accent-pink transition-colors"
                    title="Excluir"
                  >
                    <TrashIcon className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'anexos' && (
        <div className="space-y-4">
          <h3 className="text-sm font-medium text-gray-300 flex items-center gap-2">
            <PaperClipIcon className="w-4 h-4" />
            Anexos
          </h3>
          <FileUpload tarefaId={id} anexos={tarefa.anexos || []} onChange={fetchTarefa} />
        </div>
      )}

      <TarefaForm
        isOpen={formOpen}
        onClose={() => setFormOpen(false)}
        onSave={() => { setFormOpen(false); fetchTarefa(); }}
        tarefa={tarefa}
      />

      <FilePreviewModal
        tarefaId={id}
        filename={coverModalFile}
        isOpen={!!coverModalFile}
        onClose={() => setCoverModalFile(null)}
      />
    </div>
  );
}
