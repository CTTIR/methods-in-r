#!/usr/bin/env python3
"""Convert lab .qmd files into static (non-executed) form.

Two transformations:
  1. ` ```{r [opts]} `  →  ` ```r `       (display-only chunks)
  2. inline `r EXPR`    →  `EXPR`         (display-only inline)

This makes labs render as a static reference without requiring a
running R + renv environment. The R code text is preserved verbatim;
only the chunk-engine fences are converted. Idempotent.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CHUNK_RE = re.compile(r"^```\{([a-zA-Z][a-zA-Z0-9_]*)[^}\n]*\}[ \t]*$", re.M)
INLINE_RE = re.compile(r"(?<!`)`(r|python|julia)[ \t]+([^`\n]+?)`(?!`)")


def transform(text: str) -> str:
    text = CHUNK_RE.sub(lambda m: f"```{m.group(1)}", text)
    text = INLINE_RE.sub(r"`\2`", text)
    return text


def main() -> None:
    targets = list(ROOT.glob("chapters/*/labs/*.qmd"))
    targets += list(ROOT.glob("reporting/lab-*.qmd"))
    n = 0
    for p in targets:
        old = p.read_text(encoding="utf-8")
        new = transform(old)
        if new != old:
            p.write_text(new, encoding="utf-8")
            n += 1
    print(f"converted {n}/{len(targets)} lab files to static form")


if __name__ == "__main__":
    main()
