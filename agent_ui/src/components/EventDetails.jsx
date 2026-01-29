import React from "react";

// Helper function to format event times properly (handles timezone-aware ISO strings)
function formatEventDateTime(isoString) {
  // Example: "2026-01-20T15:30:00+05:30"
  const dateStr = isoString.split('T')[0];
  const timePart = isoString.split('T')[1].substring(0, 5); // Get HH:MM
  
  const date = new Date(dateStr + 'T00:00:00');
  const dateFormatted = date.toLocaleDateString('en-IN', { 
    weekday: 'short', 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric'
  });
  
  // Format time as HH:MM
  return `${dateFormatted} ${timePart}`;
}

const EventDetails = ({ event, onBack, onChat, onEdit, onDelete }) => {
  if (!event) return null;
  
  const handleDelete = async () => {
    if (window.confirm(`Are you sure you want to delete "${event.event_name}"?`)) {
      await onDelete(event.id || event.event_id);
    }
  };
  
  return (
    <div className="space-y-4">
      <button onClick={onBack} className="text-blue-600 hover:text-blue-800 font-semibold text-sm flex items-center gap-1">
        ← Back to Events
      </button>
      <h2 className="text-2xl font-bold text-slate-800 mb-4">{event.event_name}</h2>
      <div className="bg-slate-50 rounded-lg p-4 space-y-3 border border-slate-200">
        <div className="flex items-start gap-3">
          <div>
            <div className="font-semibold text-slate-700">Organizer</div>
            <div className="text-slate-700">{event.organizer}</div>
          </div>
        </div>
        <div className="flex items-start gap-3">
          <div>
            <div className="font-semibold text-slate-700">Chief Guest</div>
            <div className="text-slate-700">{event.chief_guest_name}</div>
          </div>
        </div>
        <div className="flex items-start gap-3">
          <div>
            <div className="font-semibold text-slate-700">Start Time</div>
            <div className="text-slate-700">{formatEventDateTime(event.start_time)}</div>
          </div>
        </div>
        <div className="flex items-start gap-3">
          <div>
            <div className="font-semibold text-slate-700">End Time</div>
            <div className="text-slate-700">{formatEventDateTime(event.end_time)}</div>
          </div>
        </div>
        {event.transcription && (
          <div className="flex items-start gap-3">
            <div>
              <div className="font-semibold text-slate-700">Transcription</div>
              <div className="text-slate-700 whitespace-pre-line bg-white rounded p-2 mt-1 border border-slate-200">{event.transcription}</div>
            </div>
          </div>
        )}
      </div>
      
      <div className="flex gap-2 mt-4">
        <button 
          onClick={onChat} 
          title="Chat with AI"
          className="p-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition shadow"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        </button>
        <button 
          onClick={onEdit} 
          title="Edit Event"
          className="p-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition shadow"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
        </button>
        <button 
          onClick={handleDelete} 
          title="Delete Event"
          className="p-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition shadow"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      </div>
    </div>
  );
};

export default EventDetails;
