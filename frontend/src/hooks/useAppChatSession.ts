import { useChatMessageLoader } from "./chatSession/useChatMessageLoader";
import { useChatMessagesState } from "./chatSession/useChatMessagesState";
import { useChatQuestionSender } from "./chatSession/useChatQuestionSender";

type UseAppChatSessionParams = {
  onErrorStatus: (text: string) => void;
  onClearStatus: () => void;
};

export function useAppChatSession({
  onErrorStatus,
  onClearStatus,
}: UseAppChatSessionParams) {
  const {
    messages,
    clearMessages,
    setLoadedMessages,
    appendPendingExchange,
    updatePendingAnswer,
    resolvePendingAnswer,
    failPendingAnswer,
  } = useChatMessagesState();

  const { loadMessages } = useChatMessageLoader({
    onMessagesLoaded: setLoadedMessages,
  });

  const { isSendingQuestion, sendVideoQuestion } = useChatQuestionSender({
    onAppendPendingExchange: appendPendingExchange,
    onUpdatePendingAnswer: updatePendingAnswer,
    onResolvePendingAnswer: resolvePendingAnswer,
    onFailPendingAnswer: failPendingAnswer,
    onClearStatus,
    onErrorStatus,
  });

  return {
    messages,
    isSendingQuestion,
    clearMessages,
    loadMessages,
    sendVideoQuestion,
  };
}
