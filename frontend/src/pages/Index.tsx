import { SidebarProvider } from "@/components/ui/sidebar";
import ChatView from "@/components/ChatView";
import ChatSidebar from "@/components/ChatSidebar";

const Index = () => {
  return (
    <SidebarProvider defaultOpen={true}>
      <div className="flex min-h-screen w-full overflow-hidden">
        <ChatSidebar />
        <main className="flex-1 flex flex-col bg-white">
          <ChatView />
        </main>
      </div>
    </SidebarProvider>
  );
};

export default Index;
