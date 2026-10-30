#!/usr/bin/env python3
"""List only distribution files present in the rendered site."""
import argparse
import json
from pathlib import Path
import zipfile


def collect(root):
    files = []
    candidates = [root / "methods-in-r.pdf", root / "methods-in-r.epub"]
    candidates += sorted((root / "pdf-chapters").glob("*.pdf"))
    for path in candidates:
        if not path.is_file():
            continue
        if path.suffix == ".pdf":
            with path.open("rb") as stream:
                valid = stream.read(5) == b"%PDF-"
        else:
            valid = False
            if zipfile.is_zipfile(path):
                with zipfile.ZipFile(path) as archive:
                    try:
                        valid = (archive.read("mimetype") == b"application/epub+zip"
                                 and "META-INF/container.xml" in archive.namelist()
                                 and archive.testzip() is None)
                    except (KeyError, zipfile.BadZipFile):
                        valid = False
        if valid:
            files.append(path.relative_to(root).as_posix())
    return files


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", type=Path, default=Path("docs"))
    args = parser.parse_args()
    files = collect(args.root)
    (args.root / "downloads.json").write_text(json.dumps(files) + "\n")
    print(f"Inventoried {len(files)} available downloads")
