import type { ChatMessage } from "../../types/chat";
import { CitationList } from "./CitationList";

interface AnswerCardProps {
  message: ChatMessage;
}

export function AnswerCard({ message }: AnswerCardProps) {
  return (
    <article className="answer-card">
      <div className="answer-card-question">
        <p className="answer-label">Question</p>
        <p>{message.question}</p>
      </div>

      <div className="answer-card-response">
        <p className="answer-label">Answer</p>
        <p>{message.response.answer}</p>
      </div>

      <div className="answer-quality">
        <p className="answer-label">Quality</p>
        <p><strong>Answerable:</strong> {message.response.quality.is_answerable ? "Yes" : "No"}</p>
        <p><strong>Reason:</strong> {message.response.quality.reason}</p>
      </div>

      <CitationList sources={message.response.sources} />
    </article>
  );
}
