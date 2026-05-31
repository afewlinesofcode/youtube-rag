import type { StatusTone, Video } from "../../types";
import { StatusPill } from "../StatusPill/StatusPill";
import { useWorkspaceHeader } from "./hooks/useWorkspaceHeader";

type WorkspaceHeaderProps = {
  activeVideo: Video | null;
  statusTone: StatusTone;
  statusText: string;
  isProcessingVideo: boolean;
  onProcessVideo: (youtubeUrl: string) => Promise<void>;
};

export function WorkspaceHeader({
  activeVideo,
  statusTone,
  statusText,
  isProcessingVideo,
  onProcessVideo,
}: WorkspaceHeaderProps) {
  const { youtubeUrl, setYoutubeUrl, handleProcess } = useWorkspaceHeader({
    isProcessingVideo,
    onProcessVideo,
  });

  return (
    <section className="rounded-[28px] border border-white/10 bg-white/5 p-5 shadow-glow backdrop-blur-xl md:p-6">
      <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
        <div className="max-w-2xl">
          <p className="text-xs font-semibold uppercase tracking-[0.28em] text-sky-200/80">
            Workspace
          </p>
          <h2 className="mt-2 font-display text-3xl font-semibold tracking-tight text-white md:text-4xl">
            Turn a YouTube transcript into an answerable source.
          </h2>
          <p className="mt-3 text-sm leading-7 text-slate-300 md:text-base">
            The backend processes the transcript and embeddings; this UI keeps
            the chat loop fast and focused.
          </p>
        </div>

        <div className="flex flex-col items-start gap-3 lg:items-end">
          <StatusPill tone={statusTone} text={statusText} />
          {activeVideo ? (
            <div className="rounded-2xl border border-emerald-400/20 bg-emerald-400/10 px-4 py-3 text-sm text-emerald-50">
              <p className="font-semibold">{activeVideo.title}</p>
              <p className="mt-1 text-emerald-50/80">{activeVideo.topic}</p>
            </div>
          ) : (
            <div className="rounded-2xl border border-white/10 bg-slate-950/40 px-4 py-3 text-sm text-slate-300">
              No active video selected.
            </div>
          )}
        </div>
      </div>

      <form
        className="mt-6 grid gap-3 lg:grid-cols-[minmax(0,1fr)_auto]"
        onSubmit={handleProcess}
      >
        <input
          value={youtubeUrl}
          onChange={(event) => setYoutubeUrl(event.target.value)}
          type="url"
          placeholder="https://www.youtube.com/watch?v=..."
          className="h-14 rounded-2xl border border-white/10 bg-slate-950/60 px-4 text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-sky-400/50 focus:ring-2 focus:ring-sky-400/20"
          aria-label="YouTube URL"
          required
        />
        <button
          type="submit"
          disabled={isProcessingVideo}
          className="inline-flex h-14 items-center justify-center rounded-2xl bg-sky-500 px-6 font-semibold text-white transition hover:bg-sky-400 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isProcessingVideo ? "Processing..." : "Process video"}
        </button>
      </form>
    </section>
  );
}
