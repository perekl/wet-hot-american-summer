#!/usr/bin/env python3
"""Import screenplay extract/PDF into data/script.json with cue placements."""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "app"))

from screenplay_parser import parse_screenplay_file, parse_screenplay_text  # noqa: E402

EXTRACT_PATH = ROOT / "assets" / "generated" / "screenplay_extract.txt"
CUES_PATH = ROOT / "data" / "cues.json"
OUTPUT_PATH = ROOT / "data" / "script.json"


def _extract_pdf_text(pdf_path: Path) -> str:
    try:
        import fitz
    except ImportError as exc:
        raise SystemExit("pymupdf required for PDF import: pip install pymupdf") from exc
    doc = fitz.open(str(pdf_path))
    parts = []
    for i, page in enumerate(doc, 1):
        parts.append(f"===== PAGE {i} =====")
        parts.append(page.get_text())
    doc.close()
    return "\n".join(parts)


def _best_paragraph(cue: dict, paragraphs: list, by_page: dict) -> str:
    page = int(cue.get("page", 1))
    paras = by_page.get(page, [])
    trigger = cue.get("trigger", "").strip().strip('"').lower()
    best_id = None
    best_score = 0
    for p in paras:
        text = p.text.lower()
        score = 0
        if trigger and trigger in text:
            score = len(text) + 100
        elif trigger and text in trigger:
            score = len(text) + 50
        elif trigger:
            score = sum(1 for w in trigger.split() if len(w) > 3 and w in text) * 10
        if score > best_score:
            best_score = score
            best_id = p.id
    if best_id:
        return best_id
    if paras:
        return paras[-1].id
    return paragraphs[0].id if paragraphs else ""


def import_screenplay(
    *,
    extract_path: Path = EXTRACT_PATH,
    pdf_path: Path | None = None,
    cues_path: Path = CUES_PATH,
    output_path: Path = OUTPUT_PATH,
) -> Path:
    if pdf_path and pdf_path.is_file():
        text = _extract_pdf_text(pdf_path)
        source = str(pdf_path)
    elif extract_path.is_file():
        text = extract_path.read_text(encoding="utf-8")
        source = str(extract_path)
    else:
        raise FileNotFoundError("No screenplay extract or PDF found")

    paragraphs = parse_screenplay_text(text)
    cues = json.loads(cues_path.read_text(encoding="utf-8"))
    by_page: dict[int, list] = {}
    for p in paragraphs:
        by_page.setdefault(p.page, []).append(p)

    placements = []
    for i, cue in enumerate(cues):
        after = _best_paragraph(cue, paragraphs, by_page)
        placements.append({
            "cue_id": cue["id"],
            "after_paragraph_id": after,
            "order": 0,
        })

    payload = {
        "version": 1,
        "title": "Wet Hot American Summer",
        "source": source,
        "paragraphs": [asdict(p) for p in paragraphs],
        "placements": placements,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output_path


def main():
  import argparse
  parser = argparse.ArgumentParser(description="Import screenplay into data/script.json")
  parser.add_argument("--pdf", type=Path, help="Optional PDF path (overrides extract)")
  args = parser.parse_args()
  path = import_screenplay(pdf_path=args.pdf)
  data = json.loads(path.read_text())
  print(f"Imported {len(data['paragraphs'])} paragraphs, {len(data['placements'])} cue placements")
  print(f"Wrote {path}")


if __name__ == "__main__":
    main()
