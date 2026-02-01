import React, { useState, useRef, useEffect } from "react";

const ChatWindow = ({ event }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [showSidebar, setShowSidebar] = useState(true);
  const [showTranscription, setShowTranscription] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userPrompt = input; 
    setInput(""); 

    // 1. Add user message
    setMessages((prev) => [...prev, { role: "user", content: userPrompt }]);
    
    // 2. Add placeholder for assistant message
    setMessages((prev) => [...prev, { role: "assistant", content: "" }]);
    
    setLoading(true);

    try {
      // 3. Prepare context
      const eventContext = `
Event: ${event.event_name}
Organizer: ${event.organizer}
Chief Guest: ${event.chief_guest_name}
${event.venue ? `Venue: ${event.venue}` : ""}
Start: ${new Date(event.start_time).toLocaleString()}
End: ${new Date(event.end_time).toLocaleString()}
${event.transcription ? `Transcription: ${event.transcription}` : ""}
      `.trim();

      const fullPrompt = `Context: ${eventContext}\n\nQuestion: ${userPrompt}`;

      // ---------------------------------------------------------
      // Append prompt to URL because backend expects Query Param
      // ---------------------------------------------------------
      const url = `http://localhost:8000/stream/groq?prompt=${encodeURIComponent(fullPrompt)}`;

      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) throw new Error("Failed to connect to AI");

      // 4. Read the SSE stream
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let fullResponse = "";
      let buffer = "";

      setLoading(false);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        // Decode incoming chunk
        buffer += decoder.decode(value, { stream: true });

        // Parse SSE events (format: "data: {...}\n\n")
        const events = buffer.split("\n\n");
        
        // Keep the last incomplete event in buffer
        buffer = events.pop() || "";

        // Process complete events
        events.forEach((event) => {
          if (event.startsWith("data: ")) {
            try {
              const jsonStr = event.replace("data: ", "").trim();
              const data = JSON.parse(jsonStr);

              if (data.chunk) {
                // Accumulate chunk
                fullResponse += data.chunk;

                // Update the last message with the new chunk
                setMessages((prev) => {
                  const newMessages = [...prev];
                  const lastMsgIndex = newMessages.length - 1;
                  newMessages[lastMsgIndex] = {
                    ...newMessages[lastMsgIndex],
                    content: fullResponse,
                  };
                  return newMessages;
                });
              } else if (data.done && data.answer) {
                // Final answer received
                fullResponse = data.answer;
                setMessages((prev) => {
                  const newMessages = [...prev];
                  const lastMsgIndex = newMessages.length - 1;
                  newMessages[lastMsgIndex] = {
                    ...newMessages[lastMsgIndex],
                    content: fullResponse,
                  };
                  return newMessages;
                });
              } else if (data.error) {
                // Error occurred
                throw new Error(data.error);
              }
            } catch (parseError) {
              console.error("Error parsing SSE event:", parseError);
            }
          }
        });
      }

      // Handle any remaining data in buffer
      if (buffer.trim().startsWith("data: ")) {
        try {
          const jsonStr = buffer.replace("data: ", "").trim();
          const data = JSON.parse(jsonStr);
          if (data.answer) {
            fullResponse = data.answer;
            setMessages((prev) => {
              const newMessages = [...prev];
              const lastMsgIndex = newMessages.length - 1;
              newMessages[lastMsgIndex] = {
                ...newMessages[lastMsgIndex],
                content: fullResponse,
              };
              return newMessages;
            });
          }
        } catch (parseError) {
          console.error("Error parsing final SSE event:", parseError);
        }
      }

    } catch (error) {
      console.error("Error sending message:", error);
      setLoading(false);
      setMessages((prev) => {
        const newMessages = [...prev];
        newMessages[newMessages.length - 1] = {
            role: "assistant",
            content: `Sorry, I encountered an error: ${error.message}`
        };
        return newMessages;
      });
    }
  };

  return (
    <div className="flex h-full bg-white">
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header with Sidebar Toggle */}
        <div className="flex items-center gap-2 p-3 border-b border-slate-200 bg-slate-50">
          <button
            onClick={() => setShowSidebar(!showSidebar)}
            className="p-2 hover:bg-slate-200 rounded-lg transition"
            title={showSidebar ? "Hide event details" : "Show event details"}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <h3 className="text-sm font-semibold text-slate-700">Chat Assistant</h3>
        </div>

        {/* Messages Area */}
        <div 
          className="flex-1 bg-slate-50 overflow-y-auto overflow-x-hidden border-b border-slate-200 p-4 space-y-3" 
          style={{ minHeight: 0 }}
        >
          {messages.length === 0 ? (
            <div className="text-slate-500 text-center flex items-center justify-center h-full">
               <p className="text-sm">Start asking questions about <strong>{event?.event_name}</strong></p>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                <div className={`max-w-3xl px-4 py-3 rounded-lg text-sm whitespace-pre-wrap break-words ${
                    msg.role === "user"
                      ? "bg-blue-600 text-white rounded-br-none"
                      : "bg-white text-slate-900 border border-slate-200 rounded-bl-none shadow-sm"
                  }`}>
                  {msg.content}
                </div>
              </div>
            ))
          )}
          
          {/* Loading Dots (Only visible before first chunk arrives) */}
          {loading && (
            <div className="flex justify-start">
               <div className="bg-white px-4 py-3 rounded-lg rounded-bl-none border border-slate-200">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce delay-150"></div>
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce delay-300"></div>
                  </div>
               </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <form onSubmit={sendMessage} className="flex gap-2 p-4 bg-white border-t border-slate-200">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question..."
            disabled={loading}
            className="flex-1 px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-slate-300"
          >
            Send
          </button>
        </form>
      </div>

      {/* Right Sidebar - Event Details & Transcriptions */}
      {showSidebar && (
        <div className="w-80 border-l border-slate-200 bg-white flex flex-col overflow-hidden">
          {/* Sidebar Header */}
          <div className="p-4 border-b border-slate-200 bg-slate-50">
            <h3 className="font-semibold text-slate-900 text-sm">Event Details</h3>
          </div>

          {/* Scrollable Content */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {/* Event Metadata */}
            <div className="space-y-3">
              <div>
                <div className="text-xs font-semibold text-slate-500 uppercase">Event Name</div>
                <div className="text-sm text-slate-900 font-medium">{event.event_name}</div>
              </div>
              <div>
                <div className="text-xs font-semibold text-slate-500 uppercase">Organizer</div>
                <div className="text-sm text-slate-700">{event.organizer}</div>
              </div>
              <div>
                <div className="text-xs font-semibold text-slate-500 uppercase">Chief Guest</div>
                <div className="text-sm text-slate-700">{event.chief_guest_name}</div>
              </div>
              {event.venue && (
                <div>
                  <div className="text-xs font-semibold text-slate-500 uppercase">Venue</div>
                  <div className="text-sm bg-blue-50 px-2 py-1 rounded text-blue-900 font-medium inline-block">
                    {event.venue}
                  </div>
                </div>
              )}
              <div>
                <div className="text-xs font-semibold text-slate-500 uppercase">Start Time</div>
                <div className="text-sm text-slate-700">{new Date(event.start_time).toLocaleString()}</div>
              </div>
              <div>
                <div className="text-xs font-semibold text-slate-500 uppercase">End Time</div>
                <div className="text-sm text-slate-700">{new Date(event.end_time).toLocaleString()}</div>
              </div>
            </div>

            {/* Transcription Section */}
            {event.transcription && (
              <div className="border-t border-slate-200 pt-4">
                <button
                  onClick={() => setShowTranscription(!showTranscription)}
                  className="w-full flex items-center justify-between p-3 bg-blue-50 hover:bg-blue-100 rounded-lg transition"
                >
                  <span className="text-sm font-semibold text-blue-900">📋 Transcriptions</span>
                  <svg 
                    className={`w-4 h-4 text-blue-600 transition ${showTranscription ? 'rotate-180' : ''}`}
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                  </svg>
                </button>

                {/* Transcription Content */}
                {showTranscription && (
                  <div className="mt-3 space-y-2">
                    {event.transcription.split('---').map((transcript, idx) => (
                      transcript.trim() && (
                        <div 
                          key={idx}
                          className="bg-blue-50 rounded p-3 border border-blue-200"
                        >
                          {idx > 0 && (
                            <div className="text-xs text-blue-600 font-semibold mb-2">
                              Transcript {idx}
                            </div>
                          )}
                          <div className="text-xs text-slate-700 leading-relaxed max-h-32 overflow-y-auto">
                            {transcript.trim()}
                          </div>
                        </div>
                      )
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Sidebar Footer */}
          <div className="border-t border-slate-200 p-3 bg-slate-50">
            <button
              onClick={() => setShowSidebar(false)}
              className="w-full px-3 py-2 text-sm text-slate-600 hover:text-slate-900 rounded transition"
            >
              Hide Sidebar
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatWindow;