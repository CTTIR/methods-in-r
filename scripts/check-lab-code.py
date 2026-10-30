#!/usr/bin/env python3
"""Parse every displayed R lab block; a static HTML build does not execute it."""
from pathlib import Path
import re
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
block = re.compile(r"^```(?:\{r[^\n]*\}|r)[ \t]*\n(.*?)^```[ \t]*$", re.M | re.S)
paths = sorted(root.glob("chapters/*/labs/*.Rmd")) + sorted(root.glob("reporting/lab-*.Rmd"))
if not paths:
    raise SystemExit("No lab sources found")
with tempfile.TemporaryDirectory(prefix="methods-lab-syntax-") as tmp:
    for i, path in enumerate(paths):
        chunks = [m.group(1) for m in block.finditer(path.read_text())]
        if not chunks:
            raise SystemExit(f"No R blocks: {path.relative_to(root)}")
        target = Path(tmp) / f"{i}.R"
        target.write_text("\n\n".join(chunks))
    script = Path(tmp) / "parse.R"
    script.write_text('paths <- commandArgs(TRUE); bad <- FALSE; for(p in paths) { tryCatch(parse(p), error=function(e) {message(p, ": ", conditionMessage(e)); bad <<- TRUE}) }; quit(status=as.integer(bad))')
    result = subprocess.run(["Rscript", "--vanilla", str(script), *[str(Path(tmp)/f"{i}.R") for i in range(len(paths))]], capture_output=True, text=True)
    if result.returncode:
        for i,p in enumerate(paths):
            result.stderr=result.stderr.replace(str(Path(tmp)/f"{i}.R"),str(p.relative_to(root)))
        raise SystemExit(result.stderr)
print(f"All {len(paths)} labs parse. This checks syntax, not scientific validity or execution.")
