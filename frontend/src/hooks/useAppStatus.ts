import { useCallback, useState } from "react";
import type { StatusTone } from "../types";

export function useAppStatus() {
  const [statusTone, setStatusTone] = useState<StatusTone>("idle");
  const [statusText, setStatusText] = useState("");

  const clearStatus = useCallback(() => {
    setStatusTone("idle");
    setStatusText("");
  }, []);

  const setInfoStatus = useCallback((text: string) => {
    setStatusTone("info");
    setStatusText(text);
  }, []);

  const setSuccessStatus = useCallback((text: string) => {
    setStatusTone("success");
    setStatusText(text);
  }, []);

  const setErrorStatus = useCallback((text: string) => {
    setStatusTone("error");
    setStatusText(text);
  }, []);

  return {
    statusTone,
    statusText,
    clearStatus,
    setInfoStatus,
    setSuccessStatus,
    setErrorStatus,
  };
}
