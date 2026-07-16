"use client";

import { useState, useCallback, WheelEvent } from "react";

const MIN_ZOOM = 0.6;
const MAX_ZOOM = 1.8;
const STEP = 0.1;

function clamp(value: number): number {
  return Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, Math.round(value * 100) / 100));
}

export default function ZoomablePage({ children }: { children: React.ReactNode }) {
  const [zoom, setZoom] = useState(1);

  const zoomIn = () => setZoom((z) => clamp(z + STEP));
  const zoomOut = () => setZoom((z) => clamp(z - STEP));
  const reset = () => setZoom(1);

  // Ctrl/Cmd + scroll zooms the page, like a PDF viewer. Plain scroll
  // still scrolls the document normally.
  const handleWheel = useCallback((e: WheelEvent<HTMLDivElement>) => {
    if (!e.ctrlKey && !e.metaKey) return;
    e.preventDefault();
    setZoom((z) => clamp(z - e.deltaY * 0.001));
  }, []);

  return (
    <div className="relative pb-24">
      <div
        onWheel={handleWheel}
        className="flex justify-center overflow-x-auto px-4 py-10 sm:px-10"
      >
        <div
          className="shrink-0 origin-top bg-paper shadow-[0_1px_2px_rgba(26,26,23,0.08),0_12px_28px_rgba(26,26,23,0.14)]"
          style={{
            // Roughly A3 portrait width (297mm @ 96dpi), capped so it still
            // fits on smaller viewports. Height is left to grow naturally
            // with article length rather than forced to the A3 ratio,
            // since content length varies a lot between categories.
            width: "min(1122px, 94vw)",
            transform: `scale(${zoom})`,
            transition: "transform 0.15s ease-out",
          }}
        >
          {children}
        </div>
      </div>

      <div className="fixed bottom-5 left-1/2 z-20 flex -translate-x-1/2 items-center gap-1 rounded-full border border-white/50 bg-white/40 px-2 py-1.5 shadow-[0_4px_16px_rgba(26,26,23,0.18)] backdrop-blur-md">
        <button
          onClick={zoomOut}
          aria-label="Zoom out"
          disabled={zoom <= MIN_ZOOM}
          className="flex h-8 w-8 items-center justify-center rounded-full text-lg leading-none text-ink hover:bg-white/40 disabled:opacity-30"
        >
          −
        </button>
        <button
          onClick={reset}
          aria-label="Reset zoom"
          className="min-w-[52px] px-2 font-mono text-xs text-ink/60 hover:text-ink"
        >
          {Math.round(zoom * 100)}%
        </button>
        <button
          onClick={zoomIn}
          aria-label="Zoom in"
          disabled={zoom >= MAX_ZOOM}
          className="flex h-8 w-8 items-center justify-center rounded-full text-lg leading-none text-ink hover:bg-white/40 disabled:opacity-30"
        >
          +
        </button>
      </div>
    </div>
  );
}
