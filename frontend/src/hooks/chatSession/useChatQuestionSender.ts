import { useCallback, useState } from "react";
import { streamQuestion } from "../../lib/api";

type UseChatQuestionSenderParams = {
  onAppendPendingExchange: (question: string) => void;
  onUpdatePendingAnswer: (answer: string) => void;
  onResolvePendingAnswer: (answer: string) => void;
  onFailPendingAnswer: (errorText: string) => void;
  onClearStatus: () => void;
  onErrorStatus: (text: string) => void;
};

function formatQuestionError(error: unknown): string {
  return error instanceof Error ? error.message : "Could not answer question.";
}

export function useChatQuestionSender({
  onAppendPendingExchange,
  onUpdatePendingAnswer,
  onResolvePendingAnswer,
  onFailPendingAnswer,
  onClearStatus,
  onErrorStatus,
}: UseChatQuestionSenderParams) {
  const [isSendingQuestion, setIsSendingQuestion] = useState(false);

  const sendVideoQuestion = useCallback(
    async (videoId: string, question: string) => {
      if (isSendingQuestion) {
        return;
      }

      setIsSendingQuestion(true);
      onAppendPendingExchange(question);

      try {
        let fullAnswer = "";
        await streamQuestion(videoId, question, {
          onToken: (token) => {
            fullAnswer += token;
            onUpdatePendingAnswer(fullAnswer);
          },
        });

        onResolvePendingAnswer(fullAnswer.trim());
        onClearStatus();
      } catch (error) {
        const errorText = formatQuestionError(error);
        onFailPendingAnswer(errorText);
        onErrorStatus(errorText);
      } finally {
        setIsSendingQuestion(false);
      }
    },
    [
      isSendingQuestion,
      onAppendPendingExchange,
      onClearStatus,
      onErrorStatus,
      onFailPendingAnswer,
      onUpdatePendingAnswer,
      onResolvePendingAnswer,
    ],
  );

  return {
    isSendingQuestion,
    sendVideoQuestion,
  };
}
