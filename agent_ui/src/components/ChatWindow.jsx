import React, { useState, useRef, useEffect } from "react";

const ChatWindow = ({ event }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
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
Start: ${new Date(event.start_time).toLocaleString()}
End: ${new Date(event.end_time).toLocaleString()}
${event.transcription ? `Transcription: ${event.transcription}` : ""}
      `.trim();

      const fullPrompt = `Context: ${eventContext}\n\nQuestion: ${userPrompt}`;

      // ---------------------------------------------------------
      // FIX: Append prompt to URL because backend expects Query Param
      // ---------------------------------------------------------
      const url = `http://localhost:8000/stream?prompt=${encodeURIComponent(fullPrompt)}`;

      const response = await fetch(url, {
        method: "POST", // Method is still POST
        headers: {
          "Content-Type": "application/json",
        },
        // Body is removed because prompt is now in the URL
      });

      if (!response.ok) throw new Error("Failed to connect to AI");

      // 4. Read the stream
      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      setLoading(false); 

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });

        // Update the last message
        setMessages((prev) => {
          const newMessages = [...prev];
          const lastMsgIndex = newMessages.length - 1;
          newMessages[lastMsgIndex] = {
            ...newMessages[lastMsgIndex],
            content: newMessages[lastMsgIndex].content + chunk,
          };
          return newMessages;
        });
      }

    } catch (error) {
      console.error("Error sending message:", error);
      setLoading(false);
      setMessages((prev) => {
        const newMessages = [...prev];
        newMessages[newMessages.length - 1] = {
            role: "assistant",
            content: "Sorry, I encountered an error. Please try again."
        };
        return newMessages;
      });
    }
  };

  return (
    <div className="w-full h-full flex flex-col">
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
  );
};

export default ChatWindow;