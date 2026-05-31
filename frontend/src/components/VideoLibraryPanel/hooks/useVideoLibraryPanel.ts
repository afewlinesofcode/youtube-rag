import { useCallback } from "react";
import type { Video } from "../../../types";

type UseVideoLibraryPanelParams = {
  selectedVideoId: string | null;
  onRefresh: () => Promise<void>;
  onSelectVideo: (video: Video) => Promise<void>;
};

export function useVideoLibraryPanel({
  selectedVideoId,
  onRefresh,
  onSelectVideo,
}: UseVideoLibraryPanelParams) {
  const handleRefresh = useCallback(async () => {
    await onRefresh();
  }, [onRefresh]);

  const handleSelectVideo = useCallback(
    async (video: Video) => {
      await onSelectVideo(video);
    },
    [onSelectVideo],
  );

  const isVideoActive = useCallback(
    (videoId: string) => videoId === selectedVideoId,
    [selectedVideoId],
  );

  return {
    handleRefresh,
    handleSelectVideo,
    isVideoActive,
  };
}
