import React, { useState } from "react";

const VENUE_OPTIONS = ["A Block", "E Block", "D Block", "Others"];

const EventForm = ({ onSubmit, onCancel, initialData, eventId }) => {
  const [form, setForm] = useState(initialData || {
    event_name: "",
    organizer: "",
    chief_guest_name: "",
    venue: "",
    start_time: "",
    end_time: "",
  });
  const [loading, setLoading] = useState(false);
  const [audioFile, setAudioFile] = useState(null);
  const [transcribing, setTranscribing] = useState(false);
  const [transcriptionStatus, setTranscriptionStatus] = useState(null); // null | "uploading" | "processing" | "completed" | "error"
  const [transcriptionMessage, setTranscriptionMessage] = useState("");
  const [processedAudios, setProcessedAudios] = useState([]); // Track completed transcriptions

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleAudioChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setAudioFile(file);
    }
  };

  const handleTranscribe = async () => {
    if (!audioFile) {
      alert("Please select an audio file first");
      return;
    }

    if (!eventId) {
      alert("Event must be saved first before transcribing");
      return;
    }

    setTranscribing(true);
    setTranscriptionStatus("uploading");
    setTranscriptionMessage(" Uploading audio to Azure...");

    try {
      const formData = new FormData();
      formData.append("audio_file", audioFile);

      // Stage 1: Upload & Submit Transcription Job
      console.log("Starting transcription process for:", audioFile.name);
      const response = await fetch(
        `http://localhost:8000/events/${eventId}/transcribe`,
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Transcription failed");
      }

      const result = await response.json();
      console.log("Transcription result:", result);

      // Stage 2: Audio Processed - Now Polling
      setTranscriptionStatus("processing");
      setTranscriptionMessage(`✅ Audio Processed & Stored | 🔄 Transcription in Progress...`);
      
      // Add to processed audios list
      const audioRecord = {
        name: audioFile.name,
        timestamp: new Date().toLocaleTimeString(),
        status: "processing"
      };
      setProcessedAudios(prev => [...prev, audioRecord]);

      setAudioFile(null);
      
      // Reset file input
      const fileInput = document.querySelector('input[type="file"]');
      if (fileInput) fileInput.value = "";

      // Stage 3: Wait for transcription completion (Backend handles polling)
      // The backend endpoint is synchronous and blocks until transcription is complete
      // Since the response came back successfully, transcription is DONE
      
      setTranscriptionStatus("completed");
      setTranscriptionMessage(`✅ Transcription Completed Successfully!`);
      
      // Update the processed audios list
      setProcessedAudios(prev => prev.map(audio => 
        audio.name === audioFile.name 
          ? { ...audio, status: "completed" }
          : audio
      ));

      console.log("Transcription process completed:", {
        fileName: audioFile.name,
        transcriptionLength: result.transcription_length,
        preview: result.transcription_preview
      });

    } catch (error) {
      console.error("Transcription error:", error);
      setTranscriptionStatus("error");
      setTranscriptionMessage(`❌ Error: ${error.message}`);
      
      // Update the processed audios list
      setProcessedAudios(prev => prev.map(audio => 
        audio.name === audioFile.name 
          ? { ...audio, status: "error" }
          : audio
      ));
    } finally {
      setTranscribing(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    await onSubmit(form);
    setLoading(false);
  };

  // Determine status badge appearance
  const getStatusBadge = () => {
    switch(transcriptionStatus) {
      case "uploading":
        return {
          bg: "bg-blue-100",
          border: "border-blue-300",
          text: "text-blue-900",
          icon: "📤"
        };
      case "processing":
        return {
          bg: "bg-yellow-100",
          border: "border-yellow-300",
          text: "text-yellow-900",
          icon: "🔄"
        };
      case "completed":
        return {
          bg: "bg-green-100",
          border: "border-green-300",
          text: "text-green-900",
          icon: "✅"
        };
      case "error":
        return {
          bg: "bg-red-100",
          border: "border-red-300",
          text: "text-red-900",
          icon: "❌"
        };
      default:
        return null;
    }
  };

  const statusBadge = getStatusBadge();

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
      <div>
        <label className="block text-sm font-semibold text-slate-700 mb-2">Venue</label>
        <select 
          name="venue" 
          value={form.venue} 
          onChange={handleChange}
          className="w-full border border-slate-300 rounded-lg p-3 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
        >
          <option value="">-- Select a venue --</option>
          {VENUE_OPTIONS.map(option => (
            <option key={option} value={option}>{option}</option>
          ))}
        </select>
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

      {/* Audio Upload Section */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <label className="block text-sm font-semibold text-slate-700 mb-3">Upload Audio for Transcription</label>
        <div className="space-y-3">
          <div className="flex items-center gap-3">
            <input 
              type="file" 
              accept="audio/*"
              onChange={handleAudioChange}
              disabled={transcribing}
              className="flex-1 text-sm text-slate-700 file:rounded-lg file:border-0 file:bg-blue-600 file:text-white file:font-semibold file:px-4 file:py-2 file:cursor-pointer hover:file:bg-blue-700"
            />
            <button
              type="button"
              onClick={handleTranscribe}
              disabled={!audioFile || transcribing}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
            >
              {transcribing ? "Processing..." : "Transcribe"}
            </button>
          </div>

      {/* Current Transcription Status Badge */}
          {transcriptionStatus && statusBadge && (
            <div className={`p-3 rounded-lg border-2 ${statusBadge.bg} ${statusBadge.border} ${statusBadge.text} font-semibold flex items-center gap-2 ${transcriptionStatus === 'processing' ? 'animate-pulse' : ''}`}>
              <span className="text-lg">{statusBadge.icon}</span>
              <div className="flex-1">
                <span>{transcriptionMessage}</span>
                {transcriptionStatus === 'processing' && (
                  <div className="text-xs font-normal mt-1 opacity-80">
                    Processing audio through Azure Speech Service (polling every 10 seconds)...
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Selected File Display */}
          {audioFile && !transcribing && (
            <div className="text-sm text-blue-700 flex items-center gap-2">
              <span>📁</span>
              <span>Selected: <strong>{audioFile.name}</strong></span>
            </div>
          )}

          {/* Processed Audios History */}
          {processedAudios.length > 0 && (
            <div className="border-t border-blue-200 pt-3 mt-3">
              <div className="text-xs font-semibold text-slate-600 mb-2">📋 Processing History:</div>
              <div className="space-y-2">
                {processedAudios.map((audio, idx) => (
                  <div 
                    key={idx}
                    className={`text-xs p-2 rounded flex items-center justify-between ${
                      audio.status === "completed"
                        ? "bg-green-50 text-green-700 border border-green-200"
                        : "bg-yellow-50 text-yellow-700 border border-yellow-200"
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <span>{audio.status === "completed" ? "✅" : "⏳"}</span>
                      <span className="font-medium">{audio.name}</span>
                    </div>
                    <div className="flex flex-col items-end">
                      <span>{audio.timestamp}</span>
                      <span className="text-xs font-semibold">
                        {audio.status === "completed" ? "Transcription Completed" : "In Progress"}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
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
          disabled={loading || transcribing} 
          className="px-6 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-semibold transition disabled:opacity-50"
        >
          {loading ? "Saving..." : "Save Event"}
        </button>
      </div>
    </form>
  );
};

export default EventForm;
