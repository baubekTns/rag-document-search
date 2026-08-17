import { act, renderHook, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { useAbortableRequest } from "./useAbortableRequest";

function deferred<T>() {
  let resolve: (value: T) => void;

  const promise = new Promise<T>((resolvePromise) => {
    resolve = resolvePromise;
  });

  return { promise, resolve: resolve! };
}

describe("useAbortableRequest", () => {
  it("keeps the newest response when an earlier request resolves late", async () => {
    const first = deferred<string>();
    const second = deferred<string>();
    const request = vi.fn(([query]: [string]) => query === "first" ? first.promise : second.promise);
    const { result } = renderHook(() => useAbortableRequest(request));

    act(() => {
      void result.current.execute("first");
      void result.current.execute("second");
    });

    await act(async () => {
      second.resolve("new result");
      await second.promise;
    });

    await act(async () => {
      first.resolve("stale result");
      await first.promise;
    });

    await waitFor(() => expect(result.current.data).toBe("new result"));
    expect(result.current.status).toBe("success");
  });

  it("cancels an in-flight request and preserves existing data", async () => {
    const pending = deferred<string>();
    const { result } = renderHook(() => useAbortableRequest(() => pending.promise));

    act(() => {
      void result.current.execute();
    });
    act(() => result.current.cancel());

    expect(result.current.status).toBe("idle");
    expect(result.current.data).toBeNull();
  });

  it("retries the most recent request arguments", async () => {
    const request = vi.fn().mockRejectedValueOnce(new Error("Temporary failure")).mockResolvedValueOnce("recovered");
    const { result } = renderHook(() => useAbortableRequest(request));

    await act(async () => {
      await result.current.execute("payment");
    });
    await act(async () => {
      await result.current.retry();
    });

    expect(request).toHaveBeenNthCalledWith(1, ["payment"], expect.any(AbortSignal));
    expect(request).toHaveBeenNthCalledWith(2, ["payment"], expect.any(AbortSignal));
    expect(result.current.data).toBe("recovered");
  });
});
