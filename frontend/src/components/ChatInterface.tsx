import { useState } from "react";
import { useAskQuestion } from "../features/qa/useAskQuestion";
import CitationViewer from "./CitationViewer";

export default function ChatInterface() {
  const [question, setQuestion] = useState("");
  const [validationMessage, setValidationMessage] = useState("");
  const { messages, error, status, execute } = useAskQuestion();
  const loading = status === "loading";

  const handleAsk = async () => {
    const trimmedQuestion = question.trim();

    if (!trimmedQuestion) {
      setValidationMessage("Please enter a question.");
      return;
    }

    setValidationMessage("");
    setQuestion("");
    await execute(trimmedQuestion);
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

      {validationMessage && <p>{validationMessage}</p>}
      {error && <p>{error.message}</p>}

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

              <CitationViewer sources={chatMessage.response.sources} />
            </article>
          ))
        )}
      </div>
    </section>
  );
}
