# CLAUDE.md — RSS Newspaper Aggregator

This file gives Claude (and any developer) full context on the project: what it is, how it's structured, and the conventions to follow when writing code for it.

---

## 1. Project Overview

A news aggregator web app that fetches RSS feeds from multiple Indian news sources, organizes them into categories, and displays each category as a **newspaper-style page** (hero story, ranked grid, sidebar) rather than a plain reverse-chronological list.

**Core loop:**
1. Backend periodically fetches RSS feeds per category.
2. Articles are parsed, deduplicated, enriched with images, and stored in Postgres.
3. A ranking score is computed per article (recency + source weight + engagement).
4. Frontend renders each category as its own newspaper page, pulling ranked articles from the API.

### Categories & Sources (v1)

| Category | Source | Feed URL |
|---|---|---|
| Top Stories | Times of India | `https://timesofindia.indiatimes.com/rssfeedstopstories.cms` |
| Latest Stories | India Today | `https://www.indiatoday.in/rss/home` |
| Tech | TechGenyz | `https://feeds.feedburner.com/techgenyz` |
| Business | OneIndia | `https://www.oneindia.com/rss/feeds/news-business-fb.xml` |
| Entertainment | OneIndia | `https://www.oneindia.com/rss/feeds/news-entertainment-fb.xml` |
| Sports | The Hindu | `https://www.thehindu.com/sport/feeder/` |
| Lifestyle & Fashion | The Hindu | `https://www.thehindu.com/life-and-style/feeder/default.rss` |
| Cricket | Times of India | `https://timesofindia.indiatimes.com/rssfeeds/54829575.cms` |

Sources should **not** be hardcoded in application logic — store them in a `sources` DB table so new feeds/categories can be added via an admin endpoint without a redeploy.

---

## 2. Refined Feature Set

### v1 (MVP)
- Fetch, parse, store, dedupe articles per category.
- Image extraction with `og:image` scrape fallback when RSS lacks an image.
- Per-category newspaper-style page: 1 hero (top-ranked), secondary grid, headline sidebar list.
- Homepage: mix of top-ranked stories across all categories + breaking ticker.
- Article click tracked; page displays whatever the feed provides — full `content` in a newspaper column layout when the publisher includes it, otherwise `summary` plus an outbound "continue reading" link to the original source. No scraping of source-page HTML to backfill truncated feeds (see conventions, section 11).
- Basic ranking: recency decay + source weight.
- Cron/scheduled fetch job (every 10–15 min).
- Feed health monitoring (last successful fetch, failure count) surfaced in admin.

### v2+ (post-MVP ideas)
- Search across articles (Postgres full-text search or Meilisearch).
- Trending page driven by real click-through data.
- Redis caching layer in front of category queries.
- Bookmarks / "read later" (needs lightweight auth — magic link or OAuth).
- Admin dashboard: add/disable sources, pin/unpin stories, view feed health.
- Near-duplicate detection across sources (title similarity / fuzzy hashing) so the same story from two feeds doesn't appear twice.
- Infinite scroll or "load more" pagination per category.
- Sitemap.xml + per-article SEO meta tags.
- Dark mode / theme toggle.
- PWA support for mobile.
- Personalization (category ordering based on reading history).
- **AI-generated summaries of scraped articles (v2)** — `backend/app/fetcher/summarizer.py` exists but isn't called by the enrichment pipeline yet. Currently (v1), `enrich.py` stores scraped article text **verbatim** in `articles.content` (`content_source = "scraped"`) — full-text reproduction of the source article, not a summary. This is the bigger copyright surface of the two options and is a deliberate v1 tradeoff to revisit, not the intended end state. The v2 plan is to swap the verbatim assignment in `enrich.py` for a call to `summarize_article()`, producing a short original-wording summary (`content_source = "ai_summary"`) instead — more clearly transformative and lower risk than storing the full text. A few things matter regardless of which mode is active:
  - Check each source's `robots.txt` and Terms of Service for scraping restrictions on a per-domain basis before extracting; don't scrape sources that prohibit it. This applies to the extraction step itself, independent of what's done with the content afterward.
  - Keep the "Continue reading at {source}" attribution and outbound link on every article regardless of `content_source` — scraped or summarized text is a pointer to the original, not a replacement for it.
  - Fact-check risk applies once summarization ships: an LLM summary can drop caveats, misstate numbers, or misattribute quotes from the source article — treat summaries as needing a lightweight accuracy spot-check, especially for anything time-sensitive (breaking news, figures, quotes).

