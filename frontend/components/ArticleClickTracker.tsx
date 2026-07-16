"use client";

import { useEffect, useRef } from "react";
import { registerClick } from "@/lib/api";

export default function ArticleClickTracker({ articleId }: { articleId: number }) {
  const fired = useRef(false);

  useEffect(() => {
    if (!fired.current) {
      fired.current = true;
      registerClick(articleId);
    }
  }, [articleId]);

  return null;
}
