import React, { useState, useEffect, useRef } from "react";
import ChatMessage from "./ChatMessage";
import { useToast } from "@/hooks/use-toast";
import { Send, RefreshCw } from "lucide-react";
import { useQueryClient } from "@tanstack/react-query";
import { useSidebar } from "@/components/ui/sidebar";

const API_BASE = "/api";

// Create a shared event bus for direct component communication
const eventBus = {
  listeners: new Map(),
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
    return () => this.off(event, callback);
  },
  off(event, callback) {
    if (!this.listeners.has(event)) return;
    const callbacks = this.listeners.get(event);
    const index = callbacks.indexOf(callback);
    if (index !== -1) callbacks.splice(index, 1);
  },
  emit(event, data) {
    if (!this.listeners.has(event)) return;
    this.listeners.get(event).forEach(callback => callback(data));
  }
};

// Export the event bus for other components to use
export { eventBus };

const ChatView = () => {
  const [messages, setMessages] = useState<Array<{ sender: "user" | "agent", content: string, loading?: boolean }>>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { openMobile, setOpenMobile } = useSidebar();

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Listen for events from other components
  useEffect(() => {
    // Handle new chat (clear messages)
    const newChatHandler = () => {
      console.log("New chat event received, clearing messages");
      setMessages([]);
    };
    
    // Handle load context
    const loadContextHandler = (id: string) => {
      console.log("Load context event received:", id);
      loadContext(id);
    };

    // Subscribe to events
    const unsubscribeNewChat = eventBus.on('new-chat', newChatHandler);
    const unsubscribeLoadContext = eventBus.on('load-context', loadContextHandler);

    // Check URL params on mount
    const urlParams = new URLSearchParams(window.location.search);
    const contextId = urlParams.get('context');
    
    if (contextId) {
      loadContext(contextId);
    }

    // Cleanup subscriptions on unmount
    return () => {
      unsubscribeNewChat();
      unsubscribeLoadContext();
    };
  }, []);

  const loadContext = async (id: string) => {
    setLoading(true);
    try {
      // Using URLSearchParams to format the query parameters correctly
      const res = await fetch(`${API_BASE}/load-context?id=${encodeURIComponent(id)}`, {
        method: "POST",
      });
      
      if (!res.ok) throw new Error("Failed to load context");
      
      const data = await res.json();
      
      // Parse the chat_history array from the response
      if (data.chat_history && Array.isArray(data.chat_history)) {
        // Even indices (0, 2, 4...) are user messages, odd indices (1, 3, 5...) are agent messages
        const formattedMessages = data.chat_history.map((content: string, index: number) => ({
          sender: index % 2 === 0 ? "user" : "agent" as "user" | "agent",
          content
        }));
        setMessages(formattedMessages);
      } else {
        setMessages([]);
        console.warn("No chat history found in response:", data);
      }
      
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
      
      // Clear messages immediately
      setMessages([]);
      
      toast({
        title: "Chat reset",
        description: data?.message || "Workflow reset successfully.",
        duration: 1500
      });
      
      // Clear URL and invalidate contexts
      window.history.pushState({}, "", "/");
      queryClient.invalidateQueries({ queryKey: ["contexts"] });
      
      // Notify other components
      eventBus.emit('chat-reset', null);
      
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
    
    // Close mobile sidebar if open
    if (openMobile) {
      setOpenMobile(false);
    }
    
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
    <div className="flex flex-col h-full bg-white text-black relative">
      {/* Header */}
      <div className="bg-black p-4 text-white shadow-md">
        <div className="flex justify-between items-center">
          <h1 className="text-xl font-bold ml-8 md:ml-0">Chat</h1>
          <button
            onClick={handleReset}
            className="bg-white text-black px-3 py-1 rounded-md flex items-center gap-2 hover:bg-gray-200 transition-all duration-300 shadow-sm hover:shadow-md"
            disabled={loading}
            aria-label="Reset conversation"
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
          <>
            {messages.map((message, index) => (
              <ChatMessage
                key={index}
                sender={message.sender}
                content={message.content}
                loading={message.loading}
              />
            ))}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>
      
      {/* Input Area */}
      <div className="bg-black p-4 sticky bottom-0 z-10">
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
