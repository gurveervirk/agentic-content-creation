
import React from "react";
import { cn } from "@/lib/utils";
import ReactMarkdown from "react-markdown";

interface ChatMessageProps {
  sender: "user" | "agent" | "system";
  content: string;
  loading?: boolean;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ sender, content, loading }) => {
  return (
    <div
      className={cn(
        "mb-4 flex",
        sender === "user" ? "justify-end" : "justify-start"
      )}
    >
      <div
        className={cn(
          "max-w-[80%] rounded-lg p-4 shadow-md transition-all duration-300 hover:shadow-lg transform hover:scale-[1.01]",
          sender === "user"
            ? "bg-black text-white"
            : "bg-gray-100 text-black border border-gray-200"
        )}
      >
        <div className="flex items-center mb-1">
          <div
            className={cn(
              "w-2 h-2 rounded-full mr-2",
              sender === "user" ? "bg-white" : "bg-black"
            )}
          ></div>
          <span className="font-medium">
            {sender === "user" ? "You" : sender === "agent" ? "Agent" : "System"}
          </span>
        </div>

        {loading ? (
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-current rounded-full animate-bounce"></div>
            <div className="w-2 h-2 bg-current rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
            <div className="w-2 h-2 bg-current rounded-full animate-bounce" style={{ animationDelay: "0.4s" }}></div>
          </div>
        ) : (
          <ReactMarkdown className="prose prose-sm max-w-none">{content}</ReactMarkdown>
        )}
      </div>
    </div>
  );
};

export default ChatMessage;
