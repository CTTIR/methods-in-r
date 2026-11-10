# Catch missing symbols before rendering the complete reference book.
engine <- Sys.which("xelatex")
if (!nzchar(engine)) stop("xelatex is required for the PDF font check")
folder <- tempfile("book-fonts-")
dir.create(folder)
tex <- file.path(folder, "symbols.tex")
pandoc <- Sys.which("pandoc")
if (!nzchar(pandoc)) pandoc <- file.path(rmarkdown::find_pandoc()$dir, "pandoc")
md <- file.path(folder, "inline.md")
fragment <- file.path(folder, "inline.tex")
writeLines('## Dependency `renv`\n\n`pheatmap(as.matrix(dist(t(assay(vsd)))))` and `x_name$group %in% c("a", "b")`', md)
stopifnot(system2(pandoc, c("-f", "markdown", "-t", "latex",
  "--lua-filter=scripts/wrap-inline-code.lua", shQuote(md), "-o", shQuote(fragment))) == 0L)
writeLines(c(
  "\\documentclass{book}", "\\usepackage{amsmath}", "\\usepackage{unicode-math}", "\\usepackage{hyperref}",
  "\\input{style/preamble.tex}", "\\begin{document}",
  "\\tableofcontents", "\\setcounter{page}{2555}",
  "\\addcontentsline{toc}{subsection}{\\protect\\numberline{23.100.11}Long method name}",
  "Greek and mathematical symbols: α μ β Δ σ λ π ρ χ γ τ ν κ δ ε ⁵ ₀ ₁ ₂ ∈ ≈ ≠ ≤ ≥ 𝛬 𝜃.",
  "\\(\\theta = \\boldsymbol{\\Lambda}\\) and ν₁, ν₂.",
  "\\begin{minipage}{2in}", readLines(fragment), "\\end{minipage}",
  "\\begin{verbatim}", "# Check: P(A and B) ≈ P(A) * P(B)",
  "\\end{verbatim}", "\\end{document}"
), tex, useBytes = TRUE)
for (pass in 1:2) {
status <- system2(engine, c("-halt-on-error", "-interaction=batchmode",
  paste0("-output-directory=", shQuote(folder)), shQuote(tex)),
  stdout = file.path(folder, "engine-output.txt"), stderr = file.path(folder, "engine-error.txt"))
  if (status != 0L) stop("PDF fixture compilation failed; inspect ", folder)
}

log <- file.path(folder, "symbols.log")
if (status != 0L || !file.exists(log)) stop("PDF font fixture failed; inspect ", folder)
lines <- readLines(log, warn = FALSE)
if (any(grepl("Missing character:|Overfull", lines))) {
  stop("PDF font fixture lost symbols; inspect ", log)
}
stopifnot(file.info(file.path(folder, "symbols.pdf"))$size > 0)
unlink(folder, recursive = TRUE)
cat("PDF text and code fonts preserve the required Greek and mathematical symbols.\n")
