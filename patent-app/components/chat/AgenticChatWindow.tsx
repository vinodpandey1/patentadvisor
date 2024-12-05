// components/chat/AgenticChatWindow.tsx

"use client";

import React, { useState, useEffect, FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { getPolarityLabel, getSubjectivityLabel } from "@/lib/utils/sentiment"; // Ensure these utilities are available

interface ChatMessage {
  role: "human" | "ai";
  content: string;
  sentiment?: {
    polarity: number;
    subjectivity: number;
  };
}

interface AgenticChatWindowProps {
  patentId: string;
  userId: string;
  handleAgenticSend: (query: string) => Promise<void>;
  messages: ChatMessage[];
  isLoading: boolean;
}

const AgenticChatWindow: React.FC<AgenticChatWindowProps> = ({
  patentId,
  userId,
  handleAgenticSend,
  messages,
  isLoading,
}) => {
  const [query, setQuery] = useState<string>("");

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    await handleAgenticSend(query);
    setQuery("");
  };

  return (
    <div className="h-[90vh] overflow-hidden rounded-lg shadow-md">
      <div className="flex flex-col h-full">
        {/* Chat Header */}
        <div className="p-4 bg-gray-100 border-b border-gray-300">
          <h2 className="text-xl font-semibold">Agentic Chatbot</h2>
        </div>

        {/* Chat Messages */}
        <div className="flex-1 p-4 overflow-y-auto bg-gray-50">
          {/* Display Chat History */}
          {messages.length > 0 ? (
            messages.map((msg, index) => (
              <div
                key={index}
                className={`mb-4 flex ${
                  msg.role === "human" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`${
                    msg.role === "human" ? "bg-blue-500 text-white" : "bg-gray-300 text-black"
                  } rounded-lg p-2 max-w-xs`}
                >
                  {msg.content}

                  {/* Display sentiment data for AI messages if available */}
                  {msg.role === "ai" && msg.sentiment && (
                    <div className="mt-2 text-sm">
                      <span
                        className={`inline-block px-2 py-1 rounded mr-2 ${getPolarityLabel(
                          msg.sentiment.polarity
                        ).color}`}
                      >
                        Polarity: {getPolarityLabel(msg.sentiment.polarity).label} ({msg.sentiment.polarity.toFixed(2)})
                      </span>
                      <span
                        className={`inline-block px-2 py-1 rounded ${getSubjectivityLabel(
                          msg.sentiment.subjectivity
                        ).color}`}
                      >
                        Subjectivity: {getSubjectivityLabel(msg.sentiment.subjectivity).label} ({msg.sentiment.subjectivity.toFixed(2)})
                      </span>
                    </div>
                  )}
                </div>
              </div>
            ))
          ) : (
            <p className="text-center text-gray-700">No chat history available.</p>
          )}
        </div>

        {/* Chat Input */}
        <div className="p-4 bg-white flex items-center space-x-2">
          <form onSubmit={handleSubmit} className="flex-1 flex">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask the Agentic Chatbot..."
              className="flex-1 border border-gray-300 rounded p-2"
            />
            <Button
              type="submit"
              disabled={isLoading}
              className="ml-2 bg-green-500 text-white px-4 py-2 rounded"
            >
              {isLoading ? "Sending..." : "Ask"}
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default AgenticChatWindow;
