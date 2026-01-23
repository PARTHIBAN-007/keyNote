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

    // Add user message to chat
    const userMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      // Prepare context from event
      const eventContext = `
Event: ${event.event_name}
Organizer: ${event.organizer}
Chief Guest: ${event.chief_guest_name}
Start: ${new Date(event.start_time).toLocaleString()}
End: ${new Date(event.end_time).toLocaleString()}
${event.transcription ? `Transcription: ${event.transcription}` : ""}
      `.trim();

      const prompt = `Context: ${eventContext}\n\nQuestion: ${input}`;

      // Add placeholder for assistant message
      const aiMessage = { role: "assistant", content: "" };
      setMessages((prev) => [...prev, aiMessage]);

      // Call the backend /stream endpoint
      const response = await fetch(`http://localhost:8000/stream?prompt=${encodeURIComponent(prompt)}`);

      if (!response.ok) {
        throw new Error("Failed to get response from AI");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let fullResponse = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const text = decoder.decode(value, { stream: true });
        const lines = text.split("\n");

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.chunk && data.chunk.response) {
                fullResponse += data.chunk.response;
                // Update the last message with accumulated text
                setMessages((prev) => {
                  const newMessages = [...prev];
                  newMessages[newMessages.length - 1].content = fullResponse;
                  return newMessages;
                });
              }
            } catch (e) {
              console.error("Failed to parse message:", e);
            }
          }
        }
      }
    } catch (error) {
      console.error("Error sending message:", error);
      const errorMessage = {
        role: "assistant",
        content: `Error: ${error.message}`,
      };
      setMessages((prev) => {
        // Replace the last message if it's empty, otherwise append
        const newMessages = [...prev];
        if (newMessages.length > 0 && newMessages[newMessages.length - 1].role === "assistant" && newMessages[newMessages.length - 1].content === "") {
          newMessages[newMessages.length - 1] = errorMessage;
        } else {
          newMessages.push(errorMessage);
        }
        return newMessages;
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full h-full flex flex-col">
      {/* Chat Messages Container */}
      <div className="flex-1 bg-slate-50 overflow-y-auto overflow-x-hidden border-b border-slate-200 p-4 space-y-3" style={{ minHeight: 0 }}>
        {messages.length === 0 ? (
          <div className="text-slate-500 text-center flex items-center justify-center h-full">
            <div className="text-sm">
              <p className="text-xs text-slate-400">
                Start asking questions about this event
              </p>
            </div>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-3xl px-4 py-3 rounded-lg text-sm whitespace-pre-wrap break-words ${
                  msg.role === "user"
                    ? "bg-indigo-600 text-white rounded-br-none"
                    : "bg-white text-slate-900 border border-slate-200 rounded-bl-none"
                }`}
              >
                {msg.content}
              </div>
            </div>
          ))
        )}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white text-slate-900 border border-slate-200 px-4 py-3 rounded-lg rounded-bl-none">
              <div className="flex items-center gap-2">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }}></div>
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }}></div>
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }}></div>
                </div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <form onSubmit={sendMessage} className="flex gap-2 p-4 bg-white border-t border-slate-200">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your question..."
          disabled={loading}
          className="flex-1 px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:bg-slate-100 disabled:text-slate-500 text-sm"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="px-4 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-slate-400 disabled:cursor-not-allowed transition flex items-center gap-1"
          title="Send message"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </button>
      </form>
    </div>
  );
};

export default ChatWindow;
