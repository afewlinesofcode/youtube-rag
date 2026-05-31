import { useVideoLibraryLoader } from "./videoLibrary/useVideoLibraryLoader";
import { useVideoLibraryState } from "./videoLibrary/useVideoLibraryState";
import { useVideoSelection } from "./videoLibrary/useVideoSelection";

type UseAppVideoLibraryParams = {
  onLoadMessages: (videoId: string) => Promise<void>;
  onClearMessages: () => void;
  onInfoStatus: (text: string) => void;
  onClearStatus: () => void;
  onErrorStatus: (text: string) => void;
};

export function useAppVideoLibrary({
  onLoadMessages,
  onClearMessages,
  onInfoStatus,
  onClearStatus,
  onErrorStatus,
}: UseAppVideoLibraryParams) {
  const {
    videos,
    setVideos,
    selectedVideoId,
    setSelectedVideoId,
    selectedVideoIdRef,
    activeVideo,
  } = useVideoLibraryState();

  const { isLoadingVideos, loadVideos, refreshVideos } = useVideoLibraryLoader({
    selectedVideoIdRef,
    setVideos,
    setSelectedVideoId,
    onLoadMessages,
    onClearMessages,
    onErrorStatus,
  });

  const { selectVideo } = useVideoSelection({
    setSelectedVideoId,
    onLoadMessages,
    onClearMessages,
    onInfoStatus,
    onClearStatus,
    onErrorStatus,
  });

  return {
    videos,
    selectedVideoId,
    activeVideo,
    isLoadingVideos,
    loadVideos,
    refreshVideos,
    selectVideo,
  };
}
