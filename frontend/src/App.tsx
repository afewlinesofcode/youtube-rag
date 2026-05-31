import { useCallback } from "react";
import { ChatPanel } from "./components/ChatPanel/ChatPanel";
import { VideoLibraryPanel } from "./components/VideoLibraryPanel/VideoLibraryPanel";
import { WorkspaceHeader } from "./components/WorkspaceHeader/WorkspaceHeader";
import {
  useAppChatSession,
  useAppStatus,
  useAppVideoLibrary,
  useAppVideoProcessor,
} from "./hooks";

export function App() {
  const {
    statusTone,
    statusText,
    clearStatus,
    setInfoStatus,
    setSuccessStatus,
    setErrorStatus,
  } = useAppStatus();

  const {
    messages,
    isSendingQuestion,
    clearMessages,
    loadMessages,
    sendVideoQuestion,
  } = useAppChatSession({
    onErrorStatus: setErrorStatus,
    onClearStatus: clearStatus,
  });

  const {
    videos,
    selectedVideoId,
    activeVideo,
    isLoadingVideos,
    loadVideos,
    refreshVideos,
    selectVideo,
  } = useAppVideoLibrary({
    onLoadMessages: loadMessages,
    onClearMessages: clearMessages,
    onInfoStatus: setInfoStatus,
    onClearStatus: clearStatus,
    onErrorStatus: setErrorStatus,
  });

  const { isProcessingVideo, processVideo } = useAppVideoProcessor({
    onInfoStatus: setInfoStatus,
    onSuccessStatus: setSuccessStatus,
    onErrorStatus: setErrorStatus,
    onVideoReady: loadVideos,
  });

  const handleSendQuestion = useCallback(
    async (trimmedQuestion: string) => {
      if (!activeVideo || isSendingQuestion) {
        return;
      }

      await sendVideoQuestion(activeVideo.id, trimmedQuestion);
    },
    [activeVideo, isSendingQuestion, sendVideoQuestion],
  );

  return (
    <div className="min-h-screen bg-hero-radial text-slate-100 lg:h-screen lg:overflow-hidden">
      <div className="mx-auto flex min-h-screen max-w-7xl flex-col gap-5 px-4 py-4 md:px-6 lg:h-full lg:min-h-0 lg:flex-row lg:gap-6 lg:px-8 lg:py-6">
        <VideoLibraryPanel
          videos={videos}
          selectedVideoId={selectedVideoId}
          isLoadingVideos={isLoadingVideos}
          onRefresh={refreshVideos}
          onSelectVideo={selectVideo}
        />

        <main className="flex min-h-0 flex-1 flex-col gap-5 lg:h-full lg:overflow-hidden">
          <WorkspaceHeader
            activeVideo={activeVideo}
            statusTone={statusTone}
            statusText={statusText}
            isProcessingVideo={isProcessingVideo}
            onProcessVideo={processVideo}
          />

          <ChatPanel
            activeVideo={activeVideo}
            messages={messages}
            isSendingQuestion={isSendingQuestion}
            onSendQuestion={handleSendQuestion}
          />
        </main>
      </div>
    </div>
  );
}
