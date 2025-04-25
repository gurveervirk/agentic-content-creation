
import { useState } from "react";
import { useToast } from "@/hooks/use-toast";
import { Sidebar, SidebarContent, SidebarHeader, SidebarGroup, SidebarGroupLabel, SidebarGroupContent, SidebarMenu, SidebarMenuItem, SidebarMenuButton } from "@/components/ui/sidebar";
import { MessageSquare, PlusCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useQuery } from "@tanstack/react-query";

const API_BASE = "/api";

const ChatSidebar = () => {
  const { toast } = useToast();
  const [activeChat, setActiveChat] = useState<string | null>(null);

  // Fetch contexts
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["contexts"],
    queryFn: async () => {
      const res = await fetch(`${API_BASE}/get-contexts`);
      if (!res.ok) throw new Error("Failed to fetch contexts");
      const data = await res.json();
      return Object.entries(data.contexts || {}).map(([title, id]) => ({
        title,
        id: id as string,
      }));
    },
  });

  const loadContext = async (id: string) => {
    try {
      const res = await fetch(`${API_BASE}/load-context`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id }),
      });
      
      if (!res.ok) throw new Error("Failed to load context");
      
      setActiveChat(id);
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

  return (
    <Sidebar variant="inset" className="w-72 border-r border-black">
      <SidebarHeader className="border-b border-black p-4">
        <div className="flex items-center justify-between">
          <h2 className="font-bold text-lg">Conversations</h2>
          <Button 
            variant="outline" 
            size="sm" 
            className="border-black hover:bg-black hover:text-white transition-all duration-300"
            onClick={() => {
              setActiveChat(null);
              window.location.reload();
            }}
          >
            <PlusCircle className="w-4 h-4 mr-2" />
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
                      className={`transition-all duration-200 hover:scale-102 ${activeChat === context.id ? 'bg-black text-white' : ''}`}
                    >
                      <MessageSquare className="w-4 h-4" />
                      <span className="truncate">{context.title}</span>
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
  );
};

export default ChatSidebar;
