
import React, { useState, useEffect } from "react";
import ChatMessage from "./ChatMessage";
import { useToast } from "@/hooks/use-toast";
import { Send, RefreshCw } from "lucide-react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

const API_BASE = "/api";

const ChatView = () => {
  const [messages, setMessages] = useState<Array<{ sender: "user" | "agent" | "system", content: string }>>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();
  const queryClient = useQueryClient();

  // Listen for context changes via query param
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const contextId = urlParams.get('context');
    
    if (contextId) {
      loadContext(contextId);
    }
  }, []);

  const loadContext = async (id: string) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/load-context`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id }),
      });
      
      if (!res.ok) throw new Error("Failed to load context");
      
      const data = await res.json();
      setMessages(data.chat_history || []);
      
    } catch (error) {
      console.error("Error loading context:", error);
      toast({
        title: "Error",
        description: "Failed to load the conversation",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

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
        duration: 1500
      });
      queryClient.invalidateQueries({ queryKey: ["contexts"] });
    } catch (error) {
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
      const res = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMessage }),
      });

      if (!res.ok) throw new Error(`API error: ${res.status}`);

      const data = await res.json();
      setMessages(prev => prev.filter(msg => !msg.loading));
      setMessages(prev => [...prev, { 
        sender: "agent", 
        content: data.response || "No response received."
      }]);
      queryClient.invalidateQueries({ queryKey: ["contexts"] });
    } catch (error) {
      console.error("Error sending message:", error);
      setMessages(prev => prev.filter(msg => !msg.loading));
      setMessages(prev => [...prev, { 
        sender: "agent", 
        content: "Sorry, there was an error processing your request."
      }]);
      toast({
        title: "Error",
        description: "Failed to send message",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-white text-black">
      {/* Header */}
      <div className="bg-black p-4 text-white shadow-md">
        <div className="flex justify-between items-center">
          <h1 className="text-xl font-bold">Chat</h1>
          <button
            onClick={handleReset}
            className="bg-white text-black px-3 py-1 rounded-md flex items-center gap-2 hover:bg-gray-200 transition-all duration-300 shadow-sm hover:shadow-md"
            disabled={loading}
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} /> Reset
          </button>
        </div>
      </div>
      
      {/* Messages Area */}
      <div className="flex-1 p-4 overflow-y-auto bg-white">
        {messages.length === 0 ? (
          <div className="text-center text-gray-600 mt-8">
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
      <div className="bg-black p-4">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="flex-1 px-4 py-2 rounded-md border border-gray-300 focus:outline-none focus:ring-2 focus:ring-black transition-all duration-300"
            placeholder="Type a message..."
            disabled={loading}
          />
          <button
            type="submit"
            className="bg-white text-black px-4 py-2 rounded-md hover:bg-gray-100 transition-all duration-300 shadow-sm hover:shadow-md flex items-center gap-2"
            disabled={loading || !input.trim()}
          >
            <Send className="w-4 h-4" /> Send
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatView;
