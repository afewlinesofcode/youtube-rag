import { SubmitEvent, useCallback, useState } from "react";

type UseWorkspaceHeaderParams = {
  isProcessingVideo: boolean;
  onProcessVideo: (youtubeUrl: string) => Promise<void>;
};

export function useWorkspaceHeader({
  isProcessingVideo,
  onProcessVideo,
}: UseWorkspaceHeaderParams) {
  const [youtubeUrl, setYoutubeUrl] = useState("");

  const handleProcess = useCallback(
    async (event: SubmitEvent) => {
      event.preventDefault();
      const url = youtubeUrl.trim();
      if (!url || isProcessingVideo) {
        return;
      }

      await onProcessVideo(url);
      setYoutubeUrl("");
    },
    [isProcessingVideo, onProcessVideo, youtubeUrl],
  );

  return {
    youtubeUrl,
    setYoutubeUrl,
    handleProcess,
  };
}
