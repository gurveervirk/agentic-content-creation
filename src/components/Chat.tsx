
import React, { useState } from "react";
import ChatMessage from "./ChatMessage";
import { useToast } from "@/hooks/use-toast";
import { Send, RefreshCw } from "lucide-react";

// Define API_BASE or use environment variable
const API_BASE = "/api"; // Adjust this as needed for your API endpoint

interface Message {
  sender: "user" | "agent" | "system";
  content: string;
  loading?: boolean;
}

const Chat = () => {
  const [messages, setMessages] = useState<Array<Message>>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const handleReset = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/reset`, { method: "POST" });
      if (!res.ok) throw new Error("Network error");
      const data = await res.json();
      setMessages([]);
      toast({
        title: "Chat reset",
        description: data?.message || "Workflow reset successfully.",
        duration: 1500  // Shortened toast duration
      });
    } catch {
      toast({
        title: "Failed to reset chat",
        variant: "destructive",
        duration: 1500
      });
    }
    setLoading(false);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;
    
    const userMessage = input;
    setInput("");
    setMessages(prev => [...prev, { sender: "user", content: userMessage }]);
    
    setLoading(true);
    setMessages(prev => [...prev, { sender: "agent", content: "Thinking...", loading: true }]);
    
    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage }),
      });
      
      if (!response.ok) {
        throw new Error('API request failed');
      }
      
      const data = await response.json();
      
      // Remove loading message
      setMessages(prev => prev.filter(msg => !msg.loading));
      
      // Add response from API
      setMessages(prev => [...prev, { 
        sender: "agent", 
        content: data.message || "No response from API"
      }]);
    } catch (error) {
      setMessages(prev => prev.filter(msg => !msg.loading));
      setMessages(prev => [...prev, { 
        sender: "agent", 
        content: "Sorry, there was an error processing your request."
      }]);
    }
    setLoading(false);
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="bg-[#7842f5] p-4 text-white shadow-md">
        <div className="flex justify-between items-center">
          <h1 className="text-xl font-bold">Chat</h1>
          <button
            onClick={handleReset}
            className="bg-white text-[#7842f5] px-3 py-1 rounded-md flex items-center gap-2 hover:bg-gray-100 transition-all duration-300 shadow-sm hover:shadow-md"
            disabled={loading}
          >
            <RefreshCw className="w-4 h-4" /> Reset
          </button>
        </div>
      </div>
      
      {/* Messages Area */}
      <div className="flex-1 p-4 overflow-y-auto bg-white">
        {messages.length === 0 ? (
          <div className="text-center text-gray-400 mt-8">
            No messages yet. Start a conversation!
          </div>
        ) : (
          messages.map((message, index) => (
            <ChatMessage
              key={index}
              sender={message.sender}
              content={message.content}
              loading={message.loading}
            />
          ))
        )}
      </div>
      
      {/* Input Area */}
      <div className="bg-[#7842f5] p-4">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="flex-1 px-4 py-2 rounded-md border border-gray-300 focus:outline-none focus:ring-2 focus:ring-[#7842f5] transition-all duration-300"
            placeholder="Type a message..."
            disabled={loading}
          />
          <button
            type="submit"
            className="bg-white text-[#7842f5] px-4 py-2 rounded-md hover:bg-gray-100 transition-all duration-300 shadow-sm hover:shadow-md flex items-center gap-2"
            disabled={loading || !input.trim()}
          >
            <Send className="w-4 h-4" /> Send
          </button>
        </form>
      </div>
    </div>
  );
};

export default Chat;
