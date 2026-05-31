import type { ChatMessage, ProcessJob, Video } from "../types";

type JsonValue =
  | Record<string, unknown>
  | Array<unknown>
  | string
  | number
  | boolean
  | null;

type ChatStreamHandlers = {
  onToken: (token: string) => void;
};

type ChatStreamEvent =
  | { type: "token"; content?: string }
  | { type: "done" }
  | { type: "error"; detail?: string };

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") ?? "";
const STREAM_PATH = "/api/chat/stream";
const SSE_EVENT_DELIMITER = "\n\n";

async function requestJson<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set("Accept", "application/json");
  if (init.body != null && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${apiBaseUrl}${path}`, {
    ...init,
    headers,
  });

  const data = (await response.json().catch(() => null)) as {
    detail?: string;
    message?: string;
  } | null;

  if (!response.ok) {
    throw new Error(data?.detail || data?.message || "Request failed");
  }

  return data as T;
}

export function listVideos(): Promise<Video[]> {
  return requestJson<Video[]>("/api/videos");
}

export function startVideoProcess(youtubeUrl: string): Promise<ProcessJob> {
  return requestJson<ProcessJob>("/api/videos/process", {
    method: "POST",
    body: JSON.stringify({ youtube_url: youtubeUrl } satisfies JsonValue),
  });
}

export function getVideoProcess(jobId: string): Promise<ProcessJob> {
  return requestJson<ProcessJob>(`/api/videos/process/${jobId}`);
}

export function getActiveVideoProcess(): Promise<ProcessJob | null> {
  return requestJson<ProcessJob | null>("/api/videos/process/active");
}

export function listMessages(videoId: string): Promise<ChatMessage[]> {
  return requestJson<ChatMessage[]>(`/api/videos/${videoId}/messages`);
}

export function sendQuestion(
  documentId: string,
  question: string,
): Promise<{ answer: string }> {
  return requestJson<{ answer: string }>("/api/chat", {
    method: "POST",
    body: JSON.stringify({
      document_id: documentId,
      question,
    } satisfies JsonValue),
  });
}

function parseSseData(rawEvent: string): string {
  const lines = rawEvent.split("\n");
  const dataLines = lines
    .filter((line) => line.startsWith("data:"))
    .map((line) => line.slice(5).trim());
  return dataLines.join("\n");
}

function parseChatStreamEvent(rawEvent: string): ChatStreamEvent | null {
  const rawData = parseSseData(rawEvent);
  if (!rawData) {
    return null;
  }

  try {
    return JSON.parse(rawData) as ChatStreamEvent;
  } catch {
    return null;
  }
}

function splitSseEvents(buffer: string): { events: string[]; rest: string } {
  const events: string[] = [];
  let remaining = buffer;

  let boundaryIndex = remaining.indexOf(SSE_EVENT_DELIMITER);
  while (boundaryIndex >= 0) {
    events.push(remaining.slice(0, boundaryIndex));
    remaining = remaining.slice(boundaryIndex + SSE_EVENT_DELIMITER.length);
    boundaryIndex = remaining.indexOf(SSE_EVENT_DELIMITER);
  }

  return { events, rest: remaining };
}

function handleChatStreamEvent(
  event: ChatStreamEvent,
  handlers: ChatStreamHandlers,
): "continue" | "done" {
  if (event.type === "token") {
    handlers.onToken(event.content ?? "");
    return "continue";
  }

  if (event.type === "error") {
    throw new Error(event.detail || "Could not answer question.");
  }

  return "done";
}

async function fetchChatStreamResponse(
  documentId: string,
  question: string,
): Promise<Response> {
  return fetch(`${apiBaseUrl}${STREAM_PATH}`, {
    method: "POST",
    headers: {
      Accept: "text/event-stream",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      document_id: documentId,
      question,
    } satisfies JsonValue),
  });
}

async function assertStreamResponseOk(response: Response): Promise<void> {
  if (response.ok) {
    return;
  }

  const data = (await response.json().catch(() => null)) as {
    detail?: string;
    message?: string;
  } | null;

  throw new Error(data?.detail || data?.message || "Request failed");
}

export async function streamQuestion(
  documentId: string,
  question: string,
  handlers: ChatStreamHandlers,
): Promise<void> {
  const response = await fetchChatStreamResponse(documentId, question);
  await assertStreamResponseOk(response);

  if (!response.body) {
    throw new Error("Streaming response is not available.");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) {
      break;
    }

    buffer += decoder.decode(value, { stream: true });

    const { events, rest } = splitSseEvents(buffer);
    buffer = rest;

    for (const rawEvent of events) {
      const event = parseChatStreamEvent(rawEvent);
      if (!event) {
        continue;
      }

      if (handleChatStreamEvent(event, handlers) === "done") {
        return;
      }
    }
  }
}
