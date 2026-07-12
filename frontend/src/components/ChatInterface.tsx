import { useState } from "react";
import { askQuestion } from "../services/qaService";
import type { ChatMessage } from "../types/chat";

function createMessageId() {
  return `${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

export default function ChatInterface() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const handleAsk = async () => {
    const trimmedQuestion = question.trim();

    if (!trimmedQuestion) {
      setMessage("Please enter a question.");
      return;
    }

    try {
      setLoading(true);
      setMessage("");
      setQuestion("");

      const response = await askQuestion(trimmedQuestion, 2);

      const chatMessage: ChatMessage = {
        id: createMessageId(),
        question: trimmedQuestion,
        response,
      };

      setMessages((currentMessages) => [chatMessage, ...currentMessages]);
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Failed to answer question.";

      setMessage(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section>
      <h2>Chat with Documents</h2>

      <textarea
        value={question}
        onChange={(event) => setQuestion(event.target.value)}
        placeholder="Ask a question about your uploaded documents..."
        rows={4}
        disabled={loading}
      />

      <br />

      <button onClick={handleAsk} disabled={loading || !question.trim()}>
        {loading ? "Answering..." : "Ask"}
      </button>

      {message && <p>{message}</p>}

      <div>
        {messages.length === 0 ? (
          <p>No questions asked yet.</p>
        ) : (
          messages.map((chatMessage) => (
            <article key={chatMessage.id}>
              <h3>Question</h3>
              <p>{chatMessage.question}</p>

              <h3>Answer</h3>
              <p>{chatMessage.response.answer}</p>

              <h4>Quality</h4>
              <p>
                <strong>Answerable:</strong>{" "}
                {chatMessage.response.quality.is_answerable ? "Yes" : "No"}
              </p>
              <p>
                <strong>Reason:</strong> {chatMessage.response.quality.reason}
              </p>

              <h4>Sources</h4>

              {chatMessage.response.sources.length === 0 ? (
                <p>No sources returned.</p>
              ) : (
                chatMessage.response.sources.map((source) => (
                  <details key={source.chunk_id}>
                    <summary>
                      Source {source.source_number} — chunk {source.chunk_index}
                    </summary>

                    <p>
                      <strong>Rerank score:</strong>{" "}
                      {source.rerank_score.toFixed(3)}
                    </p>

                    <p>
                      <strong>Semantic score:</strong>{" "}
                      {source.semantic_score.toFixed(3)}
                    </p>

                    <p>
                      <strong>Keyword match:</strong>{" "}
                      {source.keyword_match ? "Yes" : "No"}
                    </p>

                    <p>{source.preview}</p>
                  </details>
                ))
              )}
            </article>
          ))
        )}
      </div>
    </section>
  );
}
