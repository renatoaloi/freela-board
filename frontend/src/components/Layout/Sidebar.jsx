import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { Bars3Icon, XMarkIcon } from '@heroicons/react/24/outline';
import {
  HomeIcon,
  UsersIcon,
  FolderIcon,
  ViewColumnsIcon,
  DocumentTextIcon,
  Cog6ToothIcon,
} from '@heroicons/react/24/outline';

const navItems = [
  { to: '/', icon: HomeIcon, label: 'Dashboard' },
  { to: '/clientes', icon: UsersIcon, label: 'Clientes' },
  { to: '/projetos', icon: FolderIcon, label: 'Projetos' },
  { to: '/kanban', icon: ViewColumnsIcon, label: 'Kanban' },
  { to: '/configuracoes', icon: Cog6ToothIcon, label: 'Configurações' },
  { to: '/relatorios', icon: DocumentTextIcon, label: 'Relatórios' },
];

export default function Sidebar() {
  const [mobileOpen, setMobileOpen] = useState(false);

  const linkClass = ({ isActive }) =>
    `flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${
      isActive
        ? 'bg-accent-green/10 text-accent-green border border-accent-green/30 neon-glow-green'
        : 'text-gray-400 hover:text-gray-200 hover:bg-primary-700/50 border border-transparent'
    }`;

  return (
    <>
      <button
        onClick={() => setMobileOpen(true)}
        className="fixed top-4 left-4 z-50 p-2 rounded-lg bg-primary-800 border border-primary-700 text-gray-200 lg:hidden hover:bg-primary-700 transition-colors"
        aria-label="Open menu"
      >
        <Bars3Icon className="w-6 h-6" />
      </button>

      {mobileOpen && (
        <div
          className="fixed inset-0 bg-black/60 z-40 lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      <aside
        className={`fixed top-0 left-0 z-40 h-full w-64 bg-primary-900 border-r border-primary-700/50 transform transition-transform duration-300 ease-in-out ${
          mobileOpen ? 'translate-x-0' : '-translate-x-full'
        } lg:translate-x-0 lg:static lg:z-auto flex flex-col`}
      >
        <div className="flex items-center justify-between px-6 py-6 border-b border-primary-700/50">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-accent-green to-accent-cyan flex items-center justify-center font-bold text-primary-900 text-lg">
              FB
            </div>
            <div>
              <h1 className="text-lg font-bold text-white">FreelaBoard</h1>
              <p className="text-xs text-gray-500">Gerenciamento</p>
            </div>
          </div>
          <button
            onClick={() => setMobileOpen(false)}
            className="p-1 rounded-lg text-gray-400 hover:text-white hover:bg-primary-700 lg:hidden"
            aria-label="Close menu"
          >
            <XMarkIcon className="w-5 h-5" />
          </button>
        </div>

        <nav className="flex-1 px-3 py-6 space-y-1.5 overflow-y-auto">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              onClick={() => setMobileOpen(false)}
              className={linkClass}
            >
              <item.icon className="w-5 h-5 flex-shrink-0" />
              <span className="text-sm font-medium">{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="px-4 py-4 border-t border-primary-700/50">
          <p className="text-xs text-gray-600 text-center">FreelaBoard v1.0</p>
        </div>
      </aside>
    </>
  );
}
