"""Dialogs for creating and editing cues."""

from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont, messagebox, ttk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from script_model import ScriptProject

CUE_TYPES = ["FOREGROUND", "BACKGROUND"]
CATEGORIES = ["SFX", "Ambience", "Music", "Transition", "Silence", "Comedy"]
PRIORITIES = ["Critical", "High", "Medium", "Low", "Optional"]
DURATIONS = ["1s", "2s", "3s", "5s", "10s", "30s", "Loop", "Full song excerpt", "Scene length"]
LOOPS = ["Yes", "No"]
FADES = ["None", "In", "Out", "In/Out"]

FIELD_BG = "#16213e"
DIALOG_BG = "#1a1a2e"
LABEL_FG = "#a0a0b0"
ENTRY_FG = "white"


def _bind_mousewheel(widget, callback):
    widget.bind("<MouseWheel>", callback, add="+")
    widget.bind("<Button-4>", callback, add="+")
    widget.bind("<Button-5>", callback, add="+")


def _scroll_canvas(canvas: tk.Canvas, event):
    if event.num == 5:
        canvas.yview_scroll(3, "units")
    elif event.num == 4:
        canvas.yview_scroll(-3, "units")
    else:
        delta = event.delta
        if delta:
            steps = max(1, abs(delta) // 120)
            canvas.yview_scroll(-steps if delta > 0 else steps, "units")
    return "break"


def asset_display_label(asset_id: str, asset: dict) -> str:
    name = (asset.get("name") or "").strip()
    if name:
        return f"{asset_id} — {name}"
    return asset_id


def build_asset_lookups(assets_by_id: dict[str, dict]) -> tuple[dict[str, str], dict[str, str], list[str]]:
    display_by_id = {
        aid: asset_display_label(aid, asset)
        for aid, asset in sorted(assets_by_id.items())
    }
    id_by_display = {label: aid for aid, label in display_by_id.items()}
    return display_by_id, id_by_display, list(display_by_id.values())


class CueFormDialog(tk.Toplevel):
    def __init__(
        self,
        parent,
        title: str,
        project: ScriptProject,
        initial: dict | None = None,
        *,
        is_new: bool = False,
    ):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=DIALOG_BG)
        self.result: dict | None = None
        self.project = project
        self.assets_by_id = project.assets_by_id
        self._asset_display_by_id, self._asset_id_by_display, self._asset_display_values = (
            build_asset_lookups(self.assets_by_id)
        )
        self.is_new = is_new
        initial = dict(initial or {})

        if is_new and not initial.get("id"):
            initial["id"] = project._next_cue_id()

        initial_asset = initial.get("asset_id", "")

        container = tk.Frame(self, bg=DIALOG_BG)
        container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(container, bg=DIALOG_BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient=tk.VERTICAL, command=canvas.yview)
        body = tk.Frame(canvas, bg=DIALOG_BG, padx=16, pady=12)
        body.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=body, anchor="nw", width=520)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        wheel = lambda e: _scroll_canvas(canvas, e)
        _bind_mousewheel(self, wheel)
        _bind_mousewheel(container, wheel)
        _bind_mousewheel(canvas, wheel)
        _bind_mousewheel(body, wheel)

        if hasattr(parent, "suspend_mousewheel"):
            parent.suspend_mousewheel()

        self.vars = {
            "id": tk.StringVar(value=initial.get("id", "")),
            "name": tk.StringVar(value=initial.get("name", "")),
            "cue_type": tk.StringVar(value=initial.get("cue_type", "FOREGROUND")),
            "category": tk.StringVar(value=initial.get("category", "SFX")),
            "asset_id": tk.StringVar(value=self._display_for_asset(initial_asset)),
            "page": tk.StringVar(value=str(initial.get("page", 1))),
            "scene": tk.StringVar(value=initial.get("scene", "")),
            "trigger": tk.StringVar(value=initial.get("trigger", "")),
            "priority": tk.StringVar(value=initial.get("priority", "Medium")),
            "duration": tk.StringVar(value=initial.get("duration", "2s")),
            "loop": tk.StringVar(value=initial.get("loop", "No")),
            "fade": tk.StringVar(value=initial.get("fade", "None")),
            "volume": tk.StringVar(value=str(initial.get("volume", 85))),
            "notes": tk.StringVar(value=initial.get("notes", "")),
            "paragraph_id": tk.StringVar(value=initial.get("paragraph_id", "")),
        }
        self.vars["asset_id"].trace_add("write", self._on_asset_change)

        row = 0
        for label, key, widget in self._fields(body):
            tk.Label(body, text=label, fg=LABEL_FG, bg=DIALOG_BG, anchor="w").grid(
                row=row, column=0, sticky="nw", pady=4
            )
            widget.grid(row=row, column=1, sticky="ew", pady=4, padx=(8, 0))
            row += 1

        body.columnconfigure(1, weight=1)

        btn_row = tk.Frame(self, bg=DIALOG_BG, pady=8, padx=16)
        btn_row.pack(fill=tk.X)
        tk.Button(
            btn_row, text="Cancel", command=self.destroy, bg=FIELD_BG, fg="white",
            relief=tk.FLAT, padx=12,
        ).pack(side=tk.RIGHT, padx=8)
        tk.Button(
            btn_row, text="Save", command=self._save, bg="#e94560", fg="white",
            relief=tk.FLAT, padx=12,
        ).pack(side=tk.RIGHT, padx=8)

        self.transient(parent)
        self.grab_set()
        self.geometry("560x560")
        self.minsize(520, 400)
        self._on_asset_change()

    def _entry(self, parent, key: str, *, width: int = 40, readonly: bool = False) -> tk.Entry:
        state = "readonly" if readonly else "normal"
        ent = tk.Entry(
            parent, textvariable=self.vars[key], width=width,
            bg=FIELD_BG, fg=ENTRY_FG, insertbackground=ENTRY_FG, relief=tk.FLAT,
            readonlybackground="#0f3460" if readonly else FIELD_BG,
            state=state,
        )
        return ent

    def _combo(self, parent, key: str, values: list[str], *, width: int = 36, readonly: bool = False) -> ttk.Combobox:
        combo = ttk.Combobox(parent, textvariable=self.vars[key], values=values, width=width)
        if readonly:
            combo.configure(state="readonly")
        return combo

    def _display_for_asset(self, asset_id: str) -> str:
        if not asset_id:
            return ""
        return self._asset_display_by_id.get(asset_id, asset_id)

    def _resolve_asset_id(self, value: str) -> str:
        value = value.strip()
        if not value:
            return ""
        if value in self._asset_id_by_display:
            return self._asset_id_by_display[value]
        if value in self.assets_by_id:
            return value
        if " — " in value:
            candidate = value.split(" — ", 1)[0].strip()
            if candidate in self.assets_by_id:
                return candidate
        return value

    def _fields(self, parent):
        yield "Cue ID", "id", self._entry(parent, "id", width=20, readonly=True)
        yield "Cue Name", "name", self._entry(parent, "name")
        yield "Cue Type", "cue_type", self._combo(parent, "cue_type", CUE_TYPES, width=18)
        yield "Category", "category", self._combo(parent, "category", CATEGORIES, width=18)
        yield "Asset", "asset_id", self._combo(
            parent, "asset_id", self._asset_display_values, width=48, readonly=True,
        )
        yield "Script Page", "page", self._entry(parent, "page", width=10)
        yield "Scene", "scene", self._entry(parent, "scene")
        yield "Trigger", "trigger", self._entry(parent, "trigger")
        yield "Priority", "priority", self._combo(parent, "priority", PRIORITIES, width=18)
        yield "Duration", "duration", self._combo(parent, "duration", DURATIONS, width=18)
        yield "Loop", "loop", self._combo(parent, "loop", LOOPS, width=10)
        yield "Fade", "fade", self._combo(parent, "fade", FADES, width=12)
        yield "Volume", "volume", self._entry(parent, "volume", width=10)
        yield "Paragraph ID", "paragraph_id", self._entry(parent, "paragraph_id", width=30, readonly=True)
        yield "Notes", "notes", self._entry(parent, "notes")

    def _on_asset_change(self, *_args):
        asset = self.assets_by_id.get(self._resolve_asset_id(self.vars["asset_id"].get()), {})
        if not asset:
            return
        if self.is_new or not self.vars["name"].get().strip():
            name = asset.get("name", "")
            if name and not self.vars["name"].get().strip():
                self.vars["name"].set(name)
        if asset.get("playback_mode") == "Loop":
            self.vars["loop"].set("Yes")
            self.vars["duration"].set("Loop")
        if asset.get("category") == "Ambience":
            self.vars["cue_type"].set("BACKGROUND")
            self.vars["category"].set("Ambience")

    def _save(self):
        if not self.vars["name"].get().strip():
            messagebox.showerror("Cue", "Cue name is required", parent=self)
            return
        asset_id = self._resolve_asset_id(self.vars["asset_id"].get())
        asset = self.assets_by_id.get(asset_id, {})
        try:
            volume = int(self.vars["volume"].get())
        except ValueError:
            volume = 85
        try:
            page = int(self.vars["page"].get())
        except ValueError:
            page = 1

        self.result = {
            "id": self.vars["id"].get().strip(),
            "name": self.vars["name"].get().strip(),
            "cue_type": self.vars["cue_type"].get(),
            "category": self.vars["category"].get(),
            "asset_id": asset_id,
            "page": page,
            "scene": self.vars["scene"].get().strip(),
            "priority": self.vars["priority"].get(),
            "duration": self.vars["duration"].get(),
            "loop": self.vars["loop"].get(),
            "fade": self.vars["fade"].get(),
            "notes": self.vars["notes"].get().strip(),
            "trigger": self.vars["trigger"].get().strip(),
            "volume": volume,
            "paragraph_id": self.vars["paragraph_id"].get().strip(),
            "playback_mode": asset.get("playback_mode", "One Shot"),
            "suggested_volume": asset.get("suggested_volume", 85),
            "asset_filename": asset.get("filename", ""),
        }
        self.destroy()


def ask_new_cue(
    parent,
    project: ScriptProject,
    *,
    default_trigger: str = "",
    anchor_text: str = "",
    paragraph_id: str = "",
    cue_type: str = "FOREGROUND",
    category: str = "SFX",
) -> dict | None:
    para = project.paragraph(paragraph_id) if paragraph_id else None
    trigger = anchor_text or default_trigger
    initial = {
        "id": project._next_cue_id(),
        "trigger": trigger,
        "page": para.page if para else 1,
        "scene": para.scene if para else "",
        "paragraph_id": paragraph_id,
        "cue_type": cue_type,
        "category": category,
    }
    dlg = CueFormDialog(parent, "New Cue", project, initial, is_new=True)
    parent.wait_window(dlg)
    return dlg.result


def ask_edit_cue(parent, project: ScriptProject, cue: dict) -> dict | None:
    dlg = CueFormDialog(parent, f"Edit {cue.get('id', 'Cue')}", project, cue, is_new=False)
    parent.wait_window(dlg)
    return dlg.result
