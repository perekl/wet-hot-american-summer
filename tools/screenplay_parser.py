"""Parse screenplay text into structured paragraphs."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

PAGE_MARKER = re.compile(r"^===== PAGE (\d+) =====\s*$")
SCENE_HEADING = re.compile(
    r"^(INT\.|EXT\.|INT/EXT\.|I/E\.|EST\.|TITLE:|CREDITS|MONTAGE|OMIT)",
    re.IGNORECASE,
)
TRANSITION = re.compile(
    r"^(CUT TO:|FADE IN:|FADE OUT\.|DISSOLVE TO:|SMASH CUT:|MATCH CUT TO:)",
    re.IGNORECASE,
)
CHARACTER = re.compile(r"^[A-Z][A-Z0-9 '\.\-]{1,34}$")


@dataclass
class Paragraph:
    id: str
    page: int
    scene: str
    type: str
    speaker: str | None
    text: str


def _is_character_line(text: str) -> bool:
    line = text.strip()
    if not line or len(line) > 36:
        return False
    if SCENE_HEADING.match(line) or TRANSITION.match(line):
        return False
    if line.startswith("(") and line.endswith(")"):
        return False
    if line.isupper() and CHARACTER.match(line):
        letters = [c for c in line if c.isalpha()]
        return len(letters) >= 2
    return False


def _is_parenthetical(text: str) -> bool:
    t = text.strip()
    return t.startswith("(") and t.endswith(")")


def _classify(text: str) -> str:
    t = text.strip()
    if SCENE_HEADING.match(t):
        return "scene_heading"
    if TRANSITION.match(t):
        return "transition"
    if _is_parenthetical(t):
        return "parenthetical"
    return "action"


def parse_screenplay_text(text: str) -> list[Paragraph]:
    paragraphs: list[Paragraph] = []
    current_page = 1
    current_scene = ""
    para_num = 0
    buffer: list[str] = []

    def flush_buffer():
        nonlocal para_num, current_scene
        if not buffer:
            return
        body = "\n".join(buffer).strip()
        buffer.clear()
        if not body:
            return
        para_num += 1
        ptype = _classify(body)
        speaker = None
        if ptype == "scene_heading":
            current_scene = body.upper()
        elif _is_character_line(body):
            ptype = "character"
            speaker = body.strip()
        elif ptype == "action":
            pass
        paragraphs.append(
            Paragraph(
                id=f"PAR-{para_num:05d}",
                page=current_page,
                scene=current_scene,
                type=ptype,
                speaker=speaker,
                text=body,
            )
        )

    for raw_line in text.splitlines():
        if match := PAGE_MARKER.match(raw_line):
            flush_buffer()
            current_page = int(match.group(1))
            continue
        if not raw_line.strip():
            flush_buffer()
            continue
        buffer.append(raw_line.rstrip())

    flush_buffer()

    # Second pass: mark dialogue following character blocks
    result: list[Paragraph] = []
    pending_speaker: str | None = None
    for p in paragraphs:
        if p.type == "character":
            pending_speaker = p.speaker
            result.append(p)
            continue
        if pending_speaker and p.type in ("action", "parenthetical"):
            if p.type == "parenthetical":
                result.append(
                    Paragraph(p.id, p.page, p.scene, "parenthetical", pending_speaker, p.text)
                )
            else:
                result.append(
                    Paragraph(p.id, p.page, p.scene, "dialogue", pending_speaker, p.text)
                )
            if p.type == "action" and not _is_parenthetical(p.text):
                pending_speaker = None
            continue
        pending_speaker = None
        result.append(p)
    return result


def parse_screenplay_file(path) -> list[Paragraph]:
    return parse_screenplay_text(path.read_text(encoding="utf-8"))
