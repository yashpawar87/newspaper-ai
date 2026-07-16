"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { CATEGORY_THEMES } from "@/lib/categories";

export default function Header() {
  const pathname = usePathname();

  return (
    <header className="border-b-2 border-ink bg-paper">
      <div className="mx-auto max-w-6xl px-4 pt-6 pb-3 text-center">
        <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-ink/50">
          {new Date().toLocaleDateString("en-IN", {
            weekday: "long",
            year: "numeric",
            month: "long",
            day: "numeric",
          })}
        </p>
        <Link href="/">
          <h1 className="mt-1 font-display text-4xl font-medium tracking-tight text-ink sm:text-5xl">
            The Daily Digest
          </h1>
        </Link>
      </div>

      <nav className="mx-auto max-w-6xl px-4">
        <ul className="flex flex-wrap justify-center gap-1 border-t border-ink/15 pt-2 pb-2 text-sm">
          {CATEGORY_THEMES.map((cat) => {
            const isActive = pathname === `/${cat.slug}`;
            return (
              <li key={cat.slug}>
                <Link
                  href={`/${cat.slug}`}
                  className="relative inline-block px-3 py-1.5 font-medium transition-colors"
                  style={{ color: isActive ? cat.color : "var(--color-ink-secondary)" }}
                >
                  {isActive && (
                    <span
                      aria-hidden="true"
                      className="absolute inset-x-2 -bottom-[9px] h-[3px]"
                      style={{ backgroundColor: cat.color }}
                    />
                  )}
                  {cat.name}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
    </header>
  );
}
