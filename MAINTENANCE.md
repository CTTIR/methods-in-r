# Maintenance record — 30 October 2026

## Purpose and release criteria

This book is a biomedical methods reference for authors and peer reviewers, with
569 method entries and 80 practical labs. The maintenance strategy is to restore
source integrity first, make chapter/method navigation dependable, provide an
honest HTML reading path, then qualify available distribution formats. Acceptance
requires preserved lab statements, unique method anchors, a render using the
configured bs4 theme, working local links, and a real chooser-to-reviewer reading
journey. A static reference build does not certify every statistical procedure.

## Findings and completed work

- High — `scripts/static_labs.py`: a conversion expression consumed the first R
  statement after a chunk header. Restore 364 statements across 79 labs from
  the original source revision, and protect the converter against recurrence.
  All 80 combined lab scripts parse; the tidy-data and import/join labs were
  executed. Existing source and provenance were retained.
- High — conversion dropped 649 method/lab titles and four part entries, leaving
  content difficult to locate. Restore titles from the repository manifest,
  preserve unique anchors, and repair heading depth outside code blocks.
- High — 4,585 cross-chapter references were malformed or pointed to unavailable
  `.Rmd` pages. Use bookdown's supported anchor links; source and rendered gates
  now check their targets. A tiny independent two-chapter render verified the
  link syntax before applying it across the book.
- High — all 569 For Reviewers sections contained only empty template prompts,
  while the reading guide promised specific review advice. Replace the stubs
  with a substantive shared checklist, links to each method's assumptions or
  theory and practical tips, and explicit editorial status. Correct the reading
  guide's obsolete Quarto command and unsupported claim that every example runs.
- Medium — dark-mode tables inherited low-contrast Bootstrap cell text. Use the
  active theme's text color. The decision SVG's `root` style also reached all
  labels; scope the question-node class correctly and verify readable colors.
- Medium — the welcome heading was inside an HTML wrapper, confusing chapter
  splitting; duplicate part handling also affected layout. Restore a proper
  top-level heading and remove the duplicate script behavior.
- Medium — separate `{-}` and `{#id}` blocks printed the former literally and
  numbered front matter. Use one unnumbered attribute block; keep the method
  chooser unnumbered so numbered teaching chapters start with Foundations.
- Medium — the static method chooser displayed Mermaid source. Maintain its
  editable `.mmd` source and a rendered SVG with real text, so reading needs no
  JavaScript diagram engine. The full-size image and lookup table are linked.
- Medium — invented download links could imply failed PDF/EPUB builds succeeded.
  Inventory only actual files with valid PDF/EPUB signatures, and show those
  links in the reading interface. Add inventory tests and a final CI link gate.
- Medium — the generated EPUB had 21 broken links after chapter splitting,
  including numeric references and citation attachments. Add an atomic finalizer
  that resolves unique anchors, links the already embedded diagram and packages
  citation text as readable XHTML. Unknown targets fail without changing the
  archive. Tests protect cross-chapter navigation, exact citation text, repeat
  operation and preservation on failure.

## Observed validation

R 4.6.1, bookdown 0.47 and Pandoc on macOS ARM64. Six source unit tests pass; all 80
lab scripts parse and two data-manipulation labs execute successfully. The
configured HTML build passed in 758.89 seconds: 38 pages and 25,581 local
references, with zero broken files or anchors. The final EPUB rendered in 33.69
seconds and passed ZIP CRC/mimetype checks, with 51 archive members, 42 XHTML
files and 36,714 local references, all resolving after finalization. All 786
maintained format inputs matched the isolated EPUB build copy.

Actual desktop/mobile browser checks passed for the chooser diagram, chapter
navigation, reviewer-to-shared-checklist link, theme switching, dark table and
navigation colors, and available downloads, with no page errors. Screenshots and
the standalone diagram were inspected. The last stylesheet adjustment was copied
to the HTML output and exercised in the browser; it did not require rerunning R.

Build warnings about many input files sharing fewer first-level headings are
expected: individual methods are sections within their topic chapters. The
Pandoc MathJax option deprecation remains visible; no errors were suppressed.

## First use, limitations and next action

README.md gives prerequisites, exact dependency, test, render, inventory and local
server commands. Read `docs/index.html` through that server. Use the chooser,
follow a chapter link, then a method and its For Reviewers section. The verified EPUB uses its own format build, finalizer and refreshed download
inventory. Optional PDF requires separate qualification.

The book deliberately renders displayed code with evaluation disabled. Only the
specified labs were executed; neither HTML success nor syntax checks establish
scientific validity of all 569 methods, analyses, example outputs or reporting
recommendations. Independent scientific review, method-specific reviewer notes and broader lab
execution are the next substantive milestones. PDF additionally requires a TeX environment; no PDF
or hosted CI/deployment is claimed. Historical author/provenance notices remain.

Review the local candidate, run the prepared CI on the selected revision, and
qualify any extra distribution format before publishing. Logs and source repair
receipts are in the dated portfolio audit's `methods-in-r/` directory.
