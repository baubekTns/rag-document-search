import type { ChatMessage } from "../../types/chat";
import { AnswerCard } from "./AnswerCard";

interface ConversationProps {
  messages: ChatMessage[];
}

export function Conversation({ messages }: ConversationProps) {
  if (messages.length === 0) {
    return <p>No questions asked yet.</p>;
  }

  return (
    <div>
      {messages.map((message) => <AnswerCard key={message.id} message={message} />)}
    </div>
  );
}
