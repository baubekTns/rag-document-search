import type { QaAnswerResponse } from "./qa";

export interface ChatMessage {
  id: string;
  question: string;
  response: QaAnswerResponse;
}
