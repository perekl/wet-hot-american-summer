#!/usr/bin/env python3
"""Generate an annotated screenplay PDF with cue markers per page."""

from __future__ import annotations

import json
import re
import textwrap
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parent.parent
EXTRACT_PATH = ROOT / "assets" / "generated" / "screenplay_extract.txt"
CUES_PATH = ROOT / "data" / "cues.json"
OUTPUT_PATH = ROOT / "docs" / "AnnotatedScreenplay.pdf"

PAGE_MARKER = re.compile(r"^===== PAGE (\d+) =====\s*$")

FX_COLOR = colors.HexColor("#e94560")
BG_COLOR = colors.HexColor("#4a90d9")
BG_STOP_COLOR = colors.HexColor("#f5a623")


def _cue_type(cue: dict) -> str:
    if cue.get("cue_type"):
        return cue["cue_type"]
    if cue.get("category") == "Ambience":
        return "BACKGROUND"
    return "FOREGROUND"


def parse_screenplay_pages(path: Path) -> dict[int, str]:
    pages: dict[int, list[str]] = {}
    current: int | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        match = PAGE_MARKER.match(line)
        if match:
            current = int(match.group(1))
            pages[current] = []
            continue
        if current is not None:
            pages[current].append(line)
    return {num: "\n".join(lines).strip() for num, lines in pages.items()}


def load_cues() -> list[dict]:
    return json.loads(CUES_PATH.read_text(encoding="utf-8"))


def cues_by_page(cues: list[dict]) -> dict[int, list[dict]]:
    grouped: dict[int, list[dict]] = {}
    for cue in cues:
        page = int(cue["page"])
        grouped.setdefault(page, []).append(cue)
    return grouped


def _cue_label(cue: dict) -> str:
    kind = _cue_type(cue)
    if kind == "BACKGROUND" and cue.get("category") == "Silence":
        return f"BG STOP  {cue['id']}  {cue['name']}"
    if kind == "BACKGROUND":
        return f"BG START  {cue['id']}  {cue['name']}"
    return f"FX  {cue['id']}  {cue['name']}"


def _cue_color(cue: dict):
    kind = _cue_type(cue)
    if kind == "BACKGROUND" and cue.get("category") == "Silence":
        return BG_STOP_COLOR
    if kind == "BACKGROUND":
        return BG_COLOR
    return FX_COLOR


def generate_annotated_screenplay(
    output_path: Path = OUTPUT_PATH,
    extract_path: Path = EXTRACT_PATH,
    cues_path: Path = CUES_PATH,
) -> Path:
    if not extract_path.exists():
        raise FileNotFoundError(f"Missing screenplay extract: {extract_path}")
    if not cues_path.exists():
        raise FileNotFoundError(f"Missing cues: {cues_path}")

    pages = parse_screenplay_pages(extract_path)
    cues = load_cues() if cues_path.exists() else []
    grouped = cues_by_page(cues)
    max_page = max(pages.keys()) if pages else 90

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(output_path), pagesize=letter)
    width, height = letter
    margin_x = 0.65 * inch
    body_width = width - 2 * margin_x
    body_top = height - 1.15 * inch

    for page_num in range(1, max_page + 1):
        page_cues = grouped.get(page_num, [])
        y = height - 0.45 * inch

        pdf.setFont("Helvetica-Bold", 9)
        pdf.setFillColor(colors.HexColor("#666666"))
        pdf.drawString(margin_x, y, f"Page {page_num}")
        y -= 0.18 * inch

        for cue in page_cues:
            label = _cue_label(cue)
            color = _cue_color(cue)
            pdf.setFillColor(color)
            pdf.roundRect(margin_x, y - 0.12 * inch, body_width, 0.16 * inch, 3, fill=1, stroke=0)
            pdf.setFillColor(colors.white)
            pdf.setFont("Helvetica-Bold", 7.5)
            pdf.drawString(margin_x + 6, y - 0.02 * inch, label[:105])
            y -= 0.2 * inch

        y -= 0.05 * inch
        pdf.setStrokeColor(colors.HexColor("#cccccc"))
        pdf.line(margin_x, y, width - margin_x, y)
        y -= 0.12 * inch

        body = pages.get(page_num, "(no screenplay text for this page)")
        pdf.setFillColor(colors.black)
        pdf.setFont("Courier", 8.5)
        for paragraph in body.split("\n"):
            if not paragraph.strip():
                y -= 0.12 * inch
                continue
            for line in textwrap.wrap(paragraph, width=95):
                if y < 0.65 * inch:
                    break
                pdf.drawString(margin_x, y, line)
                y -= 0.13 * inch

        pdf.showPage()

    pdf.save()
    return output_path


def main():
    path = generate_annotated_screenplay()
    print(f"Generated annotated screenplay: {path}")


if __name__ == "__main__":
    main()
