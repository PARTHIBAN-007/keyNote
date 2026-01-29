import React from "react";

const Layout = ({ children }) => {
  return (
    <div className="min-h-screen bg-white flex flex-col">
      <header className="bg-white shadow-sm border-b border-blue-200 p-5">
        <div className="max-w-full mx-auto">
          <h1 className="text-3xl font-bold text-blue-900 tracking-wide">
            KeyNote AI
          </h1>
          <p className="text-blue-700 text-sm mt-1">Event Management & AI Assistant</p>
        </div>
      </header>
      <main className="flex flex-1 overflow-hidden w-full bg-slate-50">
        {children}
      </main>
    </div>
  );
};

export default Layout;
