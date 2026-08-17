import { useCallback, useEffect, useRef, useState } from "react";

export type RequestStatus = "idle" | "loading" | "success" | "error";

interface UseAbortableRequestOptions {
  clearDataOnExecute?: boolean;
}

interface AbortableRequest<TArgs extends readonly unknown[], TData> {
  data: TData | null;
  error: Error | null;
  status: RequestStatus;
  execute: (...args: TArgs) => Promise<TData | undefined>;
  retry: () => Promise<TData | undefined>;
  cancel: () => void;
  reset: () => void;
}

function toError(error: unknown): Error {
  return error instanceof Error
    ? error
    : new Error("The request could not be completed. Please try again.");
}

export function useAbortableRequest<TArgs extends readonly unknown[], TData>(
  request: (args: TArgs, signal: AbortSignal) => Promise<TData>,
  { clearDataOnExecute = false }: UseAbortableRequestOptions = {},
): AbortableRequest<TArgs, TData> {
  const [data, setData] = useState<TData | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [status, setStatus] = useState<RequestStatus>("idle");
  const controllerRef = useRef<AbortController | null>(null);
  const requestIdRef = useRef(0);
  const lastArgsRef = useRef<TArgs | null>(null);
  const mountedRef = useRef(true);
  const requestRef = useRef(request);

  requestRef.current = request;

  useEffect(() => {
    mountedRef.current = true;

    return () => {
      mountedRef.current = false;
      controllerRef.current?.abort();
    };
  }, []);

  const cancel = useCallback(() => {
    requestIdRef.current += 1;
    controllerRef.current?.abort();
    controllerRef.current = null;

    if (mountedRef.current) {
      setError(null);
      setStatus("idle");
    }
  }, []);

  const reset = useCallback(() => {
    cancel();

    if (mountedRef.current) {
      setData(null);
    }
  }, [cancel]);

  const execute = useCallback(
    async (...args: TArgs): Promise<TData | undefined> => {
      controllerRef.current?.abort();

      const controller = new AbortController();
      const requestId = requestIdRef.current + 1;

      requestIdRef.current = requestId;
      controllerRef.current = controller;
      lastArgsRef.current = args;

      if (mountedRef.current) {
        setError(null);
        setStatus("loading");

        if (clearDataOnExecute) {
          setData(null);
        }
      }

      try {
        const response = await requestRef.current(args, controller.signal);

        if (!mountedRef.current || requestId !== requestIdRef.current) {
          return undefined;
        }

        setData(response);
        setStatus("success");
        return response;
      } catch (requestError) {
        if (
          controller.signal.aborted ||
          !mountedRef.current ||
          requestId !== requestIdRef.current
        ) {
          return undefined;
        }

        setError(toError(requestError));
        setStatus("error");
        return undefined;
      } finally {
        if (requestId === requestIdRef.current) {
          controllerRef.current = null;
        }
      }
    },
    [clearDataOnExecute],
  );

  const retry = useCallback(() => {
    return lastArgsRef.current ? execute(...lastArgsRef.current) : Promise.resolve(undefined);
  }, [execute]);

  return { data, error, status, execute, retry, cancel, reset };
}