---

## 3. Tech Stack

- **Frontend:** Next.js (App Router), React, TypeScript, Tailwind CSS — a Node.js runtime builds and serves this app, but Node.js is not used for any backend/business logic.
- **Backend:** Python, FastAPI, `feedparser` for RSS parsing, `httpx` for async HTTP, `BeautifulSoup` for `og:image` scraping fallback — all RSS fetching, ranking, and database access live here. The frontend never talks to Postgres directly; it only calls the FastAPI REST API.
- **Database:** PostgreSQL (Railway-managed Postgres plugin)
- **Scheduler:** APScheduler running inside a dedicated FastAPI worker process (or a separate Railway cron service calling an internal `/internal/fetch` endpoint)
- **Cache (v2):** Redis (Railway plugin)
- **Deployment:** Railway — separate services for `backend`, `frontend`, `fetcher` (or combined with backend), plus the Postgres plugin

---

## 4. Architecture

```
┌─────────────────┐       ┌──────────────────┐       ┌─────────────┐
│  RSS Sources     │──────▶│  Fetcher (APScheduler│──▶│  Postgres   │
│  (8 feeds)       │       │  job, every 10-15m)│    │  (articles, │
└─────────────────┘       └──────────────────┘       │  sources,   │
                                                        │  categories)│
                                                        └──────┬──────┘
                                                               │
                                                        ┌──────▼──────┐
                                                        │  FastAPI    │
                                                        │  REST API   │
                                                        └──────┬──────┘
                                                               │
                                                        ┌──────▼──────┐
                                                        │  Next.js    │
                                                        │  Frontend   │
                                                        │  (per-cat.  │
                                                        │  newspaper  │
                                                        │  pages)     │
                                                        └─────────────┘
```

The fetcher can run **inside** the FastAPI app (as a background task on startup using APScheduler) for simplicity in v1. Split it into its own Railway service only if fetch load starts affecting API response times.

---

## 5. Database Schema

```sql
CREATE TABLE categories (
    id          SERIAL PRIMARY KEY,
    slug        VARCHAR(50) UNIQUE NOT NULL,     -- e.g. 'top-stories', 'cricket'
    name        VARCHAR(100) NOT NULL,           -- e.g. 'Top Stories'
    sort_order  INT DEFAULT 0
);

CREATE TABLE sources (
    id              SERIAL PRIMARY KEY,
    category_id     INT REFERENCES categories(id),
    name            VARCHAR(100) NOT NULL,       -- e.g. 'Times of India'
    feed_url        TEXT NOT NULL UNIQUE,
    weight          FLOAT DEFAULT 1.0,           -- source trust/priority multiplier for ranking
    is_active       BOOLEAN DEFAULT TRUE,
    scraping_allowed BOOLEAN DEFAULT FALSE,       -- manually flipped to TRUE only after a robots.txt/ToS review for this source
    last_fetched_at TIMESTAMPTZ,
    last_success_at TIMESTAMPTZ,
    failure_count   INT DEFAULT 0
);

CREATE TABLE articles (
    id              SERIAL PRIMARY KEY,
    source_id       INT REFERENCES sources(id),
    category_id     INT REFERENCES categories(id),
    guid            TEXT UNIQUE,                 -- RSS <guid> or link, used for dedupe
    title           TEXT NOT NULL,
    summary         TEXT,                        -- RSS <description>, cleaned of HTML, short teaser
    content         TEXT,                        -- RSS <content:encoded> when the feed provides it, cleaned of HTML,
                                                    -- paragraphs separated by blank lines. NULL when the feed only
                                                    -- gives a teaser — the frontend falls back to `summary` + outbound link.
    content_source  VARCHAR(20),                 -- 'feed' | 'ai_summary' | NULL — drives the "AI summary" disclosure tag in the UI
    link            TEXT NOT NULL,                -- original article URL
    image_url       TEXT,                         -- from media:content, enclosure, or og:image scrape
    published_at    TIMESTAMPTZ,
    fetched_at      TIMESTAMPTZ DEFAULT now(),
    click_count     INT DEFAULT 0,
    rank_score      FLOAT DEFAULT 0,              -- precomputed, refreshed periodically
    is_pinned       BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_articles_category_rank ON articles(category_id, rank_score DESC);
CREATE INDEX idx_articles_published ON articles(published_at DESC);
```

