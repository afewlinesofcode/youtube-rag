import { useEffect, useMemo, useRef, useState } from "react";
import type { Video } from "../../types";

export function useVideoLibraryState() {
  const [videos, setVideos] = useState<Video[]>([]);
  const [selectedVideoId, setSelectedVideoId] = useState<string | null>(null);
  const selectedVideoIdRef = useRef<string | null>(null);

  useEffect(() => {
    selectedVideoIdRef.current = selectedVideoId;
  }, [selectedVideoId]);

  const activeVideo = useMemo(
    () => videos.find((video) => video.id === selectedVideoId) ?? null,
    [selectedVideoId, videos],
  );

  return {
    videos,
    setVideos,
    selectedVideoId,
    setSelectedVideoId,
    selectedVideoIdRef,
    activeVideo,
  };
}
