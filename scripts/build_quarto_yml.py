#!/usr/bin/env python3
"""Regenerate _quarto.yml with part-per-chapter nesting.

Each chapter index becomes a ``part:`` entry and its method pages + labs
become ``chapters:`` underneath, so the sidebar shows a collapsible tree
instead of 675 flat numbered items.

Quarto 1.7.32 does not support ``file: + sections:`` in book format,
so we use ``part: filepath`` as the work-around.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / "_data" / "manifest.json").read_text(encoding="utf-8"))

CHAPTER_ORDER = [
    "01-foundations", "02-descriptives", "03-probability", "04-inferential",
    "05-power", "06-visualisation", "07-regression", "08-multivariate",
    "09-timeseries", "10-bayesian", "11-survival", "12-bioinformatics",
    "13-ml", "14-clinical", "15-metaanalysis", "16-design",
]


def chapter_files(chapter: str) -> tuple[list[str], list[str]]:
    methods = sorted(
        e["target"] for e in MANIFEST["entries"]
        if e["chapter"] == chapter and e["kind"] == "method"
    )
    labs = sorted(
        e["target"] for e in MANIFEST["entries"]
        if e["chapter"] == chapter and e["kind"] == "lab"
    )
    return methods, labs


def main() -> None:
    out: list[str] = []
    out.append("project:")
    out.append("  type: book")
    out.append("  output-dir: docs")
    out.append("")
    out.append("book:")
    out.append('  title: "Methods in R"')
    out.append('  subtitle: "A Topic Reference for Biomedical Research and Peer Review"')
    out.append("  author:")
    out.append('    name: "R. Heller"')
    out.append('    orcid: "0000-0001-8006-9742"')
    out.append("  date: today")
    out.append('  description: "A bench reference for biomedical authors and peer reviewers — every common method covered with R code, diagnostics, and reviewer-facing red flags."')
    out.append("  site-url: https://cttir.github.io/methods-in-r/")
    out.append("  repo-url: https://github.com/CTTIR/methods-in-r/")
    out.append("  repo-actions: [edit, source, issue]")
    out.append("  search: true")
    out.append("  page-navigation: true")
    out.append("  back-to-top-navigation: true")
    out.append("  downloads: [pdf]")
    out.append("  sidebar:")
    out.append("    style: docked")
    out.append("    collapse-level: 1")
    out.append("")
    out.append("  chapters:")
    out.append("    - index.qmd")
    out.append("    - how-to-use.qmd")
    out.append("    - ch00-find-your-method.qmd")

    for ch in CHAPTER_ORDER:
        methods, labs = chapter_files(ch)
        out.append(f"    - part: chapters/{ch}/index.qmd")
        out.append("      chapters:")
        for m in methods:
            out.append(f"        - {m}")
        for lab in labs:
            out.append(f"        - {lab}")

    out.append("    - part: reporting/index.qmd")
    out.append("      chapters:")
    out.append("        - reporting/strobe.qmd")
    out.append("        - reporting/consort.qmd")
    out.append("        - reporting/tripod-ai.qmd")
    out.append("        - reporting/prisma.qmd")
    out.append("        - reporting/arrive.qmd")
    out.append("        - reporting/lab-explanation-vs-prediction-reporting.qmd")

    out.append("    - references.qmd")
    out.append("")
    out.append("  appendices:")
    out.append("    - appendices/A-research-workflow.qmd")
    out.append("    - appendices/B-glossary.qmd")
    out.append("    - appendices/C-common-errors.qmd")
    out.append("    - appendices/D-writing-a-report.qmd")
    out.append("    - appendices/E-cheatsheets.qmd")
    out.append("")
    out.append("bibliography: references.bib")
    out.append("csl: https://www.zotero.org/styles/apa")
    out.append("")
    out.append("format:")
    out.append("  html:")
    out.append("    theme:")
    out.append("      light: [cosmo]")
    out.append("      dark: [darkly]")
    out.append("    css: styles.css")
    out.append("    code-copy: true")
    out.append("    code-overflow: wrap")
    out.append("    code-link: true")
    out.append("    toc: true")
    out.append("    toc-depth: 3")
    out.append("    fig-cap-location: bottom")
    out.append("    tbl-cap-location: top")
    out.append("    include-after-body:")
    out.append("      - _includes/page-pdf.html")
    out.append("  pdf:")
    out.append("    documentclass: scrbook")
    out.append("    papersize: a4")
    out.append("    geometry: margin=2.5cm")
    out.append('    fig-pos: "H"')
    out.append("")
    out.append("execute:")
    out.append("  freeze: auto")
    out.append("")

    (ROOT / "_quarto.yml").write_text("\n".join(out), encoding="utf-8")

    n_pages = sum(
        1 for line in out
        if line.strip().startswith("- chapters/")
        or line.strip().startswith("- reporting/")
        or line.strip().startswith("- appendices/")
    )
    print(f"wrote _quarto.yml — 16 chapter-parts, {n_pages} sub-pages")


if __name__ == "__main__":
    main()
