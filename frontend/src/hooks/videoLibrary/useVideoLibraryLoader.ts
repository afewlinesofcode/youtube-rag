import { useCallback, useEffect, useState } from "react";
import type { Dispatch, RefObject, SetStateAction } from "react";
import { listVideos } from "../../lib/api";
import type { Video } from "../../types";

type UseVideoLibraryLoaderParams = {
  selectedVideoIdRef: RefObject<string | null>;
  setVideos: Dispatch<SetStateAction<Video[]>>;
  setSelectedVideoId: Dispatch<SetStateAction<string | null>>;
  onLoadMessages: (videoId: string) => Promise<void>;
  onClearMessages: () => void;
  onErrorStatus: (text: string) => void;
};

export function useVideoLibraryLoader({
  selectedVideoIdRef,
  setVideos,
  setSelectedVideoId,
  onLoadMessages,
  onClearMessages,
  onErrorStatus,
}: UseVideoLibraryLoaderParams) {
  const [isLoadingVideos, setIsLoadingVideos] = useState(false);

  const loadVideos = useCallback(
    async (preferredVideoId?: string) => {
      setIsLoadingVideos(true);

      try {
        const nextVideos = await listVideos();
        setVideos(nextVideos);

        const candidateId = preferredVideoId ?? selectedVideoIdRef.current;
        const nextSelectedVideo = candidateId
          ? (nextVideos.find((video) => video.id === candidateId) ?? null)
          : null;

        setSelectedVideoId(nextSelectedVideo?.id ?? null);

        if (nextSelectedVideo) {
          await onLoadMessages(nextSelectedVideo.id);
        } else {
          onClearMessages();
        }
      } catch (error) {
        onErrorStatus(
          error instanceof Error ? error.message : "Could not load videos.",
        );
      } finally {
        setIsLoadingVideos(false);
      }
    },
    [
      onClearMessages,
      onErrorStatus,
      onLoadMessages,
      selectedVideoIdRef,
      setSelectedVideoId,
      setVideos,
    ],
  );

  useEffect(() => {
    void loadVideos();
  }, [loadVideos]);

  const refreshVideos = useCallback(async () => {
    await loadVideos();
  }, [loadVideos]);

  return {
    isLoadingVideos,
    loadVideos,
    refreshVideos,
  };
}
