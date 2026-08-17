import type { ChatMessage } from "../../types/chat";
import { AnswerCard } from "./AnswerCard";

interface ConversationProps {
  messages: ChatMessage[];
}

export function Conversation({ messages }: ConversationProps) {
  if (messages.length === 0) {
    return <p className="empty-state conversation-empty">Ask a question to start a document-grounded conversation.</p>;
  }

  return (
    <div className="conversation">
      {messages.map((message) => <AnswerCard key={message.id} message={message} />)}
    </div>
  );
}
