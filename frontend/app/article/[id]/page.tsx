import { notFound } from "next/navigation";
import { getArticle, toParagraphs, timeAgo } from "@/lib/api";
import { getCategoryTheme } from "@/lib/categories";
import ZoomablePage from "@/components/ZoomablePage";
import ArticleClickTracker from "@/components/ArticleClickTracker";

export const revalidate = 60;

export default async function ArticlePage({
  params,
}: {
  params: { id: string };
}) {
  const id = parseInt(params.id, 10);
  if (isNaN(id)) notFound();

  const article = await getArticle(id).catch(() => null);
  if (!article) notFound();

  const bodyText = article.content ?? article.summary;
  const paragraphs = bodyText ? toParagraphs(bodyText) : [];
  const theme = getCategoryTheme(article.category_slug);

  return (
    <ZoomablePage>
      {/* Client component that fires click tracking once on mount */}
      <ArticleClickTracker articleId={article.id} />

      <article className="px-12 py-14 sm:px-20">
        {/* Category + meta row */}
        <div className="mb-5 flex items-center gap-3 border-b border-ink/15 pb-5">
          <span
            className="font-mono text-[11px] font-medium uppercase tracking-wider"
            style={{ color: theme.color }}
          >
            {theme.name}
          </span>
          <span className="font-mono text-[11px] text-ink/40">·</span>
          <span className="font-mono text-[11px] text-ink/50">
            {timeAgo(article.published_at)}
          </span>
          {article.content_source === "ai_summary" && (
            <span className="ml-auto inline-block rounded-sm border border-ink/20 px-1.5 py-0.5 font-mono text-[10px] uppercase tracking-wide text-ink/50">
              AI summary
            </span>
          )}
        </div>

        {/* Image */}
        {article.image_url && (
          <div className="mb-6 relative aspect-[21/9] overflow-hidden rounded bg-ink/5">
            <img
              src={article.image_url}
              alt=""
              className="h-full w-full object-cover"
            />
          </div>
        )}

        {/* Headline */}
        <h1 className="mb-8 font-display text-4xl font-medium leading-tight text-ink sm:text-5xl">
          {article.title}
        </h1>

        {/* Body */}
        {paragraphs.length > 0 ? (
          <div className="columns-1 gap-10 text-[15px] leading-relaxed text-ink/85 sm:columns-2 [column-rule:1px_solid_var(--color-ink-secondary)]">
            {paragraphs.map((p, i) => (
              <p
                key={i}
                className={
                  i === 0
                    ? "mb-4 break-inside-avoid first-letter:float-left first-letter:mr-2 first-letter:mt-1 first-letter:font-display first-letter:text-6xl first-letter:font-medium first-letter:leading-[0.8]"
                    : "mb-4 break-inside-avoid"
                }
              >
                {p}
              </p>
            ))}
          </div>
        ) : (
          <p className="text-sm text-ink/50 italic">No content available for this article.</p>
        )}
      </article>
    </ZoomablePage>
  );
}