---

## 6. RSS Fetching Strategy

1. Load active sources from `sources` table.
2. For each source, fetch feed via `httpx` (async, with timeout + retry/backoff).
3. Parse with `feedparser`.
4. For each entry:
   - Build `guid` from `entry.id` or `entry.link` (fallback).
   - Skip if `guid` already exists in DB (dedupe).
   - Extract image in this priority order: `media:content` → `media:thumbnail` → RSS `enclosure` → scrape `og:image` from `entry.link` (only if others fail, to limit extra HTTP calls) → category default placeholder image.
   - Clean `summary` HTML (strip tags, truncate to ~300 chars) using `BeautifulSoup`.
   - Extract `content`: check `entry.content[0].value` (Atom `content` / RSS `content:encoded`, what `feedparser` exposes when the publisher includes it) — strip HTML tags with `BeautifulSoup`, preserve paragraph breaks as blank lines, store as `content`. If the feed doesn't provide this field, leave `content` NULL; do not fetch and scrape the source page's HTML to fill it in — that reproduces text the publisher chose not to put in the feed for redistribution, which is a different legal footing than displaying what they published to the feed themselves. When `content` is NULL, the frontend shows `summary` plus an outbound "continue reading at {source}" link.
   - Insert article row.
5. Update `sources.last_fetched_at`; on success reset `failure_count`, on failure increment it and log the reason.
6. If `failure_count` exceeds a threshold (e.g. 5 consecutive), flag source as unhealthy (surface in admin, don't auto-disable in v1).

Run this job every 10–15 minutes via APScheduler (`IntervalTrigger`). Guard against overlapping runs with a simple lock flag.

---

## 7. Ranking Algorithm (v1)

```
rank_score = (source_weight * 10)
           + recency_score
           + (click_count * 0.5)
           + (is_pinned ? 1000 : 0)

recency_score = max(0, 100 - hours_since_published * 2)   # decays to 0 after ~50 hours
```

Recompute `rank_score` for all articles from the last 72 hours on a schedule (e.g. every 15 min, right after fetch). Older articles simply drop out of category page queries (`WHERE published_at > now() - interval '7 days'`).

---

## 8. Backend Structure (FastAPI)

```
backend/
├── app/
│   ├── main.py                # FastAPI app init, CORS, scheduler startup
│   ├── config.py               # env vars (DATABASE_URL, ANTHROPIC_API_KEY, etc.)
│   ├── seed.py                 # one-time script inserting the 8 categories + sources
│   ├── db/
│   │   ├── models.py           # SQLAlchemy models
│   │   └── session.py
│   ├── api/
│   │   ├── categories.py       # GET /categories
│   │   └── articles.py         # GET /articles, GET /articles/{id}, POST /articles/{id}/click, GET /trending
│   ├── fetcher/
│   │   ├── scheduler.py        # APScheduler: fetch cycle + enrich cycle, each on its own interval
│   │   ├── parser.py           # feedparser wrapper: dedupe, image extraction, feed content:encoded extraction
│   │   ├── robots.py           # robots.txt check, fails closed
│   │   ├── extractor.py        # HTML scraper (trafilatura) for full article text, gated by robots.py
│   │   ├── summarizer.py       # Anthropic API call turning scraped text into a short original-wording summary
│   │   ├── enrich.py           # orchestrates extractor + summarizer for articles still missing `content`
│   │   └── ranking.py          # rank_score computation
│   └── schemas.py              # Pydantic response models
├── requirements.txt
├── .env.example
└── Procfile
```

### Content pipeline (two stages)

1. **Fetch cycle** (`fetch_interval_minutes`, default 15 min) — pulls every active source's RSS feed, inserts new articles with `summary` (teaser) and `content` set from the feed's own `content:encoded` when present (`content_source = "feed"`), otherwise `content` stays NULL.
2. **Enrich cycle** (`enrich_interval_minutes`, default 30 min, `enrich_batch_size` per run) — for articles still missing `content`, from sources where `scraping_allowed = TRUE`, scrapes the source page and stores the extracted text **as-is** (`content_source = "scraped"`). v1 does not summarize this text — it's the full article body, unsummarized, which is why article cards on the frontend render at variable heights (see `ArticleGrid`'s masonry layout) rather than a fixed size. **v2 plan:** route this through `summarizer.py` instead of storing verbatim, setting `content_source = "ai_summary"`. Storing full scraped text verbatim is a meaningfully bigger copyright surface than a summary — full-text reproduction of another publisher's article, not a transformative rewrite — so this is a deliberate, revisit-later v1 tradeoff, not the intended end state.

