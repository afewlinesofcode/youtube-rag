import { useCallback } from "react";
import { getVideoProcess } from "../../lib/api";

const MAX_POLL_ATTEMPTS = 240;
const POLL_INTERVAL_MS = 2000;

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}

type UseVideoProcessPollingParams = {
  onInfoStatus: (text: string) => void;
};

export function useVideoProcessPolling({
  onInfoStatus,
}: UseVideoProcessPollingParams) {
  const waitForVideoReady = useCallback(
    async (jobId: string): Promise<string> => {
      for (let attempt = 0; attempt < MAX_POLL_ATTEMPTS; attempt += 1) {
        await delay(POLL_INTERVAL_MS);
        const currentJob = await getVideoProcess(jobId);

        if (currentJob.status === "queued") {
          if (currentJob.attempt_count > 0) {
            onInfoStatus(
              `Retry queued. Attempt ${currentJob.attempt_count + 1} of ${currentJob.max_attempts} will start soon...`,
            );
          } else {
            onInfoStatus("Job queued. Waiting for worker...");
          }
          continue;
        }

        if (currentJob.status === "running") {
          onInfoStatus(
            `Processing transcript and embeddings. Attempt ${currentJob.attempt_count} of ${currentJob.max_attempts}...`,
          );
          continue;
        }

        if (currentJob.status === "failed") {
          throw new Error(currentJob.error || "Could not process video.");
        }

        if (currentJob.status === "succeeded" && currentJob.video_id) {
          return currentJob.video_id;
        }
      }

      throw new Error("Processing timed out. Please try again.");
    },
    [onInfoStatus],
  );

  return {
    waitForVideoReady,
  };
}
