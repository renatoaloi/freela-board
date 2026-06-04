import React from 'react';
import { Cog6ToothIcon } from '@heroicons/react/24/outline';
import DadosBancariosForm from './DadosBancariosForm';

export default function Configuracoes() {
  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-white">Configurações</h1>
        <p className="text-sm text-gray-400 mt-1">Gerencie suas preferências e dados cadastrais</p>
      </div>

      <DadosBancariosForm />
    </div>
  );
}