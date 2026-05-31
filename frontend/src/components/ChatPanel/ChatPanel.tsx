import type { UiMessage, Video } from "../../types";
import { useChatPanel } from "./hooks/useChatPanel";

type ChatPanelProps = {
  activeVideo: Video | null;
  messages: UiMessage[];
  isSendingQuestion: boolean;
  onSendQuestion: (question: string) => Promise<void>;
};

const EMPTY_TOPIC = "Ask questions once a transcript has been embedded.";

export function ChatPanel({
  activeVideo,
  messages,
  isSendingQuestion,
  onSendQuestion,
}: ChatPanelProps) {
  const { question, setQuestion, handleQuestion } = useChatPanel({
    activeVideoId: activeVideo?.id ?? null,
    isSendingQuestion,
    onSendQuestion,
  });

  return (
    <section className="flex min-h-0 flex-1 flex-col rounded-[28px] border border-white/10 bg-white/5 shadow-glow backdrop-blur-xl">
      <div className="border-b border-white/10 px-5 py-4 md:px-6">
        <h3 className="font-display text-2xl font-semibold text-white">
          Chat with the transcript
        </h3>
        <p className="mt-2 text-sm leading-6 text-slate-300">
          {activeVideo ? activeVideo.topic : EMPTY_TOPIC}
        </p>
      </div>

      <div className="flex-1 overflow-auto px-4 py-5 md:px-6">
        {!activeVideo ? (
          <div className="flex h-full min-h-[240px] items-center justify-center rounded-[24px] border border-dashed border-white/10 bg-slate-950/30 px-6 text-center text-sm leading-7 text-slate-400">
            Process a YouTube URL or choose a saved video to open its chat.
          </div>
        ) : messages.length === 0 ? (
          <div className="flex h-full min-h-[240px] items-center justify-center rounded-[24px] border border-dashed border-white/10 bg-slate-950/30 px-6 text-center text-sm leading-7 text-slate-400">
            No questions yet for this video.
          </div>
        ) : (
          <div className="space-y-3">
            {messages.map((message, index) => (
              <div
                key={`${message.id}-${index}`}
                className={`max-w-[min(820px,92%)] rounded-[24px] border px-4 py-3 text-sm leading-7 md:text-[15px] ${
                  message.role === "user"
                    ? "ml-auto border-sky-400/30 bg-sky-500/15 text-sky-50"
                    : message.isError
                      ? "mr-auto border-rose-400/30 bg-rose-500/10 text-rose-50"
                      : "mr-auto border-white/10 bg-slate-950/60 text-slate-100"
                } ${message.isPending ? "opacity-80" : ""}`}
              >
                {message.content}
              </div>
            ))}
          </div>
        )}
      </div>

      <form
        className="border-t border-white/10 p-4 md:p-6"
        onSubmit={handleQuestion}
      >
        <div className="grid gap-3 lg:grid-cols-[minmax(0,1fr)_auto]">
          <input
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            type="text"
            placeholder="Ask about this video..."
            className="h-14 rounded-2xl border border-white/10 bg-slate-950/60 px-4 text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-sky-400/50 focus:ring-2 focus:ring-sky-400/20 disabled:opacity-60"
            autoComplete="off"
            disabled={!activeVideo || isSendingQuestion}
            aria-label="Question"
          />
          <button
            type="submit"
            disabled={!activeVideo || isSendingQuestion}
            className="inline-flex h-14 items-center justify-center rounded-2xl bg-white px-6 font-semibold text-slate-950 transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isSendingQuestion ? "Sending..." : "Send question"}
          </button>
        </div>
      </form>
    </section>
  );
}
