import { Article } from "@/lib/types";
import ArticleCard from "./ArticleCard";

export default function ArticleGrid({ articles }: { articles: Article[] }) {
  if (articles.length === 0) return null;

  return (
    <div>
      <p className="mb-3 border-b border-ink/15 pb-2 font-mono text-[11px] font-medium uppercase tracking-wider text-ink/50">
        More stories
      </p>
      {/* Masonry via CSS columns rather than a row-and-column grid: each
          article renders at its natural height (full body text, no
          clamping), so columns settle at different lengths — closer to
          how a real newspaper page has uneven column breaks. */}
      <div className="columns-1 gap-x-10 sm:columns-2 lg:columns-3 [column-rule:1px_solid_rgba(26,26,23,0.1)]">
        {articles.map((article) => (
          <div key={article.id} className="mb-8 break-inside-avoid">
            <ArticleCard article={article} size="sm" />
          </div>
        ))}
      </div>
    </div>
  );
}
