import type { Video } from "../../types";
import { useVideoLibraryPanel } from "./hooks/useVideoLibraryPanel";

type VideoLibraryPanelProps = {
  videos: Video[];
  selectedVideoId: string | null;
  isLoadingVideos: boolean;
  onRefresh: () => Promise<void>;
  onSelectVideo: (video: Video) => Promise<void>;
};

function formatDate(value: string) {
  return new Intl.DateTimeFormat("en", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export function VideoLibraryPanel({
  videos,
  selectedVideoId,
  isLoadingVideos,
  onRefresh,
  onSelectVideo,
}: VideoLibraryPanelProps) {
  const { handleRefresh, handleSelectVideo, isVideoActive } =
    useVideoLibraryPanel({
      selectedVideoId,
      onRefresh,
      onSelectVideo,
    });

  return (
    <aside className="flex min-h-[220px] flex-col rounded-[28px] border border-white/10 bg-white/5 p-4 shadow-glow backdrop-blur-xl lg:h-full lg:min-h-0 lg:w-[360px] lg:p-5">
      <div className="mb-5 flex items-start justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.28em] text-sky-200/80">
            YouTube RAG
          </p>
          <h1 className="mt-2 font-display text-2xl font-semibold text-white">
            Video library
          </h1>
          <p className="mt-2 text-sm leading-6 text-slate-300">
            Process a video, then ask questions against its transcript and
            embeddings.
          </p>
        </div>
        <button
          type="button"
          onClick={() => void handleRefresh()}
          className="inline-flex items-center justify-center rounded-2xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-slate-100 transition hover:border-sky-400/40 hover:bg-sky-400/10"
          aria-label="Refresh videos"
          title="Refresh videos"
        >
          Refresh
        </button>
      </div>

      <div className="mb-4 grid grid-cols-2 gap-3">
        <div className="rounded-2xl border border-white/10 bg-slate-950/50 p-3">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-400">
            Saved videos
          </p>
          <p className="mt-2 text-2xl font-semibold text-white">
            {videos.length}
          </p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-slate-950/50 p-3">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-400">
            State
          </p>
          <p className="mt-2 text-sm font-medium text-slate-100">
            {isLoadingVideos ? "Syncing" : "Ready"}
          </p>
        </div>
      </div>

      <div className="flex-1 overflow-auto pr-1 lg:min-h-0">
        {videos.length === 0 ? (
          <div className="rounded-3xl border border-dashed border-white/15 bg-slate-950/30 px-4 py-8 text-sm leading-6 text-slate-400">
            Processed videos will appear here.
          </div>
        ) : (
          <div className="space-y-3">
            {videos.map((video) => {
              const isActive = isVideoActive(video.id);

              return (
                <button
                  key={video.id}
                  type="button"
                  onClick={() => void handleSelectVideo(video)}
                  className={`w-full rounded-3xl border p-4 text-left transition duration-200 hover:-translate-y-0.5 hover:border-sky-400/40 hover:bg-sky-400/5 ${
                    isActive
                      ? "border-sky-400/50 bg-sky-400/10 shadow-[0_0_0_1px_rgba(56,189,248,0.18)]"
                      : "border-white/10 bg-slate-950/40"
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-base font-semibold leading-6 text-white">
                        {video.title}
                      </p>
                      <p className="mt-1 text-sm leading-6 text-slate-300">
                        {video.topic}
                      </p>
                    </div>
                    {isActive ? (
                      <span className="rounded-full border border-sky-400/30 bg-sky-400/10 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-sky-100">
                        Active
                      </span>
                    ) : null}
                  </div>
                  <div className="mt-4 flex flex-wrap gap-2 text-[11px] uppercase tracking-[0.18em] text-slate-400">
                    <span className="rounded-full border border-white/10 bg-white/5 px-2.5 py-1">
                      {formatDate(video.created_at)}
                    </span>
                    <span className="max-w-[180px] truncate rounded-full border border-white/10 bg-white/5 px-2.5 py-1 normal-case tracking-normal">
                      {video.youtube_url}
                    </span>
                  </div>
                </button>
              );
            })}
          </div>
        )}
      </div>
    </aside>
  );
}
