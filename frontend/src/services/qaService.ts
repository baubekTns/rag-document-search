import type { QaAnswerResponse } from "../types/qa";

const API_BASE_URL = "http://localhost:8000";

export async function askQuestion(
  question: string,
  contextLimit = 2,
): Promise<QaAnswerResponse> {
  const params = new URLSearchParams({
    q: question,
    context_limit: String(contextLimit),
  });

  const response = await fetch(
    `${API_BASE_URL}/qa/answer?${params.toString()}`,
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Failed to answer question");
  }

  return data as QaAnswerResponse;
}
