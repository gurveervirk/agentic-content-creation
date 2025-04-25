import { useState, useEffect } from "react";
import { useToast } from "@/hooks/use-toast";
import { Sidebar, SidebarContent, SidebarHeader, SidebarGroup, SidebarGroupLabel, SidebarGroupContent, SidebarMenu, SidebarMenuItem, SidebarMenuButton, SidebarTrigger, useSidebar } from "@/components/ui/sidebar";
import { MessageSquare, PlusCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { eventBus } from "./ChatView"; // Import the event bus from ChatView

const API_BASE = "/api";

const ChatSidebar = () => {
  const { toast } = useToast();
  const [activeChat, setActiveChat] = useState<string | null>(null);
  const { setOpenMobile } = useSidebar();
  const queryClient = useQueryClient();

  // Get URL params to check for active context
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const contextParam = urlParams.get('context');
    
    if (contextParam) {
      setActiveChat(contextParam);
    }

    // Listen for chat reset events
    const resetHandler = () => {
      setActiveChat(null);
    };

    const unsubscribe = eventBus.on('chat-reset', resetHandler);
    return () => unsubscribe();
  }, []);
  
  // Fetch contexts
  const { data, isLoading, error } = useQuery({
    queryKey: ["contexts"],
    queryFn: async () => {
      const res = await fetch(`${API_BASE}/get-contexts`);
      if (!res.ok) throw new Error("Failed to fetch contexts");
      const data = await res.json();
      
      try {
        // Parse the contexts from string to object if needed
        const contexts = typeof data.contexts === 'string' 
          ? JSON.parse(data.contexts.replace(/'/g, '"')) 
          : data.contexts;
        
        return Object.entries(contexts || {}).map(([id, title]) => ({
          id,
          title,
        }));
      } catch (error) {
        console.error("Failed to parse contexts:", error);
        return [];
      }
    },
  });

  const loadContext = async (id: string) => {
    try {
      // Emit event to inform ChatView to load this context
      eventBus.emit('load-context', id);
      
      setActiveChat(id);
      setOpenMobile(false); // Close mobile drawer after selection
      
      // Navigate to the context
      window.history.pushState({}, "", `/?context=${id}`);
      
      toast({
        title: "Chat loaded",
        description: "Previous conversation loaded successfully",
      });
    } catch (error) {
      console.error("Error loading context:", error);
      toast({
        title: "Error",
        description: "Failed to load the conversation",
        variant: "destructive",
      });
    }
  };

  const handleNewChat = async () => {
    try {
      // Call the reset endpoint to clear the conversation in the backend
      const res = await fetch(`${API_BASE}/reset`, { method: "POST" });
      if (!res.ok) throw new Error("Failed to reset chat");
      
      // Clear the active chat state and URL parameter
      setActiveChat(null);
      setOpenMobile(false);
      
      // Clear URL query parameters without reloading the page
      window.history.pushState({}, "", '/');
      
      // Trigger immediate UI update in ChatView component
      eventBus.emit('new-chat', null);
      
      // Invalidate contexts query to refresh the sidebar
      queryClient.invalidateQueries({ queryKey: ["contexts"] });
      
      toast({
        title: "New Chat",
        description: "Started a new conversation",
        duration: 1500
      });
    } catch (error) {
      console.error("Error creating new chat:", error);
      toast({
        title: "Error",
        description: "Failed to create a new chat",
        variant: "destructive",
      });
    }
  };

  return (
    <>
      {/* Mobile trigger */}
      <div className="fixed left-4 top-4 z-50 md:hidden">
        <SidebarTrigger className="bg-black text-white hover:bg-gray-800" />
      </div>
      
      <Sidebar collapsible="offcanvas" variant="inset" className="border-r border-gray-200 bg-white w-[260px] max-w-[260px]">
        <SidebarHeader className="border-b border-gray-200 p-4">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <h2 className="text-lg font-bold whitespace-nowrap">Conversations</h2>
            <Button 
              variant="outline" 
              size="sm" 
              className="border-black hover:bg-black hover:text-white transition-all duration-300 whitespace-nowrap"
              onClick={handleNewChat}
            >
              <PlusCircle className="w-4 h-4 mr-1" />
              New Chat
            </Button>
          </div>
        </SidebarHeader>
        <SidebarContent>
          <SidebarGroup>
            <SidebarGroupLabel>Recent Conversations</SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                {isLoading ? (
                  <div className="p-4 text-center text-gray-500">Loading...</div>
                ) : error ? (
                  <div className="p-4 text-center text-red-500">Failed to load conversations</div>
                ) : data && data.length > 0 ? (
                  data.map((context) => (
                    <SidebarMenuItem key={context.id}>
                      <SidebarMenuButton 
                        onClick={() => loadContext(context.id)}
                        className={`transition-all duration-200 ${activeChat === context.id ? 'bg-black text-white' : 'hover:bg-gray-100'}`}
                      >
                        <MessageSquare className="w-4 h-4 min-w-4" />
                        <span className="truncate">{String(context.title)}</span>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  ))
                ) : (
                  <div className="p-4 text-center text-gray-500">No conversations yet</div>
                )}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        </SidebarContent>
      </Sidebar>
    </>
  );
};

export default ChatSidebar;
