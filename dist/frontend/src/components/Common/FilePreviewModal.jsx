import React, { useEffect, useState } from 'react';
import { uploadAPI } from '../../services/api';
import Modal from './Modal';
import {
  ArrowDownTrayIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';

const IMAGE_EXTS = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'bmp', 'ico'];

function classify(filename) {
  const ext = filename.toLowerCase().split('.').pop();
  if (IMAGE_EXTS.includes(ext)) return 'image';
  if (ext === 'pdf') return 'pdf';
  return 'other';
}

export default function FilePreviewModal({ tarefaId, filename, isOpen, onClose }) {
  const [blobUrl, setBlobUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const kind = filename ? classify(filename) : 'other';

  useEffect(() => {
    if (!isOpen || !filename) return undefined;
    let active = true;
    let createdUrl = null;
    setLoading(true);
    setError(null);
    setBlobUrl(null);
    uploadAPI
      .download(tarefaId, filename)
      .then((res) => {
        if (!active) return;
        const url = URL.createObjectURL(res.data);
        createdUrl = url;
        setBlobUrl(url);
      })
      .catch(() => {
        if (active) setError('Não foi possível carregar o arquivo.');
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
      if (createdUrl) URL.revokeObjectURL(createdUrl);
    };
  }, [isOpen, tarefaId, filename]);

  const handleDownload = () => {
    if (!blobUrl) return;
    const a = document.createElement('a');
    a.href = blobUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={filename} size="max-w-4xl">
      {loading && (
        <div className="text-center py-12 text-gray-400 text-sm">Carregando…</div>
      )}
      {error && (
        <div className="flex items-center gap-2 text-accent-pink text-sm">
          <ExclamationTriangleIcon className="w-5 h-5" />
          {error}
        </div>
      )}
      {!loading && !error && blobUrl && kind === 'image' && (
        <div className="flex items-center justify-center bg-primary-900/50 rounded-lg overflow-hidden">
          <img
            src={blobUrl}
            alt={filename}
            className="max-h-[70vh] max-w-full object-contain"
          />
        </div>
      )}
      {!loading && !error && blobUrl && kind === 'pdf' && (
        <iframe
          src={blobUrl}
          title={filename}
          className="w-full h-[70vh] rounded-lg border border-primary-700/50 bg-white"
        />
      )}
      {!loading && !error && blobUrl && kind === 'other' && (
        <div className="text-center py-12 space-y-4">
          <p className="text-gray-400 text-sm">
            Pré-visualização não disponível para este tipo de arquivo.
          </p>
        </div>
      )}
      {!loading && !error && blobUrl && (
        <div className="mt-4 flex justify-end">
          <button
            onClick={handleDownload}
            className="btn-secondary inline-flex items-center gap-2 text-xs"
          >
            <ArrowDownTrayIcon className="w-4 h-4" />
            Baixar
          </button>
        </div>
      )}
    </Modal>
  );
}
