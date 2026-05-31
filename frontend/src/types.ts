export interface Video {
  id: string;
  youtube_url: string;
  title: string;
  topic: string;
  created_at: string;
}

export interface ChatMessage {
  id: number;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

export type StatusTone = "idle" | "success" | "error" | "info";

export type UiMessage = ChatMessage & {
  isPending?: boolean;
  isError?: boolean;
};

export interface ProcessJob {
  id: string;
  youtube_url: string;
  status: "queued" | "running" | "succeeded" | "failed";
  video_id: string | null;
  error: string | null;
  created_at: string;
  updated_at: string;
}
