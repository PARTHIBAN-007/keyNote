import React, { useState } from "react";

const EventForm = ({ onSubmit, onCancel, initialData }) => {
  const [form, setForm] = useState(initialData || {
    event_name: "",
    organizer: "",
    chief_guest_name: "",
    start_time: "",
    end_time: "",
    transcription: "",
  });
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    await onSubmit(form);
    setLoading(false);
  };

  return (
    <form className="space-y-4" onSubmit={handleSubmit}>
      <div>
        <label className="block text-sm font-semibold text-slate-700 mb-2">Event Name *</label>
        <input 
          name="event_name" 
          value={form.event_name} 
          onChange={handleChange} 
          required 
          className="w-full border border-slate-300 rounded-lg p-3 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100" 
          placeholder="Enter event name" 
        />
      </div>
      <div>
        <label className="block text-sm font-semibold text-slate-700 mb-2">Organizer *</label>
        <input 
          name="organizer" 
          value={form.organizer} 
          onChange={handleChange} 
          required 
          className="w-full border border-slate-300 rounded-lg p-3 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100" 
          placeholder="Enter organizer name" 
        />
      </div>
      <div>
        <label className="block text-sm font-semibold text-slate-700 mb-2">Chief Guest Name *</label>
        <input 
          name="chief_guest_name" 
          value={form.chief_guest_name} 
          onChange={handleChange} 
          required 
          className="w-full border border-slate-300 rounded-lg p-3 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100" 
          placeholder="Enter chief guest name" 
        />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-2">Start Time *</label>
          <input 
            type="datetime-local" 
            name="start_time" 
            value={form.start_time} 
            onChange={handleChange} 
            required 
            className="w-full border border-slate-300 rounded-lg p-3 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100" 
          />
        </div>
        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-2">End Time *</label>
          <input 
            type="datetime-local" 
            name="end_time" 
            value={form.end_time} 
            onChange={handleChange} 
            required 
            className="w-full border border-slate-300 rounded-lg p-3 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100" 
          />
        </div>
      </div>
      <div>
        <label className="block text-sm font-semibold text-slate-700 mb-2">Transcription</label>
        <textarea 
          name="transcription" 
          value={form.transcription} 
          onChange={handleChange} 
          className="w-full border border-slate-300 rounded-lg p-3 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100" 
          placeholder="Add transcription notes (optional)" 
          rows="3" 
        />
      </div>
      <div className="flex gap-3 justify-end pt-4 border-t border-slate-200">
        <button 
          type="button" 
          onClick={onCancel} 
          className="px-6 py-2 rounded-lg  border border-slate-300 hover:bg-slate-100 text-slate-700 font-semibold transition"
        >
          Cancel
        </button>
        <button 
          type="submit" 
          disabled={loading} 
          className="px-6 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-semibold transition disabled:opacity-50"
        >
          {loading ? "Saving..." : "Save Event"}
        </button>
      </div>
    </form>
  );
};

export default EventForm;
