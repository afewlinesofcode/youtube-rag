import { useCallback, useState } from "react";

type UseProcessJobWatcherParams = {
  waitForVideoReady: (jobId: string) => Promise<string>;
  onSuccessStatus: (text: string) => void;
  onErrorStatus: (text: string) => void;
  onVideoReady: (videoId: string) => Promise<void>;
};

function formatProcessError(error: unknown): string {
  return error instanceof Error ? error.message : "Could not process video.";
}

export function useProcessJobWatcher({
  waitForVideoReady,
  onSuccessStatus,
  onErrorStatus,
  onVideoReady,
}: UseProcessJobWatcherParams) {
  const [isProcessingVideo, setIsProcessingVideo] = useState(false);

  const watchProcessJob = useCallback(
    async (jobId: string) => {
      setIsProcessingVideo(true);

      try {
        const resolvedVideoId = await waitForVideoReady(jobId);
        onSuccessStatus("Video is ready.");
        await onVideoReady(resolvedVideoId);
      } catch (error) {
        onErrorStatus(formatProcessError(error));
      } finally {
        setIsProcessingVideo(false);
      }
    },
    [onErrorStatus, onSuccessStatus, onVideoReady, waitForVideoReady],
  );

  return {
    isProcessingVideo,
    watchProcessJob,
  };
}
