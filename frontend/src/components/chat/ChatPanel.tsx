import { useState } from "react";
import { useDocumentWorkspace } from "../../features/documents/useDocumentWorkspace";
import { useAskQuestion } from "../../features/qa/useAskQuestion";
import { Conversation } from "./Conversation";
import { QuestionComposer } from "./QuestionComposer";

export function ChatPanel() {
  const [question, setQuestion] = useState("");
  const [validationMessage, setValidationMessage] = useState("");
  const { messages, error, status, execute } = useAskQuestion();
  const workspace = useDocumentWorkspace();
  const loading = status === "loading";

  const handleAsk = async () => {
    const trimmedQuestion = question.trim();

    if (!trimmedQuestion) {
      setValidationMessage("Please enter a question.");
      return;
    }

    setValidationMessage("");
    setQuestion("");
    await execute(trimmedQuestion, workspace.selectedDocumentId);
  };

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
      />

      {validationMessage && <p className="feedback feedback-error">{validationMessage}</p>}
      {error && <p className="feedback feedback-error">{error.message}</p>}
      {loading && <p className="feedback feedback-loading">Reviewing your documents...</p>}
      <Conversation messages={messages} />
    </section>
  );
}
