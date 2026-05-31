import { SubmitEvent, useCallback, useState } from "react";

type UseChatPanelParams = {
  activeVideoId: string | null;
  isSendingQuestion: boolean;
  onSendQuestion: (question: string) => Promise<void>;
};

export function useChatPanel({
  activeVideoId,
  isSendingQuestion,
  onSendQuestion,
}: UseChatPanelParams) {
  const [question, setQuestion] = useState("");

  const handleQuestion = useCallback(
    async (event: SubmitEvent) => {
      event.preventDefault();
      const trimmedQuestion = question.trim();

      if (!trimmedQuestion || !activeVideoId || isSendingQuestion) {
        return;
      }

      await onSendQuestion(trimmedQuestion);
      setQuestion("");
    },
    [activeVideoId, isSendingQuestion, onSendQuestion, question],
  );

  return {
    question,
    setQuestion,
    handleQuestion,
  };
}
