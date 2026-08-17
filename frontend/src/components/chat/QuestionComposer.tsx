interface QuestionComposerProps {
  question: string;
  loading: boolean;
  onQuestionChange: (question: string) => void;
  onSubmit: () => void;
  describedBy?: string;
}

export function QuestionComposer({
  question,
  loading,
  onQuestionChange,
  onSubmit,
  describedBy,
}: QuestionComposerProps) {
  return (
    <form className="question-composer" onSubmit={(event) => { event.preventDefault(); onSubmit(); }} aria-busy={loading}>
      <label className="field-label" htmlFor="document-question">
        Your question
        <textarea
          id="document-question"
          value={question}
          onChange={(event) => onQuestionChange(event.target.value)}
          placeholder="Ask a question about your uploaded documents..."
          autoComplete="off"
          aria-describedby={describedBy}
          aria-invalid={Boolean(describedBy)}
          rows={4}
          disabled={loading}
        />
      </label>

      <button className="button button-primary" type="submit" disabled={loading || !question.trim()}>
        {loading ? "Answering..." : "Ask"}
      </button>
    </form>
  );
}
