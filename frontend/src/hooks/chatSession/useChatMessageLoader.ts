import { useCallback } from "react";
import { listMessages } from "../../lib/api";
import type { UiMessage } from "../../types";

type UseChatMessageLoaderParams = {
  onMessagesLoaded: (messages: UiMessage[]) => void;
};

export function useChatMessageLoader({
  onMessagesLoaded,
}: UseChatMessageLoaderParams) {
  const loadMessages = useCallback(
    async (videoId: string) => {
      const nextMessages = await listMessages(videoId);
      onMessagesLoaded(nextMessages);
    },
    [onMessagesLoaded],
  );

  return {
    loadMessages,
  };
}
