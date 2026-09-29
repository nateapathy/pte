#!/usr/bin/env python3
"""Collect the form data embedded in Pragmatic Trial Evaluation PDFs into a CSV.

Each PDF downloaded from the form carries its responses as JSON inside the
PDF's XMP metadata. This script pulls that JSON out of every PDF it is given
(files or folders) and writes one row per evaluation. Standard library only.

    python3 extract_pte.py path/to/pdfs/ -o evaluations.csv
"""
import argparse
import csv
import html
import json
import re
import sys
import zlib
from pathlib import Path

TAG = re.compile(rb"<jspdf:metadata>(.*?)</jspdf:metadata>", re.S)
STREAM = re.compile(rb"stream\r?\n(.*?)\r?\nendstream", re.S)


def read_record(path):
    raw = path.read_bytes()
    m = TAG.search(raw)
    if not m:  # metadata stream may be compressed if the PDF was re-saved elsewhere
        for s in STREAM.finditer(raw):
            try:
                m = TAG.search(zlib.decompress(s.group(1)))
            except zlib.error:
                continue
            if m:
                break
    if not m:
        return None
    rec = json.loads(html.unescape(m.group(1).decode("utf-8")))
    return rec if rec.get("schema") == "pte-evaluation" else None


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("paths", nargs="+", type=Path, help="PDF files and/or folders")
    ap.add_argument("-o", "--out", type=Path, default=Path("pte_evaluations.csv"))
    args = ap.parse_args()

    pdfs = []
    for p in args.paths:
        pdfs += sorted(p.rglob("*.pdf")) if p.is_dir() else [p]

    rows, skipped = [], []
    for pdf in pdfs:
        rec = read_record(pdf)
        if rec is None:
            skipped.append(pdf)
        else:
            rows.append({"source_file": pdf.name, **rec})

    if rows:
        cols = list(dict.fromkeys(k for r in rows for k in r))
        with args.out.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(rows)
    print(f"{len(rows)} evaluation(s) written to {args.out}")
    for pdf in skipped:
        print(f"  skipped (no embedded form data): {pdf}", file=sys.stderr)


if __name__ == "__main__":
    main()
