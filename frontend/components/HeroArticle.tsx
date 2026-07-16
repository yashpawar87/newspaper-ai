"use client";

import Link from "next/link";
import { Article } from "@/lib/types";
import { timeAgo, toParagraphs } from "@/lib/api";

export default function HeroArticle({
  article,
  accentColor,
}: {
  article: Article;
  accentColor: string;
}) {
  const bodyText = article.content ?? article.summary;
  const paragraphs = bodyText ? toParagraphs(bodyText) : [];
  const isAiSummary = article.content_source === "ai_summary";
  const isScraped = article.content_source === "scraped";

  return (
    <article>
      <Link href={`/article/${article.id}`} className="group block">
        <div className="relative mb-3 aspect-[21/9] overflow-hidden rounded bg-ink/5">
          {article.image_url ? (
            <img
              src={article.image_url}
              alt=""
              className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-[1.02]"
            />
          ) : (
            <div className="flex h-full items-center justify-center text-ink/25">
              <span className="font-mono text-sm">no image</span>
            </div>
          )}
        </div>
        <div className="flex items-center gap-2">
          <span
            className="inline-block font-mono text-[11px] font-medium uppercase tracking-wider"
            style={{ color: accentColor }}
          >
            {article.is_pinned ? "Editor's pick" : "Top ranked"}
          </span>
          {isAiSummary && (
            <span className="inline-block rounded-sm border border-ink/20 px-1.5 py-0.5 font-mono text-[10px] uppercase tracking-wide text-ink/50">
              AI summary
            </span>
          )}
          {isScraped && (
            <span className="inline-block rounded-sm border border-ink/20 px-1.5 py-0.5 font-mono text-[10px] uppercase tracking-wide text-ink/50">
              Full text via source
            </span>
          )}
        </div>
        <h2 className="headline-link mt-1 font-display text-3xl font-medium leading-tight text-ink sm:text-4xl">
          {article.title}
        </h2>
      </Link>

      <p className="mt-2 mb-5 font-mono text-[11px] text-ink/50">
        {timeAgo(article.published_at)}
      </p>

      {paragraphs.length > 0 && (
        <div className="columns-1 gap-8 text-[15px] leading-relaxed text-ink/85 sm:columns-2 [column-rule:1px_solid_var(--color-ink-secondary)]">
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
      )}
    </article>
  );
}
