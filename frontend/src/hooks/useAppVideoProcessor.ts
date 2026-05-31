import { useProcessJobWatcher } from "./videoProcessor/useProcessJobWatcher";
import { useRestoreActiveVideoProcess } from "./videoProcessor/useRestoreActiveVideoProcess";
import { useStartVideoProcessing } from "./videoProcessor/useStartVideoProcessing";
import { useVideoProcessPolling } from "./videoProcessor/useVideoProcessPolling";

type UseAppVideoProcessorParams = {
  onInfoStatus: (text: string) => void;
  onSuccessStatus: (text: string) => void;
  onErrorStatus: (text: string) => void;
  onVideoReady: (videoId: string) => Promise<void>;
};

export function useAppVideoProcessor({
  onInfoStatus,
  onSuccessStatus,
  onErrorStatus,
  onVideoReady,
}: UseAppVideoProcessorParams) {
  const { waitForVideoReady } = useVideoProcessPolling({ onInfoStatus });

  const { isProcessingVideo, watchProcessJob } = useProcessJobWatcher({
    waitForVideoReady,
    onSuccessStatus,
    onErrorStatus,
    onVideoReady,
  });

  useRestoreActiveVideoProcess({
    onInfoStatus,
    onErrorStatus,
    watchProcessJob,
  });

  const { processVideo } = useStartVideoProcessing({
    isProcessingVideo,
    onInfoStatus,
    onErrorStatus,
    watchProcessJob,
  });

  return {
    isProcessingVideo,
    processVideo,
  };
}