`scraping_allowed` on the `sources` table starts `FALSE` for every source (see `seed.py`) and must be flipped manually per source only after reading that source's `robots.txt` and Terms of Service — this is not something the code decides for you. `extractor.py` also re-checks `robots.txt` live at scrape time as a second, automated line of defense, independent of the manual flag.

The frontend always renders an outbound "Continue reading at {source} →" link beneath the article body, regardless of `content_source` — a summary or scraped copy points to the original reporting, it doesn't replace it. `HeroArticle` shows a small disclosure tag next to the article: "Full text via source" when `content_source = "scraped"`, "AI summary" when `content_source = "ai_summary"` (v2). Article grid cards (`ArticleGrid`) render as a CSS-columns masonry layout rather than a fixed grid, since full unsummarized article bodies vary a lot in length — cards settle at their natural height instead of being clamped to a uniform size.

### Key API endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/categories` | List all categories |
| GET | `/articles?category=cricket&page=1&limit=20` | Ranked articles for a category |
| GET | `/articles/{id}` | Single article detail |
| POST | `/articles/{id}/click` | Increment click count, then frontend redirects to `link` |
| GET | `/trending` | Top articles across all categories (v2) |
| GET | `/health` | Fetch job status, feed health summary |

---

## 9. Frontend Structure (Next.js)

```
frontend/
├── app/
│   ├── page.tsx                     # homepage: cross-category highlights + ticker
│   ├── [category]/page.tsx          # dynamic category page (newspaper layout)
│   ├── article/[id]/page.tsx        # optional preview before outbound redirect
│   └── layout.tsx
├── components/
│   ├── Header.tsx                   # nav across categories
│   ├── BreakingTicker.tsx
│   ├── HeroArticle.tsx              # large top story
│   ├── ArticleGrid.tsx              # secondary ranked stories
│   ├── HeadlineSidebar.tsx          # compact list, rest of ranked stories
│   └── ArticleCard.tsx
└── lib/api.ts                       # fetch wrapper for FastAPI backend
```

### Newspaper Layout Pattern (per category page)

- **Masthead** — category name, date, nav to other categories.
- **Hero** — #1 ranked article, large image, headline, summary.
- **Secondary grid** — next 4–6 ranked articles, 2–3 column grid with thumbnails.
- **Sidebar/column** — remaining articles as compact headline list (like a newspaper "in brief" column).
- Clicking any article calls `POST /articles/{id}/click` then redirects to the original source `link` (client-side, `window.location`).

### Color System ("Paper & Ink")

Defined in `tailwind.config.ts` (utility classes) and mirrored as CSS vars in `app/globals.css` (for inline styles / non-Tailwind consumers). Category accent colors live in `lib/categories.ts` as data, not Tailwind tokens, since they're driven by which category is active rather than fixed per-component.

**Base palette:**
| Token | Hex | Used for |
|---|---|---|
| `paper` | `#f6f4ee` | The floating "page" — masthead, the A3 card in `ZoomablePage`, article card backgrounds |
| `ink` | `#1a1a17` | Headlines, body text |
| `ink-secondary` | `#5c5b54` | Timestamps, byline metadata, secondary info (most components use `ink/50`–`ink/60` opacity for this same effect) |
| `canvas` | `#dcd8cc` | `<body>` background only — a muted warm gray behind the paper card so the ivory page reads as a distinct sheet rather than blending into the page background |

