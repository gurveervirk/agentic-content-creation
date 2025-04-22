
import React, { useRef, useState, useEffect } from "react";
import ChatMessage from "./ChatMessage";
import { Send, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "@/hooks/use-toast";

type Message = { sender: "user" | "agent" | "system"; content: string };

const API_BASE = "http://localhost:8000";

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  // Scroll to bottom on new message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed || loading) return;
    // Add user message instantly
    setMessages((prev) => [
      ...prev,
      { sender: "user", content: trimmed }
    ]);
    setLoading(true);
    setInput("");

    // Add loading placeholder
    setMessages((prev) => [
      ...prev,
      { sender: "agent", content: "..." }
    ]);

    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: trimmed }),
      });
      if (!res.ok) throw new Error("Network error");
      const data = await res.json();
      // Remove placeholder, add real agent message
      setMessages((prev) => [
        ...prev.slice(0, -1),
        { sender: "agent", content: data.response || "" },
      ]);
    } catch (err) {
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
      // Toast confirmation
      toast({
        title: "Chat reset",
        description: data?.message || "Workflow reset successfully."
      });
    } catch {
      toast({
        title: "Failed to reset chat",
        variant: "destructive"
      });
    }
    setLoading(false);
  };

  return (
    <div className="flex flex-col h-[100dvh] bg-gray-50">
      {/* Top bar with Reset */}
      <div className="flex items-center justify-between bg-white px-4 py-3 border-b border-gray-200 sticky top-0 z-10">
        <div className="font-semibold text-lg text-gray-700">Chat</div>
        <Button
          onClick={handleReset}
          variant="outline"
          size="sm"
          className="flex items-center gap-1"
          disabled={loading}
        >
          <RefreshCw size={16} /> Reset Chat
        </Button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-auto px-2 py-4">
        {messages.length === 0 && !loading && (
          <div className="text-center text-gray-400 mt-12">
            Start your conversation!
          </div>
        )}
        {messages.map((msg, i) => (
          <ChatMessage
            key={i}
            sender={msg.sender}
            content={msg.content}
          />
        ))}
        {loading && (
          <div ref={messagesEndRef} />
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input box */}
      <div className="bg-white border-t border-gray-200 px-4 py-3 sticky bottom-0">
        <div className="flex gap-2 items-center">
          <Input
            className="flex-1"
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
            variant="default"
            className="flex gap-1 items-center"
          >
            <Send size={18} /> Send
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Chat;

