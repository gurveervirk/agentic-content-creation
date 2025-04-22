
import React from "react";
import { cn } from "@/lib/utils";
import { marked } from "marked";

// Simple XSS mitigation for demo; production apps require better!
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
    ? "bg-primary text-white"
    : isAgent
      ? "bg-gray-200 text-gray-900"
      : "bg-yellow-100 text-yellow-800";

  // For agent, render HTML + markdown. For user, render as-is.
  let messageBody;
  if (isAgent) {
    // Allow HTML AND markdown (marked can parse HTML in markdown)
    const raw = marked.parse(content);
    messageBody = (
      <div
        className="prose prose-sm max-w-none"
        dangerouslySetInnerHTML={{ __html: sanitize(raw) }}
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
          "rounded-xl px-4 py-2 max-w-[75%] shadow",
          bg
        )}
      >
        {messageBody}
      </div>
    </div>
  );
};

export default ChatMessage;

