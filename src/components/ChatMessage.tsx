
import React from "react";
import { cn } from "@/lib/utils";
import { marked } from "marked";
import { Loader2 } from "lucide-react";
import ReactMarkdown from "react-markdown";

// Enable HTML in markdown
marked.setOptions({
  gfm: true,
  breaks: true,
});

// Simple XSS mitigation
function sanitize(text: string) {
  const doc = new DOMParser().parseFromString(text, "text/html");
  return doc.body.innerHTML;
}

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
    ? "bg-purple-50 text-purple-600 border border-purple-100"
    : isUser
      ? "bg-purple-600 text-white"
      : "bg-white text-gray-900 border border-purple-100";

  // Render loading state for agent
  if (isLoading) {
    return (
      <div className="flex justify-start mb-2">
        <div className={cn(
          "rounded-xl px-4 py-2 max-w-[75%] shadow-sm flex items-center gap-2",
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
        className="prose prose-sm max-w-none prose-p:my-1 prose-headings:my-2 [&>:first-child]:mt-0 [&>:last-child]:mb-0"
        components={{
          h1: 'h2',  // Prevent oversized headings
          pre: 'pre',
          code: 'code',
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
        "flex mb-2",
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
