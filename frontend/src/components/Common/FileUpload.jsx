import React, { useState, useRef } from 'react';
import { uploadAPI } from '../../services/api';
import { TrashIcon, PaperClipIcon, ArrowUpTrayIcon } from '@heroicons/react/24/outline';
import FilePreviewModal from './FilePreviewModal';

export default function FileUpload({ tarefaId, anexos = [], onChange }) {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [dragOver, setDragOver] = useState(false);
  const [previewFile, setPreviewFile] = useState(null);
  const fileInputRef = useRef(null);

  const handleUpload = async (file) => {
    if (!file) return;
    setUploading(true);
    setProgress(0);
    try {
      await uploadAPI.upload(tarefaId, file, (e) => {
        const pct = Math.round((e.loaded * 100) / e.total);
        setProgress(pct);
      });
      if (onChange) await onChange();
    } catch {
      alert('Erro ao fazer upload do arquivo.');
    } finally {
      setUploading(false);
      setProgress(0);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleUpload(file);
  };

  const handleDelete = async (filename) => {
    if (!confirm('Excluir este arquivo?')) return;
    try {
      await uploadAPI.delete(tarefaId, filename);
      if (onChange) await onChange();
    } catch {
      alert('Erro ao excluir arquivo.');
    }
  };

  return (
    <div className="space-y-4">
      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all duration-200 ${
          dragOver
            ? 'border-accent-cyan bg-accent-cyan/5'
            : 'border-primary-600 hover:border-primary-500 bg-primary-800/30'
        }`}
      >
        <ArrowUpTrayIcon className="w-8 h-8 mx-auto mb-2 text-gray-500" />
        <p className="text-sm text-gray-400">
          Arraste um arquivo aqui ou clique para selecionar
        </p>
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          onChange={(e) => {
            if (e.target.files[0]) handleUpload(e.target.files[0]);
            e.target.value = '';
          }}
        />
      </div>

      {uploading && (
        <div className="space-y-1">
          <div className="flex justify-between text-xs text-gray-400">
            <span>Enviando...</span>
            <span>{progress}%</span>
          </div>
          <div className="w-full h-1.5 bg-primary-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-accent-green rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {anexos.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-gray-300 flex items-center gap-2">
            <PaperClipIcon className="w-4 h-4" />
            Arquivos ({anexos.length})
          </h4>
          <div className="grid gap-2">
            {anexos.map((filename) => (
              <div
                key={filename}
                className="flex items-center justify-between px-4 py-2.5 bg-primary-800/50 rounded-lg border border-primary-700/50"
              >
                <div className="flex items-center gap-3 min-w-0">
                  <PaperClipIcon className="w-4 h-4 text-gray-500 flex-shrink-0" />
                  <button
                    type="button"
                    onClick={() => setPreviewFile(filename)}
                    className="text-sm text-accent-cyan hover:underline truncate text-left"
                  >
                    {filename}
                  </button>
                </div>
                <button
                  onClick={() => handleDelete(filename)}
                  className="p-1.5 text-gray-500 hover:text-accent-pink transition-colors flex-shrink-0"
                  title="Excluir"
                >
                  <TrashIcon className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      <FilePreviewModal
        tarefaId={tarefaId}
        filename={previewFile}
        isOpen={!!previewFile}
        onClose={() => setPreviewFile(null)}
      />
    </div>
  );
}