**Category accents** (`lib/categories.ts`, unchanged from earlier — used for active nav underline, "Top ranked"/eyebrow labels, and sidebar numbering via the `accentColor` prop):
| Category | Hex | Description |
|---|---|---|
| Top Stories | `#B23A2F` | Deep red |
| Latest Stories | `#445066` | Slate blue-gray |
| Tech | `#2B5C8A` | Blue |
| Business | `#3D6B35` | Green |
| Entertainment | `#6B3FA0` | Purple |
| Sports | `#C1622B` | Burnt orange |
| Lifestyle & Fashion | `#9C4F63` | Mauve |
| Cricket | `#1F6F5C` | Teal |

**UI-specific accents:**
- `live` (`#e4302c`) — the "Live" badge in `BreakingTicker`. Deliberately a brighter, more saturated red than the Top Stories deep red (`#B23A2F`) so breaking news reads as "urgent" rather than "just another category," even though both are red.
- Zoom controls (`ZoomablePage`'s floating pill) — semi-transparent white (`bg-white/40` + `backdrop-blur-md`) with a thin `border-white/50` border, rather than solid paper, so it reads as a floating overlay control regardless of what's scrolled beneath it.

---

## 10. Deployment (Railway)

- **Postgres plugin** — provisioned via Railway, connection string injected as `DATABASE_URL`.
- **Backend service** — deploy `backend/` as a Railway service (Dockerfile or Nixpacks auto-detect for Python). Run migrations on deploy (Alembic recommended). APScheduler starts on app startup within this service for v1.
- **Frontend service** — deploy `frontend/` as a separate Railway service (Next.js auto-detected by Nixpacks). Set `NEXT_PUBLIC_API_URL` to the backend's Railway public URL.
- **Redis plugin (v2)** — add when caching is introduced.

### Environment Variables

Backend:
```
DATABASE_URL=postgresql://...
FETCH_INTERVAL_MINUTES=15
ALLOWED_ORIGINS=https://your-frontend.up.railway.app
```

Frontend:
```
NEXT_PUBLIC_API_URL=https://your-backend.up.railway.app
```

---

## 11. Conventions for Claude / Contributors

- Never hardcode source URLs in Python logic — always read from the `sources` table (seed them via a migration/seed script, not inline code).
- All timestamps stored and compared in UTC; convert to IST only at display time in the frontend.
- Backend responses use Pydantic schemas — don't leak SQLAlchemy models directly through the API.
- Image URLs from external sources should be proxied or at least validated (check content-type) before storing, to avoid broken thumbnails.
- Keep the fetcher idempotent — re-running it must never create duplicate articles (rely on the `guid` unique constraint).
- Display only content the feed itself provides (`summary`, and `content` when the publisher includes `content:encoded`). Never scrape the source page's full article HTML to backfill a truncated feed — that crosses from "displaying what was published to the feed" into republishing text the publisher didn't put there for redistribution. When a feed only gives a teaser, show the teaser and link out — don't try to work around it.
- The frontend renders each category as a fixed-width "page card" (~1122px, roughly A3 portrait width at 96dpi) with floating zoom controls, rather than a full-bleed responsive page — see `components/ZoomablePage.tsx`. Site navigation (masthead, category tabs, ticker) stays outside the card and does not zoom.
- Prefer server-side rendering (Next.js App Router server components) for category pages for better SEO on first load; use client components only where interactivity is required (click tracking, ticker).
- Keep the language boundary strict: all fetching, parsing, ranking, and persistence logic belongs in the Python/FastAPI backend. The Next.js frontend is presentation-only — it calls the REST API and renders the response, never reimplements backend logic in a Node.js API route.

---

## 12. Open Decisions (flag to user before implementing)

- Auth strategy for bookmarks (v2) — magic link vs OAuth vs none.
- Whether to add a search backend (Postgres full-text vs external service) once article volume grows.
- Whether near-duplicate detection (v2) is worth the complexity given only 8 sources in v1.
- Per-source scraping legality review (v2, HTML extraction + AI summary) — needs a `robots.txt`/ToS check for each of the 8 sources before implementation; some may need to stay RSS-teaser-only.
- Whether AI-generated summaries get a visible "AI-summarized" disclosure label in the UI — worth deciding before shipping v2, not after.
