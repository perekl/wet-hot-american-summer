"""Cue-to-script-page indexing for PDF sync."""

from __future__ import annotations

from collections import defaultdict


def cue_type(cue: dict) -> str:
    if cue.get("cue_type"):
        return cue["cue_type"]
    if cue.get("category") == "Ambience":
        return "BACKGROUND"
    return "FOREGROUND"


def is_background_stop(cue: dict) -> bool:
    return cue_type(cue) == "BACKGROUND" and cue.get("category") == "Silence"


def build_page_index(cues: list[dict]) -> dict[int, list[dict]]:
    by_page: dict[int, list[dict]] = defaultdict(list)
    for cue in cues:
        by_page[int(cue["page"])].append(cue)
    return dict(by_page)


def cues_on_page(cues: list[dict], page: int) -> list[dict]:
    return [c for c in cues if int(c["page"]) == page]


def queue_index_for_page(cues: list[dict], page: int) -> int:
    """Index in queue for the best cue match when script shows a page."""
    for i, cue in enumerate(cues):
        if int(cue["page"]) == page:
            return i
    for i in range(len(cues) - 1, -1, -1):
        if int(cues[i]["page"]) <= page:
            return i
    return 0


def search_snippets(trigger: str) -> list[str]:
    """Candidate text snippets to locate a cue in PDF page text."""
    text = trigger.strip().strip('"').strip("'")
    if not text:
        return []
    snippets: list[str] = []
    snippets.append(text[: min(60, len(text))])
    if len(text) > 24:
        snippets.append(text[:24])
    words = text.split()
    if len(words) >= 4:
        snippets.append(" ".join(words[:4]))
    if len(words) >= 2:
        snippets.append(" ".join(words[:2]))
    # dedupe preserving order
    seen: set[str] = set()
    out: list[str] = []
    for s in snippets:
        key = s.lower()
        if key and key not in seen and len(key) >= 4:
            seen.add(key)
            out.append(s)
    return out
