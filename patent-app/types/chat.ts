// types/chat.ts

export type MessageRole =
  | "function"
  | "data"
  | "system"
  | "user"
  | "assistant"
  | "tool";

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  timestamp?: string; // Optional field for message timestamp
}
