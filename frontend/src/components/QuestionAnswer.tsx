import { useState } from "react";
import { askQuestion } from "../services/qaService";
import type { QaAnswerResponse } from "../types/qa";

export default function QuestionAnswer() {
  const [question, setQuestion] = useState("");
  const [answerResult, setAnswerResult] = useState<QaAnswerResponse | null>(
    null,
  );
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const handleAsk = async () => {
    if (!question.trim()) {
      setMessage("Please enter a question.");
      return;
    }

    try {
      setLoading(true);
      setMessage("");
      setAnswerResult(null);

      const result = await askQuestion(question.trim());

      setAnswerResult(result);
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
      <h2>Ask a Question</h2>

      <textarea
        value={question}
        onChange={(event) => setQuestion(event.target.value)}
        placeholder="Ask something about your uploaded document..."
        rows={4}
        disabled={loading}
      />

      <br />

      <button onClick={handleAsk} disabled={loading || !question.trim()}>
        {loading ? "Answering..." : "Ask"}
      </button>

      {message && <p>{message}</p>}

      {answerResult && (
        <div>
          <h3>Answer</h3>

          <p>{answerResult.answer}</p>

          <h3>Quality Check</h3>

          <p>
            <strong>Answerable:</strong>{" "}
            {answerResult.quality.is_answerable ? "Yes" : "No"}
          </p>

          <p>
            <strong>Reason:</strong> {answerResult.quality.reason}
          </p>

          <p>
            <strong>Top rerank score:</strong>{" "}
            {answerResult.quality.top_rerank_score.toFixed(3)}
          </p>

          <p>
            <strong>Top semantic score:</strong>{" "}
            {answerResult.quality.top_semantic_score.toFixed(3)}
          </p>

          <h3>Sources</h3>

          {answerResult.sources.length === 0 ? (
            <p>No sources returned.</p>
          ) : (
            answerResult.sources.map((source) => (
              <article key={source.chunk_id}>
                <h4>Source {source.source_number}</h4>

                <p>
                  <strong>Chunk index:</strong> {source.chunk_index}
                </p>

                <p>
                  <strong>Rerank score:</strong>{" "}
                  {source.rerank_score.toFixed(3)}
                </p>

                <p>
                  <strong>Keyword match:</strong>{" "}
                  {source.keyword_match ? "Yes" : "No"}
                </p>

                <p>{source.preview}</p>
              </article>
            ))
          )}
        </div>
      )}
    </section>
  );
}
