import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Base palette — "Paper & Ink"
        paper: "#f6f4ee", // the page itself
        ink: "#1a1a17", // headlines/body text
        "ink-secondary": "#5c5b54", // timestamps, secondary info
        canvas: "#dcd8cc", // outer background the paper "floats" on

        // UI-specific accents (category colors stay inline via
        // lib/categories.ts, since they're data-driven per section)
        live: "#e4302c", // breaking-news ticker badge — deliberately
        // brighter/more saturated than the Top Stories deep red so it
        // reads as "urgent" rather than "categorized"
        accent: "#b23a2f", // kept as a fallback/default accent
      },
      fontFamily: {
        display: ["var(--font-display)", "serif"],
        body: ["var(--font-body)", "sans-serif"],
        mono: ["var(--font-mono)", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
