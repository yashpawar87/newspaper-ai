"use client";

import Link from "next/link";
import { Article } from "@/lib/types";
import { timeAgo, toParagraphs } from "@/lib/api";

export default function HeadlineSidebar({
  articles,
  accentColor,
}: {
  articles: Article[];
  accentColor: string;
}) {
  if (articles.length === 0) return null;

  return (
    <div>
      <p className="mb-3 border-b border-ink/15 pb-2 font-mono text-[11px] font-medium uppercase tracking-wider text-ink/50">
        In brief
      </p>
      <ul className="space-y-4">
        {articles.map((article, i) => (
          <li key={article.id}>
            <Link href={`/article/${article.id}`} className="group flex gap-3">
              <span
                className="mt-[3px] shrink-0 font-mono text-xs font-medium"
                style={{ color: accentColor }}
              >
                {String(i + 2).padStart(2, "0")}
              </span>
              <div>
                <h4 className="headline-link font-display text-[15px] font-medium leading-snug text-ink">
                  {article.title}
                </h4>
                {(article.content || article.summary) && (
                  <div className="mt-1 space-y-1.5 text-[12px] leading-relaxed text-ink/75">
                    {toParagraphs(article.content || article.summary || "").map((p, pIndex) => (
                      <p key={pIndex}>{p}</p>
                    ))}
                  </div>
                )}
                <p className="mt-0.5 font-mono text-[11px] text-ink/50">
                  {timeAgo(article.published_at)}
                </p>
              </div>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
