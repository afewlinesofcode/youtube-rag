import { useEffect } from "react";
import { getActiveVideoProcess } from "../../lib/api";

type UseRestoreActiveVideoProcessParams = {
  onInfoStatus: (text: string) => void;
  onErrorStatus: (text: string) => void;
  watchProcessJob: (jobId: string) => Promise<void>;
};

function restoreStatusText(status: string): string {
  return status === "queued"
    ? "Job queued. Waiting for worker..."
    : "Processing transcript and embeddings...";
}

function formatRestoreError(error: unknown): string {
  return error instanceof Error
    ? error.message
    : "Could not restore process state.";
}

export function useRestoreActiveVideoProcess({
  onInfoStatus,
  onErrorStatus,
  watchProcessJob,
}: UseRestoreActiveVideoProcessParams) {
  useEffect(() => {
    let isCancelled = false;

    void getActiveVideoProcess()
      .then((activeJob) => {
        if (!activeJob || isCancelled) {
          return;
        }

        onInfoStatus(restoreStatusText(activeJob.status));
        return watchProcessJob(activeJob.id);
      })
      .catch((error) => {
        if (!isCancelled) {
          onErrorStatus(formatRestoreError(error));
        }
      });

    return () => {
      isCancelled = true;
    };
  }, [onErrorStatus, onInfoStatus, watchProcessJob]);
}
