import React from 'react';
import Modal from './Modal';

export default function ConfirmModal({
  isOpen,
  onCancel,
  onConfirm,
  title = 'Confirmar',
  message = 'Tem certeza que deseja continuar?',
  confirmLabel = 'Confirmar',
}) {
  return (
    <Modal isOpen={isOpen} onClose={onCancel} title={title} size="max-w-md">
      <p className="text-sm text-gray-300">{message}</p>
      <div className="flex items-center justify-end gap-3 pt-6">
        <button type="button" onClick={onCancel} className="btn-secondary">
          Cancelar
        </button>
        <button type="button" onClick={onConfirm} className="btn-danger">
          {confirmLabel}
        </button>
      </div>
    </Modal>
  );
}
