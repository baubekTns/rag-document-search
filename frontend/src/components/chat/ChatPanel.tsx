import { useState } from "react";
import { useDocumentWorkspace } from "../../features/documents/useDocumentWorkspace";
import { useAskQuestion } from "../../features/qa/useAskQuestion";
import { Conversation } from "./Conversation";
import { QuestionComposer } from "./QuestionComposer";

export function ChatPanel() {
  const [question, setQuestion] = useState("");
  const [validationMessage, setValidationMessage] = useState("");
  const [cancellationMessage, setCancellationMessage] = useState("");
  const { messages, error, status, execute, cancel } = useAskQuestion();
  const workspace = useDocumentWorkspace();
  const loading = status === "loading";

  const handleAsk = async () => {
    const trimmedQuestion = question.trim();

    if (!trimmedQuestion) {
      setValidationMessage("Please enter a question.");
      return;
    }

    setValidationMessage("");
    setCancellationMessage("");
    setQuestion("");
    await execute(trimmedQuestion, workspace.selectedDocumentId);
  };

  const handleCancel = () => {
    cancel();
    setCancellationMessage("Question cancelled. Your conversation is still available.");
  };

  const errorMessage = validationMessage || error?.message;

  return (
    <section className="panel chat-panel" aria-labelledby="chat-title">
      <div className="panel-heading panel-heading-inline">
        <div>
          <p className="eyebrow">Ask</p>
          <h2 id="chat-title">Ask your documents</h2>
          <p>Get a grounded answer with the source passages used to create it.</p>
        </div>
        <p className="scope-pill">Scope: {workspace.scopeLabel}</p>
      </div>
      <QuestionComposer
        question={question}
        loading={loading}
        onQuestionChange={setQuestion}
        onSubmit={() => void handleAsk()}
        describedBy={errorMessage ? "question-error" : undefined}
      />

      {loading && <button className="button button-tertiary cancel-action" type="button" onClick={handleCancel}>Cancel question</button>}
      {errorMessage && <p id="question-error" className="feedback feedback-error" role="alert">{errorMessage}</p>}
      {loading && <p className="feedback feedback-loading" role="status" aria-live="polite">Reviewing your documents...</p>}
      {cancellationMessage && <p className="feedback feedback-loading" role="status" aria-live="polite">{cancellationMessage}</p>}
      <Conversation messages={messages} />
    </section>
  );
}
