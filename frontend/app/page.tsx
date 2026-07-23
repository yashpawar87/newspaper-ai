import { getTrending } from "@/lib/api";
import { getCategoryTheme } from "@/lib/categories";
import ArticleCard from "@/components/ArticleCard";
import HeroArticle from "@/components/HeroArticle";
import HeadlineSidebar from "@/components/HeadlineSidebar";
import ZoomablePage from "@/components/ZoomablePage";
import MarketWatch from "@/components/MarketWatch";

export const revalidate = 60;

export default async function HomePage() {
  const topStories = await getTrending(17).catch(() => []);
  const [hero, ...rest] = topStories;
  const sidebarArticles = rest.slice(0, 5);
  const gridArticles = rest.slice(5);
  const accentColor = hero ? getCategoryTheme(hero.category_slug).color : "#B23A2F";

  if (!hero) {
    return (
      <ZoomablePage>
        <div className="px-12 py-14 text-center sm:px-20">
          <p className="font-mono text-[11px] uppercase tracking-wider text-ink/50">
            Waiting for the first feed fetch
          </p>
          <h2 className="mt-2 font-display text-3xl font-medium text-ink">
            The edition is being assembled.
          </h2>
        </div>
      </ZoomablePage>
    );
  }

  return (
    <ZoomablePage>
      <div className="px-12 py-14 sm:px-20">
        <MarketWatch />
        <h1 className="sr-only">Top-ranked stories across all categories</h1>
        <div className="grid grid-cols-1 gap-8 border-b border-ink/15 pb-8 lg:grid-cols-[2fr_1fr]">
          <HeroArticle article={hero} accentColor={accentColor} />
          <HeadlineSidebar articles={sidebarArticles} accentColor={accentColor} />
        </div>
        {gridArticles.length > 0 && (
          <div className="grid grid-cols-1 gap-8 pt-8 sm:grid-cols-2 lg:grid-cols-3">
            {gridArticles.map((article) => (
              <ArticleCard key={article.id} article={article} size="sm" />
            ))}
          </div>
        )}
      </div>
    </ZoomablePage>
  );
}
