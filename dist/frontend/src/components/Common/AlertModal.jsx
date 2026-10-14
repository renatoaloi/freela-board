import React from 'react';
import Modal from './Modal';

export default function AlertModal({
  isOpen,
  onClose,
  title = 'Aviso',
  message = '',
}) {
  return (
    <Modal isOpen={isOpen} onClose={onClose} title={title} size="max-w-md">
      <p className="text-sm text-gray-300">{message}</p>
      <div className="flex items-center justify-end gap-3 pt-6">
        <button type="button" onClick={onClose} className="btn-primary">
          OK
        </button>
      </div>
    </Modal>
  );
}
