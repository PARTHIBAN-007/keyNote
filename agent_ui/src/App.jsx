
import React, { useEffect, useState } from "react";
import Layout from "./components/Layout";
import EventList from "./components/EventList";
import Calendar from "./components/Calendar";
import Modal from "./components/Modal";
import EventForm from "./components/EventForm";
import EventDetails from "./components/EventDetails";
import ChatWindow from "./components/ChatWindow";

const API_URL = "http://localhost:8000/events/";

function groupEventsByDate(events) {
  const map = {};
  events.forEach((event) => {
    const date = new Date(event.start_time);
    const dateStr = date.toISOString().slice(0, 10);
    if (!map[dateStr]) map[dateStr] = [];
    map[dateStr].push(event);
  });
  return map;
}

function App() {
  const [events, setEvents] = useState([]);
  const [selectedDate, setSelectedDate] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [modalType, setModalType] = useState(""); // "view" | "create" | "edit" | "details"
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [loading, setLoading] = useState(false);
  const [chatMode, setChatMode] = useState(false); // Full screen chat mode

  useEffect(() => {
    fetchEvents();
  }, []);

  const fetchEvents = async () => {
    setLoading(true);
    try {
      const res = await fetch(API_URL);
      const data = await res.json();
      setEvents(data);
    } catch (e) {
      console.error("Failed to fetch events", e);
    }
    setLoading(false);
  };

  const handleDateClick = (dateStr) => {
    setSelectedDate(dateStr);
    setModalType("view");
    setShowModal(true);
    setSelectedEvent(null);
  };

  const handleEventClick = (event) => {
    setSelectedEvent(event);
    setModalType("details");
    setShowModal(true);
  };

  const handleCreateEvent = () => {
    setModalType("create");
    setShowModal(true);
    setSelectedEvent(null);
  };

  const handleEditEvent = () => {
    setModalType("edit");
  };

  const handleSaveEvent = async (form) => {
    try {
      if (modalType === "edit" && selectedEvent) {
        // Update existing event
        const eventId = selectedEvent.id || selectedEvent.event_id;
        const res = await fetch(`${API_URL}${eventId}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(form),
        });
        if (!res.ok) throw new Error("Failed to update event");
      } else {
        // Create new event
        const res = await fetch(API_URL, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(form),
        });
        if (!res.ok) throw new Error("Failed to create event");
      }
      setShowModal(false);
      setModalType("");
      setSelectedEvent(null);
      fetchEvents();
    } catch (e) {
      console.error("Failed to save event", e);
      alert("Failed to save event. Please try again.");
    }
  };

  const handleDeleteEvent = async (eventId) => {
    try {
      const res = await fetch(`${API_URL}${eventId}`, {
        method: "DELETE",
      });
      if (!res.ok) throw new Error("Failed to delete event");
      setShowModal(false);
      setModalType("");
      setSelectedEvent(null);
      fetchEvents();
    } catch (e) {
      console.error("Failed to delete event", e);
      alert("Failed to delete event. Please try again.");
    }
  };

  const handleBackToEvents = () => {
    setModalType("view");
    setSelectedEvent(null);
  };

  const handleChatWithAI = () => {
    setChatMode(true);
  };

  const handleExitChat = () => {
    setChatMode(false);
  };

  const eventsByDate = groupEventsByDate(events);
  const eventsForSelectedDate = selectedDate ? eventsByDate[selectedDate] || [] : [];

  return (
    <Layout>
      {/* Full screen chat mode */}
      {chatMode && selectedEvent && (
        <div className="w-full min-h-screen flex flex-col bg-slate-100 overflow-auto">
          {/* Header */}
          <div className="flex items-center gap-3 p-4 border-b border-slate-200 bg-white sticky top-0 z-10">
            <button
              onClick={handleExitChat}
              className="p-2 hover:bg-slate-200 rounded-lg transition"
              title="Back to events"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <div>
              <h2 className="text-lg font-bold text-slate-900">{selectedEvent.event_name}</h2>
              <p className="text-xs text-slate-500">Chat with AI about this event</p>
            </div>
          </div>
          {/* Chat Container - Centered and wider */}
          <div className="flex-1 flex items-center justify-center p-4 overflow-auto">
            <div className="w-full max-w-5xl h-[80vh] bg-white rounded-lg shadow-lg border border-slate-200 overflow-hidden flex flex-col">
              <ChatWindow event={selectedEvent} />
            </div>
          </div>
        </div>
      )}

      {/* Normal event management view */}
      {!chatMode && (
        <>
          <div className="flex w-full h-full gap-4 p-4">
        {/* Event List Section - 3/4 width */}
        <div className="w-3/4 flex flex-col max-h-[calc(100vh-8rem)]">
          <div className="bg-white rounded-lg shadow border border-slate-200 p-5 mb-4 flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-slate-900">Event Calendar</h1>
              <p className="text-slate-600 text-sm mt-1">Manage and track your events</p>
            </div>
            <button
              onClick={handleCreateEvent}
              className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-semibold transition shadow flex items-center gap-2 text-lg"
            >
              ➕ New Event
            </button>
          </div>
          <div className="flex-1 bg-white rounded-lg shadow border border-slate-200 overflow-hidden flex flex-col">
            <EventList events={events} onSelectEvent={handleEventClick} />
          </div>
        </div>

        {/* Calendar Section - 1/4 width - Independent size */}
        <div className="w-1/4 flex flex-col max-h-[calc(100vh-8rem)]">
          <Calendar events={events} onDateClick={handleDateClick} />
        </div>
      </div>

      {/* Modal for date click, event details, create, or edit */}
      <Modal open={showModal} onClose={() => {
        setShowModal(false);
        setModalType("");
        setSelectedEvent(null);
      }}>
        {modalType === "view" && (
          <div>
            <div className="mb-4 pb-4 border-b-2 border-slate-200">
              <h3 className="text-xl font-bold text-slate-900 mb-4">📅 {selectedDate}</h3>
              <button onClick={handleCreateEvent} className="w-full px-4 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-semibold transition flex items-center justify-center gap-2 text-lg">
              ➕ New Event
            </button>
            </div>
            {eventsForSelectedDate.length === 0 ? (
              <div className="text-slate-500 text-center py-8">No events on this date</div>
            ) : (
              <ul className="space-y-2 max-h-96 overflow-y-auto">
                {eventsForSelectedDate.map((event) => (
                  <li 
                    key={event.id || event.event_id || event.created_at} 
                    className="bg-indigo-50 rounded-lg p-3 cursor-pointer hover:bg-indigo-100 transition border-l-4 border-indigo-500" 
                    onClick={() => handleEventClick(event)}
                  >
                    <div className="font-semibold text-slate-900">{event.event_name}</div>
                    <div className="text-xs text-slate-600 mt-1">{new Date(event.start_time).toLocaleTimeString()}</div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
        {modalType === "create" && (
          <div>
            <h3 className="text-xl font-bold text-slate-900 mb-4">✨ Create New Event</h3>
            <EventForm 
              onSubmit={handleSaveEvent} 
              onCancel={() => {
                setShowModal(false);
                setModalType("");
              }}
              initialData={{ 
                start_time: selectedDate ? selectedDate + 'T00:00' : '', 
                end_time: selectedDate ? selectedDate + 'T01:00' : '',
                event_name: "",
                organizer: "",
                chief_guest_name: "",
                transcription: ""
              }} 
            />
          </div>
        )}
        {modalType === "edit" && selectedEvent && (
          <div>
            <h3 className="text-xl font-bold text-slate-900 mb-4">✏️ Edit Event</h3>
            <EventForm 
              onSubmit={handleSaveEvent} 
              onCancel={() => {
                setModalType("details");
              }}
              initialData={{
                event_name: selectedEvent.event_name,
                organizer: selectedEvent.organizer,
                chief_guest_name: selectedEvent.chief_guest_name,
                start_time: selectedEvent.start_time.replace('Z', '').slice(0, 16),
                end_time: selectedEvent.end_time.replace('Z', '').slice(0, 16),
                transcription: selectedEvent.transcription || ""
              }}
            />
          </div>
        )}
        {modalType === "details" && selectedEvent && (
          <EventDetails 
            event={selectedEvent} 
            onBack={handleBackToEvents} 
            onChat={handleChatWithAI}
            onEdit={handleEditEvent}
            onDelete={handleDeleteEvent}
          />
        )}
      </Modal>
        </>
      )}
    </Layout>
  );
}

export default App;
