
import React from "react";
import { cn } from "@/lib/utils";
import { Loader2 } from "lucide-react";
import ReactMarkdown from "react-markdown";

type Props = {
  sender: "user" | "agent" | "system";
  content: string;
  loading?: boolean;
};

const ChatMessage: React.FC<Props> = ({ sender, content, loading = false }) => {
  const isUser = sender === "user";
  const isAgent = sender === "agent";
  const isLoading = loading && isAgent;
  
  const bg = isLoading 
    ? "bg-white text-deep-purple-600 border border-deep-purple-100"
    : isUser
      ? "bg-deep-purple-600 text-white"
      : "bg-white text-deep-purple-600 border border-deep-purple-100";

  // Render loading state for agent
  if (isLoading) {
    return (
      <div className="flex justify-start mb-2">
        <div className={cn(
          "rounded-xl px-4 py-2 max-w-[75%] shadow-sm flex items-center gap-2 transition-all duration-300 ease-in-out transform hover:scale-102 hover:shadow-hover-elevation",
          bg
        )}>
          <Loader2 className="animate-spin w-5 h-5" />
          <span>Thinking...</span>
        </div>
      </div>
    );
  }

  // For agent, render HTML + markdown. For user, render as-is.
  let messageBody;
  if (isAgent) {
    messageBody = (
      <ReactMarkdown 
        components={{
          h1: ({ node, ...props }) => <h2 {...props} />,
          pre: ({ node, ...props }) => <pre {...props} />,
          code: ({ node, ...props }) => <code {...props} />,
        }}
      >
        {content}
      </ReactMarkdown>
    );
  } else {
    messageBody = <span>{content}</span>;
  }

  return (
    <div
      className={cn(
        "flex mb-2 transition-all duration-300 ease-in-out transform hover:scale-102 hover:shadow-hover-elevation",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      <div
        className={cn(
          "rounded-xl px-4 py-2 max-w-[75%] shadow-sm",
          bg
        )}
      >
        {messageBody}
      </div>
    </div>
  );
};

export default ChatMessage;
