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
    <div className="question-composer">
      <textarea
        value={question}
        onChange={(event) => onQuestionChange(event.target.value)}
        placeholder="Ask a question about your uploaded documents..."
        rows={4}
        disabled={loading}
      />

      <button className="button button-primary" onClick={onSubmit} disabled={loading || !question.trim()}>
        {loading ? "Answering..." : "Ask"}
      </button>
    </div>
  );
}
