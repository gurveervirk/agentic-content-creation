
import React from "react";
import { cn } from "@/lib/utils";
import { marked } from "marked";

// Enable HTML in markdown
marked.setOptions({
  gfm: true,
  breaks: true,
  headerIds: false,
  mangle: false
});

// Simple XSS mitigation
function sanitize(text: string) {
  const doc = new DOMParser().parseFromString(text, "text/html");
  return doc.body.innerHTML;
}

type Props = {
  sender: "user" | "agent" | "system";
  content: string;
};

const ChatMessage: React.FC<Props> = ({ sender, content }) => {
  const isUser = sender === "user";
  const isAgent = sender === "agent";
  
  const bg = isUser
    ? "bg-purple-600 text-white"
    : isAgent
      ? "bg-white text-gray-900 border border-purple-100"
      : "bg-yellow-100 text-yellow-800";

  // For agent, render HTML + markdown. For user, render as-is.
  let messageBody;
  if (isAgent) {
    const html = marked(content);
    messageBody = (
      <div
        className="prose prose-sm max-w-none prose-p:my-1 prose-headings:my-2 [&>:first-child]:mt-0 [&>:last-child]:mb-0"
        dangerouslySetInnerHTML={{ __html: sanitize(html) }}
      />
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
