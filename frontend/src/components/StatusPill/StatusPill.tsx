type StatusTone = "idle" | "success" | "error" | "info";

type StatusPillProps = {
  tone: StatusTone;
  text: string;
};

export function StatusPill({ tone, text }: StatusPillProps) {
  if (tone === "idle" || !text) {
    return null;
  }

  const styles = {
    success: "border-emerald-500/30 bg-emerald-500/10 text-emerald-100",
    error: "border-rose-500/30 bg-rose-500/10 text-rose-100",
    info: "border-sky-500/30 bg-sky-500/10 text-sky-100",
  };

  return (
    <div
      className={`inline-flex rounded-full border px-3 py-1 text-sm ${styles[tone]}`}
    >
      {text}
    </div>
  );
}
