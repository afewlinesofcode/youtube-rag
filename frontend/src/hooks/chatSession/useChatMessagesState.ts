import { useCallback, useState } from "react";
import type { UiMessage } from "../../types";

function replaceLastMessage(
  current: UiMessage[],
  patch: Partial<UiMessage>,
): UiMessage[] {
  if (current.length === 0) {
    return current;
  }

  const next = [...current];
  next[next.length - 1] = {
    ...next[next.length - 1],
    ...patch,
  };
  return next;
}

export function useChatMessagesState() {
  const [messages, setMessages] = useState<UiMessage[]>([]);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  const setLoadedMessages = useCallback((nextMessages: UiMessage[]) => {
    setMessages(nextMessages);
  }, []);

  const appendPendingExchange = useCallback((question: string) => {
    setMessages((current) => [
      ...current,
      {
        id: Date.now(),
        role: "user",
        content: question,
        created_at: new Date().toISOString(),
      },
      {
        id: Date.now() + 1,
        role: "assistant",
        content: "Thinking...",
        created_at: new Date().toISOString(),
        isPending: true,
      },
    ]);
  }, []);

  const resolvePendingAnswer = useCallback((answer: string) => {
    setMessages((current) =>
      replaceLastMessage(current, {
        content: answer,
        isPending: false,
        isError: false,
      }),
    );
  }, []);

  const updatePendingAnswer = useCallback((answer: string) => {
    setMessages((current) =>
      replaceLastMessage(current, {
        content: answer,
        isPending: true,
        isError: false,
      }),
    );
  }, []);

  const failPendingAnswer = useCallback((errorText: string) => {
    setMessages((current) =>
      replaceLastMessage(current, {
        content: errorText,
        isPending: false,
        isError: true,
      }),
    );
  }, []);

  return {
    messages,
    clearMessages,
    setLoadedMessages,
    appendPendingExchange,
    updatePendingAnswer,
    resolvePendingAnswer,
    failPendingAnswer,
  };
}
