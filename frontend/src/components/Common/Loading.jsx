import React from 'react';

export default function Loading({ message = 'Carregando...' }) {
  return (
    <div className="flex flex-col items-center justify-center py-20">
      <div className="relative w-12 h-12">
        <div className="absolute inset-0 border-4 border-primary-700 rounded-full" />
        <div className="absolute inset-0 border-4 border-transparent border-t-accent-green rounded-full animate-spin" />
      </div>
      <p className="mt-4 text-sm text-gray-400">{message}</p>
    </div>
  );
}
