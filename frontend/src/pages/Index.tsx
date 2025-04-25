
import { SidebarProvider } from "@/components/ui/sidebar";
import ChatView from "@/components/ChatView";
import ChatSidebar from "@/components/ChatSidebar";

const Index = () => {
  return (
    <SidebarProvider>
      <div className="flex min-h-screen w-full bg-white">
        <ChatSidebar />
        <div className="flex-1 flex flex-col">
          <ChatView />
        </div>
      </div>
    </SidebarProvider>
  );
};

export default Index;
