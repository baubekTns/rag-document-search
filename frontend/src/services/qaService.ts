import { requestJson } from "./apiClient";
import type { QaAnswerResponse } from "../types/qa";

export async function askQuestion(
  question: string,
  contextLimit = 2,
  signal?: AbortSignal,
): Promise<QaAnswerResponse> {
  const params = new URLSearchParams({
    q: question,
    context_limit: String(contextLimit),
  });

  return requestJson<QaAnswerResponse>(`/qa/answer?${params.toString()}`, {
    signal,
  });
}
