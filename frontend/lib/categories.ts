export type CategoryTheme = {
  slug: string;
  name: string;
  color: string;
};

// Accent color per category. Kept here rather than in the DB so the frontend
// can render a color even before a category exists server-side, and so a
// designer can retune the palette without touching the backend.
export const CATEGORY_THEMES: CategoryTheme[] = [
  { slug: "top-stories", name: "Top Stories", color: "#B23A2F" },
  { slug: "latest-stories", name: "Latest Stories", color: "#445066" },
  { slug: "tech", name: "Tech", color: "#2B5C8A" },
  { slug: "business", name: "Business", color: "#3D6B35" },
  { slug: "entertainment", name: "Entertainment", color: "#6B3FA0" },
  { slug: "sports", name: "Sports", color: "#C1622B" },
];

export function getCategoryTheme(slug: string): CategoryTheme {
  return (
    CATEGORY_THEMES.find((c) => c.slug === slug) ?? {
      slug,
      name: slug,
      color: "#445066",
    }
  );
}
