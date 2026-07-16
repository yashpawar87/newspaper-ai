import type { Metadata } from "next";
import { Fraunces, Inter, IBM_Plex_Mono } from "next/font/google";
import Header from "@/components/Header";
import BreakingTicker from "@/components/BreakingTicker";
import { getTrending } from "@/lib/api";
import "./globals.css";

const fraunces = Fraunces({
  subsets: ["latin"],
  variable: "--font-display",
  weight: ["400", "500", "600"],
});

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-body",
});

const plexMono = IBM_Plex_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  weight: ["400", "500"],
});

export const metadata: Metadata = {
  title: "The Daily Digest",
  description: "A ranked, category-organized digest of India's top news feeds.",
};

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const ticker = await getTrending(10).catch(() => []);

  return (
    <html lang="en">
      <body
        className={`${fraunces.variable} ${inter.variable} ${plexMono.variable} bg-canvas font-body text-ink antialiased`}
      >
        <BreakingTicker articles={ticker} />
        <Header />
        <main>{children}</main>
      </body>
    </html>
  );
}
