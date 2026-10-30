knitr::opts_chunk$set(
  echo       = TRUE,
  eval       = FALSE,
  message    = FALSE,
  warning    = FALSE,
  cache      = FALSE,
  fig.align  = "center",
  fig.width  = 7,
  fig.height = 4.5,
  fig.retina = 2,
  dpi        = 300,
  out.width  = "90%",
  comment    = "#>"
)

options(
  scipen = 999,
  digits = 3,
  knitr.kable.NA = "—"
)

set.seed(42)

# Citation files copy hook — see refinement §3.3
if (file.exists("citation.bib")) {
  dir.create("docs/citation-files", recursive = TRUE, showWarnings = FALSE)
  file.copy("citation.bib", "docs/citation-files/citation.bib", overwrite = TRUE)
  if (file.exists("citation.ris")) {
    file.copy("citation.ris", "docs/citation-files/citation.ris", overwrite = TRUE)
  }
}

if (requireNamespace("ggplot2", quietly = TRUE)) {
  ggplot2::theme_set(
    ggplot2::theme_minimal(base_size = 12) +
      ggplot2::theme(
        plot.title.position   = "plot",
        plot.caption.position = "plot",
        plot.caption          = ggplot2::element_text(hjust = 0, color = "#666"),
        panel.grid.minor      = ggplot2::element_blank()
      )
  )
}
