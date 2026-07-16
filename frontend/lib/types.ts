export interface Category {
  id: number;
  slug: string;
  name: string;
  sort_order: number;
}

export interface Article {
  id: number;
  title: string;
  summary: string | null;
  // Full body text as provided by the feed's content:encoded field, when
  // present. Plain text with paragraphs separated by blank lines — never
  // raw HTML. Falls back to null when the source only supplies a teaser
  // (in which case `summary` is all there is, and the reader is pointed
  // to `link` to read the rest).
  content: string | null;
  // "feed" when `content` came from the RSS feed's own content:encoded field.
  // "ai_summary" is reserved for a future summarization pipeline. Null means
  // the source only published a teaser in the feed.
  content_source: "feed" | "scraped" | "ai_summary" | null;
  link: string;
  image_url: string | null;
  source_name: string;
  category_slug: string;
  published_at: string | null;
  click_count: number;
  rank_score: number;
  is_pinned: boolean;
}

export interface ArticlesResponse {
  articles: Article[];
  page: number;
  total: number;
}
