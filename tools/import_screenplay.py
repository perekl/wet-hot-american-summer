#!/usr/bin/env python3
"""Import screenplay extract/PDF into data/script.json with cue placements."""

from __future__ import annotations

import json
import re
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


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().strip('"').lower())


def _trigger_score(trigger: str, text: str) -> int:
    if not trigger:
        return 0
    t = _norm(trigger)
    tx = _norm(text)
    if not t:
        return 0
    if t in tx:
        return 2000 - min(len(tx), 500)
    if tx in t:
        return 1500 - min(len(tx), 500)
    words = [w for w in re.findall(r"[a-z0-9']+", t) if len(w) > 2]
    if not words:
        return 0
    hits = sum(1 for w in words if w in tx)
    if hits == 0:
        return 0
    phrase_bonus = 0
    for n in range(min(4, len(words)), 1, -1):
        for i in range(len(words) - n + 1):
            phrase = " ".join(words[i : i + n])
            if phrase in tx:
                phrase_bonus = max(phrase_bonus, n * 80)
                break
        if phrase_bonus:
            break
    ratio = hits / len(words)
    return int(phrase_bonus + ratio * 150 + hits * 10)


def _scene_score(scene: str, para_scene: str, para_text: str) -> int:
    if not scene:
        return 0
    s = scene.strip().upper()
    ps = (para_scene or "").strip().upper()
    body = para_text.upper()
    if ps == s:
        return 25
    tail = s.split(" - ")[-1].strip() if " - " in s else s
    if tail and len(tail) > 4 and tail in ps:
        return 15
    if s in body:
        return 10
    return 0


def _page_bonus(cue_page: int, para_page: int) -> int:
    diff = abs(cue_page - para_page)
    if diff == 0:
        return 30
    if diff == 1:
        return 10
    return -5 * diff


def _type_penalty(para_type: str) -> int:
    if para_type in ("scene_heading", "transition"):
        return -80
    if para_type == "character":
        return -40
    return 0


def _best_paragraph(cue: dict, paragraphs: list, by_page: dict) -> str:
    cue_page = int(cue.get("page", 1))
    trigger = cue.get("trigger", "")
    scene = cue.get("scene", "")
    name = cue.get("name", "")
    best_id = None
    best_score = -9999
    for p in paragraphs:
        score = _trigger_score(trigger, p.text)
        score += _scene_score(scene, p.scene, p.text)
        score += _page_bonus(cue_page, p.page)
        score += _type_penalty(p.type)
        if name:
            name_words = [
                w for w in re.findall(r"[a-z0-9']+", name.lower()) if len(w) > 4
            ]
            score += sum(3 for w in name_words if w in p.text.lower())
        if score > best_score:
            best_score = score
            best_id = p.id
    if best_score > 0 and best_id:
        return best_id
    page_paras = by_page.get(cue_page, [])
    for p in reversed(page_paras):
        if p.type in ("action", "dialogue"):
            return p.id
    if page_paras:
        return page_paras[-1].id
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
    para_order: dict[str, int] = {}
    for cue in cues:
        after = _best_paragraph(cue, paragraphs, by_page)
        order = para_order.get(after, 0)
        para_order[after] = order + 1
        placements.append({
            "cue_id": cue["id"],
            "after_paragraph_id": after,
            "order": order,
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
