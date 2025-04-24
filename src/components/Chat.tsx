
import React, { useRef, useState, useEffect } from "react";
import ChatMessage from "./ChatMessage";
import { Send, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "@/hooks/use-toast";

type Message = { 
  sender: "user" | "agent" | "system"; 
  content: string; 
  loading?: boolean;
};

const API_BASE = "http://localhost:8000";

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed || loading) return;
    
    // Add user message
    setMessages((prev) => [
      ...prev,
      { sender: "user", content: trimmed }
    ]);
    setLoading(true);
    setInput("");

    // Add loading message
    setMessages((prev) => [
      ...prev,
      { sender: "agent", content: "", loading: true }
    ]);

    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: trimmed }),
      });
      if (!res.ok) throw new Error("Network error");
      const data = await res.json();
      
      // Replace loading message with actual response
      setMessages((prev) => [
        ...prev.slice(0, -1),
        { sender: "agent", content: data.response || "" }
      ]);
    } catch (err) {
      // Replace loading message with error message
      setMessages((prev) => [
        ...prev.slice(0, -1),
        {
          sender: "system",
          content: "Error: Unable to fetch a response."
        }
      ]);
      toast({
        title: "Network error",
        description:
          "Could not connect to chat API. Please try again.",
        variant: "destructive"
      });
    }
    setLoading(false);
  };

  const handleInputKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
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
        duration: 1500  // Shorter toast duration
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

  return (
    <div className="flex flex-col h-[100dvh] bg-white">
      <div className="flex items-center justify-between bg-deep-purple-600 px-4 py-3 border-b border-white sticky top-0 z-10 shadow-sm">
        <div className="font-semibold text-lg text-white">Chat</div>
        <Button
          onClick={handleReset}
          variant="outline"
          size="sm"
          className="flex items-center gap-1 text-white hover:text-white hover:bg-white/10 transition-all duration-300 ease-in-out transform hover:scale-105"
          disabled={loading}
        >
          <RefreshCw size={16} /> Reset Chat
        </Button>
      </div>

      <div className="flex-1 overflow-auto px-4 py-6 space-y-3">
        {messages.length === 0 && !loading && (
          <div className="text-center text-deep-purple-600 mt-12">
            Start your conversation!
          </div>
        )}
        {messages.map((msg, i) => (
          <ChatMessage
            key={i}
            sender={msg.sender}
            content={msg.content}
            loading={msg.loading}
          />
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="bg-deep-purple-600 border-t border-white px-4 py-4 sticky bottom-0 shadow-[0_-1px_3px_rgba(0,0,0,0.05)]">
        <div className="flex gap-2 items-center max-w-4xl mx-auto">
          <Input
            className="flex-1 bg-white border-white focus-visible:ring-white text-deep-purple-600 transition-all duration-300 hover:shadow-hover-elevation"
            placeholder="Type a message..."
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleInputKeyDown}
            disabled={loading}
            autoFocus
            maxLength={1000}
          />
          <Button
            onClick={handleSend}
            disabled={!input.trim() || loading}
            className="bg-white hover:bg-white/90 text-deep-purple-600 flex gap-1 items-center transition-all duration-300 ease-in-out transform hover:scale-105 active:scale-95"
          >
            <Send size={18} /> Send
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Chat;
