"use client";

import Link from "next/link";
import { Article } from "@/lib/types";
import { timeAgo, toParagraphs } from "@/lib/api";

export default function ArticleCard({
  article,
  size = "md",
}: {
  article: Article;
  size?: "sm" | "md";
}) {
  const bodyText = article.content ?? article.summary;
  const paragraphs = bodyText ? toParagraphs(bodyText) : [];

  return (
    <article>
      <Link href={`/article/${article.id}`} className="group block">
        <div
          className={`relative mb-2 overflow-hidden rounded bg-ink/5 ${
            size === "sm" ? "aspect-[4/3]" : "aspect-[16/10]"
          }`}
        >
          {article.image_url ? (
            <img
              src={article.image_url}
              alt=""
              className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-[1.03]"
            />
          ) : (
            <div className="flex h-full items-center justify-center text-ink/25">
              <span className="font-mono text-xs">no image</span>
            </div>
          )}
        </div>
        <h3
          className={`headline-link font-display font-medium leading-snug text-ink ${
            size === "sm" ? "text-base" : "text-lg"
          }`}
        >
          {article.title}
        </h3>
      </Link>

      <p className="mt-1 mb-2 font-mono text-[11px] text-ink/50">
        {timeAgo(article.published_at)}
      </p>

      {paragraphs.length > 0 && (
        <div className="space-y-2 text-[13px] leading-relaxed text-ink/75">
          {paragraphs.map((p, i) => (
            <p key={i}>{p}</p>
          ))}
        </div>
      )}
    </article>
  );
}
