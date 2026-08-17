import type { ChatMessage } from "../../types/chat";
import { CitationList } from "./CitationList";

interface AnswerCardProps {
  message: ChatMessage;
}

export function AnswerCard({ message }: AnswerCardProps) {
  return (
    <article>
      <h3>Question</h3>
      <p>{message.question}</p>

      <h3>Answer</h3>
      <p>{message.response.answer}</p>

      <h4>Quality</h4>
      <p><strong>Answerable:</strong> {message.response.quality.is_answerable ? "Yes" : "No"}</p>
      <p><strong>Reason:</strong> {message.response.quality.reason}</p>

      <CitationList sources={message.response.sources} />
    </article>
  );
}
