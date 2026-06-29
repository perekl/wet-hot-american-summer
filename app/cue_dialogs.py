"""Dialogs for creating and editing cues."""

from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont, messagebox, ttk


CUE_TYPES = ["FOREGROUND", "BACKGROUND"]
CATEGORIES = ["SFX", "Ambience", "Music", "Transition", "Silence", "Comedy"]
PRIORITIES = ["Critical", "High", "Medium", "Low", "Optional"]


class CueFormDialog(tk.Toplevel):
    def __init__(self, parent, title: str, assets_by_id: dict, initial: dict | None = None):
        super().__init__(parent)
        self.title(title)
        self.configure(bg="#1a1a2e")
        self.result: dict | None = None
        self.assets_by_id = assets_by_id
        initial = initial or {}

        body = tk.Frame(self, bg="#1a1a2e", padx=16, pady=12)
        body.pack(fill=tk.BOTH, expand=True)

        self.vars = {
            "name": tk.StringVar(value=initial.get("name", "")),
            "cue_type": tk.StringVar(value=initial.get("cue_type", "FOREGROUND")),
            "category": tk.StringVar(value=initial.get("category", "SFX")),
            "asset_id": tk.StringVar(value=initial.get("asset_id", "")),
            "expected_background_asset_id": tk.StringVar(
                value=initial.get("expected_background_asset_id", "")
            ),
            "priority": tk.StringVar(value=initial.get("priority", "Medium")),
            "notes": tk.StringVar(value=initial.get("notes", "")),
            "trigger": tk.StringVar(value=initial.get("trigger", "")),
            "volume": tk.StringVar(value=str(initial.get("volume", 85))),
        }

        row = 0
        for label, key, widget in self._fields():
            tk.Label(body, text=label, fg="#a0a0b0", bg="#1a1a2e").grid(
                row=row, column=0, sticky="w", pady=4
            )
            widget.grid(row=row, column=1, sticky="ew", pady=4, padx=(8, 0))
            row += 1

        body.columnconfigure(1, weight=1)

        btn_row = tk.Frame(self, bg="#1a1a2e", pady=8)
        btn_row.pack(fill=tk.X)
        tk.Button(btn_row, text="Cancel", command=self.destroy, bg="#16213e", fg="white",
                  relief=tk.FLAT, padx=12).pack(side=tk.RIGHT, padx=8)
        tk.Button(btn_row, text="Save", command=self._save, bg="#e94560", fg="white",
                  relief=tk.FLAT, padx=12).pack(side=tk.RIGHT, padx=8)

        self.transient(parent)
        self.grab_set()
        self.geometry("480x380")

    def _fields(self):
        asset_ids = sorted(self.assets_by_id.keys())
        asset_combo = ttk.Combobox(self, textvariable=self.vars["asset_id"], values=asset_ids, width=36)
        exp_combo = ttk.Combobox(
            self, textvariable=self.vars["expected_background_asset_id"], values=[""] + asset_ids, width=36
        )
        yield "Cue Name", "name", tk.Entry(self, textvariable=self.vars["name"], width=40)
        yield "Cue Type", "cue_type", ttk.Combobox(self, textvariable=self.vars["cue_type"], values=CUE_TYPES)
        yield "Category", "category", ttk.Combobox(self, textvariable=self.vars["category"], values=CATEGORIES)
        yield "Asset ID", "asset_id", asset_combo
        yield "Expected Background", "expected_background_asset_id", exp_combo
        yield "Priority", "priority", ttk.Combobox(self, textvariable=self.vars["priority"], values=PRIORITIES)
        yield "Trigger", "trigger", tk.Entry(self, textvariable=self.vars["trigger"], width=40)
        yield "Volume", "volume", tk.Entry(self, textvariable=self.vars["volume"], width=10)
        yield "Notes", "notes", tk.Entry(self, textvariable=self.vars["notes"], width=40)

    def _save(self):
        if not self.vars["name"].get().strip():
            messagebox.showerror("Cue", "Cue name is required", parent=self)
            return
        asset_id = self.vars["asset_id"].get().strip()
        asset = self.assets_by_id.get(asset_id, {})
        try:
            volume = int(self.vars["volume"].get())
        except ValueError:
            volume = 85
        self.result = {
            "name": self.vars["name"].get().strip(),
            "cue_type": self.vars["cue_type"].get(),
            "category": self.vars["category"].get(),
            "asset_id": asset_id,
            "expected_background_asset_id": self.vars["expected_background_asset_id"].get().strip() or None,
            "priority": self.vars["priority"].get(),
            "notes": self.vars["notes"].get().strip(),
            "trigger": self.vars["trigger"].get().strip(),
            "volume": volume,
            "playback_mode": asset.get("playback_mode", "One Shot"),
            "suggested_volume": asset.get("suggested_volume", 85),
            "asset_filename": asset.get("filename", ""),
        }
        if not self.result["expected_background_asset_id"]:
            self.result.pop("expected_background_asset_id", None)
        self.destroy()


def ask_new_cue(parent, assets_by_id: dict, default_trigger: str = "") -> dict | None:
    dlg = CueFormDialog(parent, "New Cue", assets_by_id, {"trigger": default_trigger})
    parent.wait_window(dlg)
    return dlg.result


def ask_edit_cue(parent, assets_by_id: dict, cue: dict) -> dict | None:
    dlg = CueFormDialog(parent, f"Edit {cue.get('id', 'Cue')}", assets_by_id, cue)
    parent.wait_window(dlg)
    return dlg.result
