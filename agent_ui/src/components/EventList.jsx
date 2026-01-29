import React from "react";

function formatEventDateTime(isoString) {
  const dateStr = isoString.split('T')[0];
  const timePart = isoString.split('T')[1].substring(0, 5);
  
  const date = new Date(dateStr + 'T00:00:00');
  const dateFormatted = date.toLocaleDateString('en-IN', { 
    weekday: 'short', 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric'
  });
  
  return `${dateFormatted} ${timePart}`;
}

const EventList = ({ events, onSelectEvent }) => {
  return (
    <div className="h-full overflow-y-auto p-6 flex flex-col bg-white">
      <h2 className="text-2xl font-bold text-slate-800 mb-6 sticky top-0 bg-white py-2">Events ({events.length})</h2>
      {events.length === 0 ? (
        <div className="text-slate-400 text-center py-16 flex-1 flex items-center justify-center flex-col">
          <p className="text-lg text-slate-600">No events scheduled yet</p>
          <p className="text-sm text-slate-400 mt-2">Create your first event using the calendar</p>
        </div>
      ) : (
        <ul className="space-y-3 flex-1">
          {events.map((event) => (
            <li
              key={event.id || event.event_id || event.created_at}
              className="bg-white rounded-lg shadow border border-slate-200 p-4 cursor-pointer hover:shadow-md hover:border-blue-300 transition-all duration-200 border-l-4 border-blue-500 group"
              onClick={() => onSelectEvent(event)}
            >
              <div className="font-bold text-slate-800 text-lg group-hover:text-blue-600 transition">{event.event_name}</div>
              <div className="text-sm text-slate-600 mt-2">
                <span className="font-semibold">Start:</span> {formatEventDateTime(event.start_time)}
              </div>
              <div className="text-sm text-slate-600 mt-1">
                <span className="font-semibold">End:</span> {formatEventDateTime(event.end_time)}
              </div>
              <div className="text-sm text-slate-600 mt-1">
                <span className="font-semibold">Organizer:</span> {event.organizer}
              </div>
              <div className="text-sm text-slate-600 mt-1">
                <span className="font-semibold">Guest:</span> {event.chief_guest_name}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default EventList;
