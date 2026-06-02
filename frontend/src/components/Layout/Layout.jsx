import React from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";

export default function Layout() {
  return (
    <div className="flex min-h-screen bg-primary-900">
      <Sidebar />
      <main className="flex-1 ml-0 lg:ml-6 min-h-screen transition-all duration-300">
        <div className="p-4 sm:p-6 sm:pl-20 lg:p-8 pt-16 lg:pt-8 max-w-7xl mx-auto">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
