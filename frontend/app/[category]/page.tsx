import { notFound } from "next/navigation";
import { getArticles, getCategories } from "@/lib/api";
import { CATEGORY_THEMES, getCategoryTheme } from "@/lib/categories";
import HeroArticle from "@/components/HeroArticle";
import HeadlineSidebar from "@/components/HeadlineSidebar";
import ArticleGrid from "@/components/ArticleGrid";
import ZoomablePage from "@/components/ZoomablePage";
import MarketWatch from "@/components/MarketWatch";

export const revalidate = 60;

export async function generateStaticParams() {
  const categories = await getCategories().catch(() => []);
  const slugs = new Set([
    ...CATEGORY_THEMES.map((category) => category.slug),
    ...categories.map((category) => category.slug),
  ]);
  return Array.from(slugs).map((category) => ({ category }));
}

export default async function CategoryPage({
  params,
}: {
  params: { category: string };
}) {
  const [categoryRows, articleResponse] = await Promise.all([
    getCategories().catch(() => []),
    getArticles(params.category, 1, 15).catch(() => ({
      articles: [],
      page: 1,
      total: 0,
    })),
  ]);

  const isKnownCategory =
    CATEGORY_THEMES.some((category) => category.slug === params.category) ||
    categoryRows.some((category) => category.slug === params.category);

  if (!isKnownCategory) notFound();

  const theme = getCategoryTheme(params.category);
  const { articles } = articleResponse;

  if (articles.length === 0) {
    return (
      <ZoomablePage>
        <div className="px-12 py-14 sm:px-20">
          <div className="border-b-2 border-ink pb-5 text-center">
            <p
              className="font-mono text-[11px] font-medium uppercase tracking-wider"
              style={{ color: theme.color }}
            >
              {theme.name}
            </p>
            <h1 className="mt-2 font-display text-5xl font-medium leading-none text-ink">
              {theme.name}
            </h1>
          </div>
          <div className="mx-auto flex min-h-[420px] max-w-xl flex-col items-center justify-center text-center">
            <p className="font-mono text-[11px] uppercase tracking-wider text-ink/50">
              Edition pending
            </p>
            <h2 className="mt-3 font-display text-3xl font-medium leading-tight text-ink">
              No ranked stories are available for this section yet.
            </h2>
            <p className="mt-3 text-sm leading-relaxed text-ink/60">
              This page will fill automatically after the backend fetches and ranks the RSS feed.
            </p>
          </div>
        </div>
      </ZoomablePage>
    );
  }

  // Articles arrive pre-sorted by rank_score from the backend:
  // position 1 = hero, next 4 = sidebar "in brief", rest = grid.
  const [hero, ...rest] = articles;
  const sidebarArticles = rest.slice(0, 4);
  const gridArticles = rest.slice(4);

  return (
    <ZoomablePage>
      <div className="px-12 py-14 sm:px-20">
        <MarketWatch />
        <h1 className="sr-only">{theme.name}</h1>
        <div className="grid grid-cols-1 gap-8 border-b border-ink/15 pb-8 lg:grid-cols-[2fr_1fr]">
          <HeroArticle article={hero} accentColor={theme.color} />
          <HeadlineSidebar articles={sidebarArticles} accentColor={theme.color} />
        </div>
        <div className="pt-8">
          <ArticleGrid articles={gridArticles} />
        </div>
      </div>
    </ZoomablePage>
  );
}
