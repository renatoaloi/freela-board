import React, { useEffect, useCallback } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';

export default function Modal({ isOpen, onClose, title, children, size = 'max-w-2xl' }) {
  const handleKeyDown = useCallback(
    (e) => {
      if (e.key === 'Escape') onClose();
    },
    [onClose],
  );

  useEffect(() => {
    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'hidden';
    }
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = '';
    };
  }, [isOpen, handleKeyDown]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div
        className="absolute inset-0 bg-black/70 backdrop-blur-sm"
        onClick={onClose}
      />
      <div
        className={`relative w-full ${size} max-h-[90vh] glass-card rounded-2xl overflow-hidden`}
      >
        <div className="flex items-center justify-between px-6 py-4 border-b border-primary-700/50">
          <h2 className="text-lg font-semibold text-white">{title}</h2>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-primary-700 transition-colors"
            aria-label="Close"
          >
            <XMarkIcon className="w-5 h-5" />
          </button>
        </div>
        <div className="overflow-y-auto p-6" style={{ maxHeight: 'calc(90vh - 73px)' }}>
          {children}
        </div>
      </div>
    </div>
  );
}
