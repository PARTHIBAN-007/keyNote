import React from "react";

const Modal = ({ open, onClose, children }) => {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-30">
      <div className="bg-white rounded-lg shadow-xl p-8 min-w-[400px] max-w-2xl relative max-h-[85vh] overflow-y-auto border border-slate-200">
        <button
          className="absolute top-4 right-4 text-slate-400 hover:text-red-600 text-2xl font-bold transition hover:bg-red-50 rounded-full w-8 h-8 flex items-center justify-center"
          onClick={onClose}
          title="Close"
        >
          ✕
        </button>
        {children}
      </div>
    </div>
  );
};

export default Modal;
