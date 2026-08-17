import { useState } from "react";
import { DocumentSelector } from "../documents/DocumentSelector";
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
    <section>
      <h2>Chat with Documents</h2>
      <DocumentSelector
        label="Question"
        documents={workspace.documents}
        selectedDocumentId={workspace.selectedDocumentId}
        status={workspace.documentStatus}
        error={workspace.documentError}
        onSelect={workspace.setSelectedDocumentId}
        onRetry={() => void workspace.refreshDocuments()}
      />
      <QuestionComposer
        question={question}
        loading={loading}
        onQuestionChange={setQuestion}
        onSubmit={() => void handleAsk()}
      />

      {validationMessage && <p>{validationMessage}</p>}
      {error && <p>{error.message}</p>}
      <Conversation messages={messages} />
    </section>
  );
}
