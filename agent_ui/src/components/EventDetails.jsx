import React from "react";

const EventDetails = ({ event, onBack, onChat, onEdit, onDelete }) => {
  if (!event) return null;
  
  const handleDelete = async () => {
    if (window.confirm(`Are you sure you want to delete "${event.event_name}"?`)) {
      await onDelete(event.id || event.event_id);
    }
  };
  
  return (
    <div className="space-y-4">
      <button onClick={onBack} className="text-indigo-600 hover:text-indigo-800 font-semibold text-sm flex items-center gap-1">
        ← Back to Events
      </button>
      <h2 className="text-2xl font-bold text-slate-900 mb-4">{event.event_name}</h2>
      <div className="bg-slate-50 rounded-lg p-4 space-y-3 border border-slate-200">
        <div className="flex items-start gap-3">
          <div>
            <div className="font-semibold text-slate-700">Organizer</div>
            <div className="text-slate-600">{event.organizer}</div>
          </div>
        </div>
        <div className="flex items-start gap-3">
          <div>
            <div className="font-semibold text-slate-700">Chief Guest</div>
            <div className="text-slate-600">{event.chief_guest_name}</div>
          </div>
        </div>
        <div className="flex items-start gap-3">
          <div>
            <div className="font-semibold text-slate-700">Start Time</div>
            <div className="text-slate-600">{new Date(event.start_time).toLocaleString()}</div>
          </div>
        </div>
        <div className="flex items-start gap-3">
          <div>
            <div className="font-semibold text-slate-700">End Time</div>
            <div className="text-slate-600">{new Date(event.end_time).toLocaleString()}</div>
          </div>
        </div>
        {event.transcription && (
          <div className="flex items-start gap-3">
            <div>
              <div className="font-semibold text-slate-700">Transcription</div>
              <div className="text-slate-600 whitespace-pre-line bg-white rounded p-2 mt-1 border border-slate-200">{event.transcription}</div>
            </div>
          </div>
        )}
      </div>
      
      <div className="flex gap-2 mt-4">
        <button 
          onClick={onChat} 
          title="Ask AI"
          className="flex-1 flex items-center justify-center px-4 py-3 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 font-semibold transition shadow text-xl"
        >
          🤖
        </button>
        <button 
          onClick={onEdit} 
          title="Edit Event"
          className="flex-1 flex items-center justify-center px-4 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-semibold transition shadow text-xl"
        >
          ✏️
        </button>
        <button 
          onClick={handleDelete} 
          title="Delete Event"
          className="flex-1 flex items-center justify-center px-4 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 font-semibold transition shadow text-xl"
        >
          🗑️
        </button>
      </div>
    </div>
  );
};

export default EventDetails;
