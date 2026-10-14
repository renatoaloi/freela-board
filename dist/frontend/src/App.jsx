import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout/Layout';
import Dashboard from './components/Dashboard/Dashboard';
import ClientesList from './components/Clientes/ClientesList';
import ProjetosList from './components/Projetos/ProjetosList';
import Kanban from './components/Kanban/Kanban';
import TarefaDetail from './components/Tarefas/TarefaDetail';
import RelatoriosList from './components/Relatorios/RelatoriosList';
import RelatorioView from './components/Relatorios/RelatorioView';
import FechamentoMensal from './components/Fechamento/FechamentoMensal';
import Configuracoes from './components/Configuracoes/Configuracoes';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="clientes" element={<ClientesList />} />
        <Route path="projetos" element={<ProjetosList />} />
        <Route path="kanban" element={<Kanban />} />
        <Route path="tarefas/:id" element={<TarefaDetail />} />
        <Route path="relatorios" element={<RelatoriosList />} />
        <Route path="relatorios/:id" element={<RelatorioView />} />
        <Route path="fechamento" element={<FechamentoMensal />} />
        <Route path="configuracoes" element={<Configuracoes />} />
      </Route>
    </Routes>
  );
}
