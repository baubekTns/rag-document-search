const LOCAL_API_BASE_URL = "http://localhost:8000";

function normalizeApiBaseUrl(value: string | undefined): string {
  const baseUrl = value?.trim() || LOCAL_API_BASE_URL;

  return baseUrl.replace(/\/+$/, "");
}

const API_BASE_URL = normalizeApiBaseUrl(import.meta.env.VITE_API_URL);

export class ApiError extends Error {
  readonly status: number;
  readonly details?: unknown;

  constructor(status: number, message: string, details?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

type ParsedResponse =
  | { kind: "empty" }
  | { kind: "json"; data: unknown }
  | { kind: "text"; data: string }
  | { kind: "invalid-json"; data: string };

function buildApiUrl(path: string): string {
  return `${API_BASE_URL}/${path.replace(/^\/+/, "")}`;
}

async function parseResponse(response: Response): Promise<ParsedResponse> {
  const text = await response.text();

  if (!text.trim()) {
    return { kind: "empty" };
  }

  const contentType = response.headers.get("content-type") ?? "";
  const expectsJson = contentType.includes("application/json");

  if (!expectsJson) {
    return { kind: "text", data: text };
  }

  try {
    return { kind: "json", data: JSON.parse(text) as unknown };
  } catch {
    return { kind: "invalid-json", data: text };
  }
}

function getErrorMessage(response: Response, parsed: ParsedResponse): string {
  if (parsed.kind === "json" && typeof parsed.data === "object" && parsed.data) {
    const detail = (parsed.data as { detail?: unknown }).detail;
    const message = (parsed.data as { message?: unknown }).message;

    if (typeof detail === "string" && detail.trim()) return detail;
    if (typeof message === "string" && message.trim()) return message;
  }

  if (response.status >= 500) {
    return "The server could not complete the request. Please try again.";
  }

  return "The request could not be completed. Please try again.";
}

function getDetails(parsed: ParsedResponse): unknown {
  return parsed.kind === "empty" ? undefined : parsed.data;
}

function isAbortError(error: unknown, signal?: AbortSignal): boolean {
  return signal?.aborted === true ||
    (error instanceof DOMException && error.name === "AbortError");
}

export interface ApiRequestOptions extends RequestInit {
  signal?: AbortSignal;
}

export async function requestJson<T>(
  path: string,
  options: ApiRequestOptions = {},
): Promise<T> {
  let response: Response;

  try {
    response = await fetch(buildApiUrl(path), options);
  } catch (error) {
    if (isAbortError(error, options.signal)) {
      throw new ApiError(0, "The request was cancelled.");
    }

    throw new ApiError(
      0,
      "Unable to reach the server. Check your connection and try again.",
      error,
    );
  }

  let parsed: ParsedResponse;

  try {
    parsed = await parseResponse(response);
  } catch (error) {
    if (isAbortError(error, options.signal)) {
      throw new ApiError(0, "The request was cancelled.");
    }

    throw new ApiError(
      response.status,
      "Unable to read the server response. Please try again.",
      error,
    );
  }

  if (!response.ok) {
    throw new ApiError(
      response.status,
      getErrorMessage(response, parsed),
      getDetails(parsed),
    );
  }

  if (parsed.kind === "json") {
    return parsed.data as T;
  }

  if (parsed.kind === "empty") {
    throw new ApiError(response.status, "The server returned an empty response.");
  }

  throw new ApiError(
    response.status,
    "The server returned an invalid response. Please try again.",
    parsed.data,
  );
}
