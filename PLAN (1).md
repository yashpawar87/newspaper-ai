# In-App Article Reading And Hover Upgrade
Keeps people inside the newspaper experience instead of immediately bouncing to an external tab — matches how a real newspaper works (you read the page you're on, then optionally seek out the original wire source).

## Summary
Build a canonical `/article/[id]` page and route every article surface to it instead of opening the publisher URL. Article opens will count as engagement for reranking. Missing full content will be scraped in the backend background enrichment cycle after RSS fetches, with robots.txt checks still enforced. The UI will keep source attribution by name, but will not show an original publisher link, per your preference.

## Key Changes
- Add a Next.js route at `/article/[id]` that fetches `GET /articles/{id}` and renders a newspaper-style article page inside the existing `ZoomablePage`.
- Update hero, grid cards, sidebar headlines, homepage articles, category articles, and breaking ticker to link to `/article/${article.id}`.
- Move click tracking to in-app article opens:
  - Article links call `POST /articles/{id}/click` before or during navigation.
  - The article detail page also safely registers an open once, so direct links count too.
- Create shared article presentation helpers/components:
  - A reusable headline link style with a deliberate hover treatment instead of a plain underline.
  - A reusable article body renderer so `HeroArticle`, `ArticleCard`, `HeadlineSidebar`, and `/article/[id]` do not duplicate paragraph logic.
- Re-enable backend background enrichment:
  - After each RSS fetch cycle, run an enrichment batch for articles with `content IS NULL`.
  - Use existing `trafilatura` extraction and `robots.txt` guard.
  - Store scraped text in `articles.content` with `content_source="scraped"`.
  - Keep failures non-blocking: failed scrape leaves the article as summary-only.
- Add config knobs:
  - `ENRICH_INTERVAL_MINUTES=30`
  - `ENRICH_BATCH_SIZE=10`
  - `ENABLE_ARTICLE_SCRAPING=true`
- Keep article page fallback behavior:
  - If scraped/feed full content exists, render it as the article body.
  - If only summary exists, render the summary as the available article body and show a subtle “summary only” disclosure.
  - Do not render a publisher link.

## Hover Interaction
- Replace bare underline with a shared headline hover style:
  - Slight text color/accent shift.
  - Thin animated rule or highlight behind/under the headline.
  - Image zoom remains on image-backed cards.
  - Cursor and focus states clearly indicate in-app navigation.
- Apply the same interaction consistently to:
  - Hero headline
  - Article card headline
  - Sidebar headline
  - Breaking ticker item

## Test Plan
- Backend:
  - Run Python compile check.
  - Run a fetch/enrich cycle against a temp database and confirm articles with missing `content` are enriched when robots allow it.
  - Confirm failed scraping does not crash scheduler.
  - Confirm `POST /articles/{id}/click` increments `click_count` and updates `rank_score`.
- Frontend:
  - Run `npm run build`.
  - Verify `/article/[id]` renders with full content when present.
  - Verify summary-only articles still render without breaking.
  - Verify all article surfaces navigate internally, not to `article.link`.
  - Verify no publisher link is shown.
  - Verify hover treatment appears on hero, cards, sidebar, and ticker.

## Assumptions
- In-app opens, not publisher exits, are the ranking engagement signal.
- Original publisher URL remains stored in the database but is not displayed in the UI.
- Scraping is allowed to run for active sources when `ENABLE_ARTICLE_SCRAPING=true`, but the extractor still fails closed when robots.txt disallows scraping.
- Background enrichment is preferred over lazy scraping on article open.
