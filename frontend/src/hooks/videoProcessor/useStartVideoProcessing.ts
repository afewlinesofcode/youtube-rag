import { useCallback } from "react";
import { startVideoProcess } from "../../lib/api";

type UseStartVideoProcessingParams = {
  isProcessingVideo: boolean;
  onInfoStatus: (text: string) => void;
  onErrorStatus: (text: string) => void;
  watchProcessJob: (jobId: string) => Promise<void>;
};

function formatStartError(error: unknown): string {
  return error instanceof Error ? error.message : "Could not process video.";
}

export function useStartVideoProcessing({
  isProcessingVideo,
  onInfoStatus,
  onErrorStatus,
  watchProcessJob,
}: UseStartVideoProcessingParams) {
  const processVideo = useCallback(
    async (youtubeUrl: string) => {
      if (isProcessingVideo) {
        return;
      }

      onInfoStatus("Job queued. Preparing transcript extraction...");

      try {
        const job = await startVideoProcess(youtubeUrl);
        await watchProcessJob(job.id);
      } catch (error) {
        onErrorStatus(formatStartError(error));
      }
    },
    [isProcessingVideo, onErrorStatus, onInfoStatus, watchProcessJob],
  );

  return {
    processVideo,
  };
}
