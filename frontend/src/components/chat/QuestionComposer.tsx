interface QuestionComposerProps {
  question: string;
  loading: boolean;
  onQuestionChange: (question: string) => void;
  onSubmit: () => void;
}

export function QuestionComposer({
  question,
  loading,
  onQuestionChange,
  onSubmit,
}: QuestionComposerProps) {
  return (
    <>
      <textarea
        value={question}
        onChange={(event) => onQuestionChange(event.target.value)}
        placeholder="Ask a question about your uploaded documents..."
        rows={4}
        disabled={loading}
      />

      <br />

      <button onClick={onSubmit} disabled={loading || !question.trim()}>
        {loading ? "Answering..." : "Ask"}
      </button>
    </>
  );
}
