import { useCallback, useRef, useState } from "react";
import { useAbortableRequest } from "../../hooks/useAbortableRequest";
import { askQuestion } from "../../services/qaService";
import type { ChatMessage } from "../../types/chat";
import type { QaAnswerResponse } from "../../types/qa";

function createMessageId() {
  return `${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

export function useAskQuestion() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const lastQuestionRef = useRef<string | null>(null);
  const {
    execute: executeRequest,
    retry: retryRequest,
    ...requestState
  } = useAbortableRequest<[string, string | null], QaAnswerResponse>(
    ([question, documentId], signal) => askQuestion(question, 2, signal, documentId),
  );

  const addMessage = useCallback((question: string, response: QaAnswerResponse) => {
    setMessages((currentMessages) => [
      { id: createMessageId(), question, response },
      ...currentMessages,
    ]);
  }, []);

  const execute = useCallback(
    async (question: string, documentId: string | null) => {
      lastQuestionRef.current = question;
      const response = await executeRequest(question, documentId);

      if (response) {
        addMessage(question, response);
      }

      return response;
    },
    [addMessage, executeRequest],
  );

  const retry = useCallback(async () => {
    const response = await retryRequest();

    if (response && lastQuestionRef.current) {
      addMessage(lastQuestionRef.current, response);
    }

    return response;
  }, [addMessage, retryRequest]);

  return { ...requestState, messages, execute, retry };
}
