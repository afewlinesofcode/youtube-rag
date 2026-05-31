import { useCallback } from "react";
import type { Dispatch, SetStateAction } from "react";
import type { Video } from "../../types";

type UseVideoSelectionParams = {
  setSelectedVideoId: Dispatch<SetStateAction<string | null>>;
  onLoadMessages: (videoId: string) => Promise<void>;
  onClearMessages: () => void;
  onInfoStatus: (text: string) => void;
  onClearStatus: () => void;
  onErrorStatus: (text: string) => void;
};

export function useVideoSelection({
  setSelectedVideoId,
  onLoadMessages,
  onClearMessages,
  onInfoStatus,
  onClearStatus,
  onErrorStatus,
}: UseVideoSelectionParams) {
  const selectVideo = useCallback(
    async (video: Video) => {
      setSelectedVideoId(video.id);
      onClearMessages();
      onInfoStatus(`Loading ${video.title}...`);

      try {
        await onLoadMessages(video.id);
        onClearStatus();
      } catch (error) {
        onErrorStatus(
          error instanceof Error ? error.message : "Could not load messages.",
        );
      }
    },
    [
      onClearMessages,
      onClearStatus,
      onErrorStatus,
      onInfoStatus,
      onLoadMessages,
      setSelectedVideoId,
    ],
  );

  return {
    selectVideo,
  };
}
