import { Article, ArticlesResponse, Category } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    // Revalidate every minute so category pages stay fresh without
    // hammering the backend on every request.
    next: { revalidate: 60 },
  });
  if (!res.ok) {
    throw new Error(`API request failed: ${res.status} ${path}`);
  }
  return res.json();
}

export function getCategories(): Promise<Category[]> {
  return apiFetch<Category[]>("/categories");
}

export function getArticles(
  categorySlug: string,
  page = 1,
  limit = 15
): Promise<ArticlesResponse> {
  const params = new URLSearchParams({
    category: categorySlug,
    page: String(page),
    limit: String(limit),
  });
  return apiFetch<ArticlesResponse>(`/articles?${params.toString()}`);
}

export function getTrending(limit = 10): Promise<Article[]> {
  return apiFetch<Article[]>(`/trending?limit=${limit}`);
}

export function getArticle(id: number): Promise<Article> {
  return apiFetch<Article>(`/articles/${id}`);
}

// Fire-and-forget click tracking. A failed ping should never block
// navigation to the source article.
export async function registerClick(id: number): Promise<void> {
  const url = `${API_URL}/articles/${id}/click`;
  try {
    if (typeof navigator !== "undefined" && "sendBeacon" in navigator) {
      navigator.sendBeacon(url);
      return;
    }
    await fetch(url, { method: "POST", keepalive: true });
  } catch {
    // ignore
  }
}

export function toParagraphs(text: string): string[] {
  return text
    .split(/\n\s*\n/)
    .map((p) => p.trim())
    .filter(Boolean);
}

export function excerpt(article: Pick<Article, "content" | "summary">, maxLength = 220): string | null {
  const source = article.content ?? article.summary;
  if (!source) return null;
  const flat = source.replace(/\s+/g, " ").trim();
  if (flat.length <= maxLength) return flat;
  return `${flat.slice(0, maxLength).trimEnd()}…`;
}

export function timeAgo(iso: string | null): string {
  if (!iso) return "recently";
  const diffMs = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diffMs / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins} min ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs} hr ago`;
  const days = Math.floor(hrs / 24);
  return `${days} day${days > 1 ? "s" : ""} ago`;
}
