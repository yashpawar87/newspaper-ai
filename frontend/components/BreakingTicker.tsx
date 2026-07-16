"use client";

import Link from "next/link";
import { Article } from "@/lib/types";

export default function BreakingTicker({ articles }: { articles: Article[] }) {
  if (articles.length === 0) return null;

  // Duplicate the list so the CSS animation can loop seamlessly at -50%.
  const loop = [...articles, ...articles];

  return (
    <div className="flex items-center gap-3 bg-ink text-paper">
      <span className="shrink-0 bg-live px-3 py-1.5 font-mono text-[11px] font-medium uppercase tracking-wider text-paper">
        Live
      </span>
      <div className="relative flex-1 overflow-hidden py-1.5">
        <div className="flex w-max animate-ticker gap-10 whitespace-nowrap text-sm">
          {loop.map((article, i) => (
            <Link
              key={`${article.id}-${i}`}
              href={`/article/${article.id}`}
              className="hover:opacity-75 transition-opacity"
            >
              {article.title}
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
