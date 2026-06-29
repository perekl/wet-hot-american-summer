"""Editable screenplay project model (data/script.json + cues)."""

from __future__ import annotations

import json
import re
from copy import deepcopy
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = ROOT / "data" / "script.json"
CUES_PATH = ROOT / "data" / "cues.json"
ASSETS_PATH = ROOT / "data" / "assets.json"

CUE_ID_RE = re.compile(r"^CUE-(\d+)$")


@dataclass
class Paragraph:
    id: str
    page: int
    scene: str
    type: str
    speaker: str | None
    text: str


@dataclass
class Placement:
    cue_id: str
    after_paragraph_id: str
    order: int = 0


def _cue_type(cue: dict) -> str:
    if cue.get("cue_type"):
        return cue["cue_type"]
    if cue.get("category") == "Ambience":
        return "BACKGROUND"
    return "FOREGROUND"


def _marker_kind(cue: dict) -> str:
    if _cue_type(cue) == "BACKGROUND":
        if cue.get("category") == "Silence":
            return "BG_STOP"
        return "BG"
    if cue.get("category") == "Music" or cue.get("playback_mode") == "Music":
        return "MUSIC"
    return "FX"


class ScriptProject:
    def __init__(self, root: Path = ROOT):
        self.root = root
        self.script_path = root / "data" / "script.json"
        self.cues_path = root / "data" / "cues.json"
        self.assets_path = root / "data" / "assets.json"
        self.title = "Wet Hot American Summer"
        self.source = ""
        self.paragraphs: list[Paragraph] = []
        self.placements: list[Placement] = []
        self.cues: list[dict] = []
        self.assets_by_id: dict[str, dict] = {}
        self._paragraph_index: dict[str, Paragraph] = {}

    def script_exists(self) -> bool:
        return self.script_path.is_file()

    def load(self) -> None:
        if self.script_path.is_file():
            data = json.loads(self.script_path.read_text(encoding="utf-8"))
            self.title = data.get("title", self.title)
            self.source = data.get("source", "")
            self.paragraphs = [Paragraph(**p) for p in data.get("paragraphs", [])]
            self.placements = [Placement(**p) for p in data.get("placements", [])]
        self.cues = json.loads(self.cues_path.read_text(encoding="utf-8"))
        if self.assets_path.is_file():
            assets = json.loads(self.assets_path.read_text(encoding="utf-8"))
            self.assets_by_id = {a["id"]: a for a in assets}
        self._rebuild_index()
        if not self.placements and self.paragraphs:
            self._placements_from_cue_pages()

    def save_script(self) -> None:
        payload = {
            "version": 1,
            "title": self.title,
            "source": self.source,
            "paragraphs": [asdict(p) for p in self.paragraphs],
            "placements": [asdict(p) for p in self.placements],
        }
        self.script_path.parent.mkdir(parents=True, exist_ok=True)
        self.script_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _rebuild_index(self) -> None:
        self._paragraph_index = {p.id: p for p in self.paragraphs}

    def paragraph(self, paragraph_id: str) -> Paragraph | None:
        return self._paragraph_index.get(paragraph_id)

    def cues_after(self, paragraph_id: str) -> list[dict]:
        ids = [
            pl.cue_id
            for pl in sorted(
                [p for p in self.placements if p.after_paragraph_id == paragraph_id],
                key=lambda x: (x.order, x.cue_id),
            )
        ]
        by_id = {c["id"]: c for c in self.cues}
        return [by_id[cid] for cid in ids if cid in by_id]

    def placement_for(self, cue_id: str) -> Placement | None:
        for pl in self.placements:
            if pl.cue_id == cue_id:
                return pl
        return None

    def ordered_cue_ids(self) -> list[str]:
        order: list[tuple[int, int, int, str]] = []
        para_seq = {p.id: i for i, p in enumerate(self.paragraphs)}
        for pl in self.placements:
            seq = para_seq.get(pl.after_paragraph_id, 999999)
            para = self.paragraph(pl.after_paragraph_id)
            page = para.page if para else 999
            order.append((page, seq, pl.order, pl.cue_id))
        order.sort()
        return [cid for *_rest, cid in order]

    def get_cues_sorted(self) -> list[dict]:
        by_id = {c["id"]: c for c in self.cues}
        ordered = [by_id[cid] for cid in self.ordered_cue_ids() if cid in by_id]
        placed = {c["id"] for c in ordered}
        for c in self.cues:
            if c["id"] not in placed:
                ordered.append(c)
        for i, cue in enumerate(ordered):
            cue["index"] = i
        return ordered

    def _placements_from_cue_pages(self) -> None:
        """Fallback when script has no placements yet."""
        by_page: dict[int, list[Paragraph]] = {}
        for p in self.paragraphs:
            by_page.setdefault(p.page, []).append(p)
        self.placements = []
        for cue in self.cues:
            page = int(cue.get("page", 1))
            paras = by_page.get(page, [])
            after = self._best_paragraph_for_trigger(cue, paras)
            if not after and paras:
                after = paras[-1].id
            elif not after and self.paragraphs:
                after = self.paragraphs[0].id
            if after:
                self.placements.append(Placement(cue["id"], after, 0))

    def _best_paragraph_for_trigger(self, cue: dict, paragraphs: list[Paragraph]) -> str | None:
        if cue.get("paragraph_id") and self.paragraph(cue["paragraph_id"]):
            return cue["paragraph_id"]
        trigger = cue.get("trigger", "").strip().strip('"').lower()
        if not trigger or not paragraphs:
            return None
        best_id = None
        best_score = 0
        for p in paragraphs:
            text = p.text.lower()
            score = 0
            if trigger in text:
                score = len(text) + 100
            elif text in trigger:
                score = len(text) + 50
            else:
                words = [w for w in trigger.split() if len(w) > 3]
                score = sum(1 for w in words if w in text) * 10
            if score > best_score:
                best_score = score
                best_id = p.id
        return best_id

    def move_cue(self, cue_id: str, after_paragraph_id: str, order: int | None = None) -> None:
        self.placements = [p for p in self.placements if p.cue_id != cue_id]
        if order is None:
            order = len([p for p in self.placements if p.after_paragraph_id == after_paragraph_id])
        self.placements.append(Placement(cue_id, after_paragraph_id, order))
        self._sync_cue_from_placement(cue_id)

    def reorder_cue(self, cue_id: str, direction: int) -> None:
        pl = self.placement_for(cue_id)
        if not pl:
            return
        siblings = sorted(
            [p for p in self.placements if p.after_paragraph_id == pl.after_paragraph_id],
            key=lambda x: (x.order, x.cue_id),
        )
        idx = next((i for i, s in enumerate(siblings) if s.cue_id == cue_id), None)
        if idx is None:
            return
        new_idx = idx + direction
        if new_idx < 0 or new_idx >= len(siblings):
            return
        siblings[idx], siblings[new_idx] = siblings[new_idx], siblings[idx]
        for i, s in enumerate(siblings):
            s.order = i

    def duplicate_cue(self, cue_id: str) -> dict | None:
        src = next((c for c in self.cues if c["id"] == cue_id), None)
        pl = self.placement_for(cue_id)
        if not src or not pl:
            return None
        new_cue = deepcopy(src)
        new_cue["id"] = self._next_cue_id()
        new_cue["name"] = f"{src['name']} (copy)"
        self.cues.append(new_cue)
        self.move_cue(new_cue["id"], pl.after_paragraph_id, pl.order + 1)
        return new_cue

    def delete_cue(self, cue_id: str) -> None:
        self.cues = [c for c in self.cues if c["id"] != cue_id]
        self.placements = [p for p in self.placements if p.cue_id != cue_id]

    def update_cue(self, cue_id: str, fields: dict) -> None:
        for cue in self.cues:
            if cue["id"] == cue_id:
                cue.update(fields)
                self._sync_cue_from_placement(cue_id)
                return

    def add_cue(self, after_paragraph_id: str, fields: dict) -> dict:
        para = self.paragraph(after_paragraph_id)
        cue = {
            "id": self._next_cue_id(),
            "asset_id": fields.get("asset_id", ""),
            "asset_filename": fields.get("asset_filename", ""),
            "playback_mode": fields.get("playback_mode", "One Shot"),
            "suggested_volume": fields.get("suggested_volume", 85),
            "page": para.page if para else 1,
            "scene": para.scene if para else "",
            "trigger": fields.get("trigger") or (para.text[:120] if para else ""),
            "name": fields.get("name", "New Cue"),
            "category": fields.get("category", "SFX"),
            "priority": fields.get("priority", "Medium"),
            "duration": fields.get("duration", "2s"),
            "loop": fields.get("loop", "No"),
            "fade": fields.get("fade", "None"),
            "volume": fields.get("volume", 85),
            "notes": fields.get("notes", ""),
            "cue_type": fields.get("cue_type", "FOREGROUND"),
            "paragraph_id": after_paragraph_id,
        }
        if fields.get("expected_background_asset_id"):
            cue["expected_background_asset_id"] = fields["expected_background_asset_id"]
        asset = self.assets_by_id.get(cue["asset_id"])
        if asset:
            cue["asset_filename"] = asset.get("filename", cue["asset_filename"])
            cue["playback_mode"] = asset.get("playback_mode", cue["playback_mode"])
            cue["suggested_volume"] = asset.get("suggested_volume", cue["suggested_volume"])
        self.cues.append(cue)
        self.move_cue(cue["id"], after_paragraph_id)
        return cue

    def _sync_cue_from_placement(self, cue_id: str) -> None:
        cue = next((c for c in self.cues if c["id"] == cue_id), None)
        pl = self.placement_for(cue_id)
        if not cue or not pl:
            return
        para = self.paragraph(pl.after_paragraph_id)
        if not para:
            return
        cue["paragraph_id"] = pl.after_paragraph_id
        cue["page"] = para.page
        cue["scene"] = para.scene
        if not cue.get("trigger"):
            cue["trigger"] = para.text[:160]

    def _next_cue_id(self) -> str:
        nums = []
        for c in self.cues:
            m = CUE_ID_RE.match(c.get("id", ""))
            if m:
                nums.append(int(m.group(1)))
        n = max(nums, default=0) + 1
        return f"CUE-{n:03d}"

    def save_all(self) -> None:
        from cue_persistence import persist_project

        for pl in self.placements:
            self._sync_cue_from_placement(pl.cue_id)
        self.cues = self.get_cues_sorted()
        persist_project(self)
        self.save_script()
