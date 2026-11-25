import type { MetaResponse, RecommendRequest, RecommendResponse } from "./types";

/** Railway/public API base URL — trailing slash stripped to avoid `//api/...`. */
const API_URL = (
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"
).replace(/\/+$/, "");

async function parseJson<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const body = (await res.json()) as { detail?: string };
      if (body.detail) detail = body.detail;
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

export async function fetchMeta(): Promise<MetaResponse> {
  const res = await fetch(`${API_URL}/api/meta`, { cache: "no-store" });
  return parseJson<MetaResponse>(res);
}

export async function postRecommend(
  body: RecommendRequest,
): Promise<RecommendResponse> {
  const res = await fetch(`${API_URL}/api/recommend`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return parseJson<RecommendResponse>(res);
}

export { API_URL };
