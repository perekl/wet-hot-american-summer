#!/usr/bin/env python3
"""Wet Hot American Summer — live table-read soundboard."""

from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import font as tkfont
except ImportError:
    print("tkinter is required", file=sys.stderr)
    sys.exit(1)

APP_DIR = Path(__file__).resolve().parent
ROOT = APP_DIR.parent
CUES_PATH = ROOT / "data" / "cues.json"

sys.path.insert(0, str(APP_DIR))
from playback import VLCPlaybackEngine  # noqa: E402


class SoundboardApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("WHAS Table Read — Soundboard")
        self.geometry("900x620")
        self.configure(bg="#1a1a2e")

        self.cues = self._load_cues()
        self.index = 0
        self.player = self._init_player()

        self._build_ui()
        self._bind_keys()
        self._refresh()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _init_player(self) -> VLCPlaybackEngine | None:
        try:
            return VLCPlaybackEngine(ROOT)
        except ImportError as exc:
            print(exc, file=sys.stderr)
            return None

    def _load_cues(self) -> list[dict]:
        if not CUES_PATH.exists():
            raise FileNotFoundError(
                f"Missing {CUES_PATH}. Run: python tools/generate_production_kit.py"
            )
        return json.loads(CUES_PATH.read_text(encoding="utf-8"))

    def _build_ui(self):
        title_font = tkfont.Font(family="Helvetica", size=22, weight="bold")
        big_font = tkfont.Font(family="Helvetica", size=18, weight="bold")
        med_font = tkfont.Font(family="Helvetica", size=13)
        small_font = tkfont.Font(family="Helvetica", size=11)

        header = tk.Label(self, text="WET HOT AMERICAN SUMMER", font=title_font,
                          fg="#e94560", bg="#1a1a2e")
        header.pack(pady=(16, 4))
        sub = tk.Label(self, text="Sound Cue Navigator (playback not yet implemented)",
                       font=small_font, fg="#a0a0b0", bg="#1a1a2e")
        sub.pack(pady=(0, 12))

        nav = tk.Frame(self, bg="#1a1a2e")
        nav.pack(pady=8)

        self.btn_prev = tk.Button(nav, text="◀  PREVIOUS", font=med_font, width=14,
                                  command=self.prev_cue, bg="#16213e", fg="white",
                                  activebackground="#0f3460", relief=tk.FLAT, padx=8, pady=10)
        self.btn_prev.grid(row=0, column=0, padx=12)

        self.btn_play = tk.Button(nav, text="▶  PLAY", font=tkfont.Font(size=28, weight="bold"),
                                  width=8, command=self.play_cue, bg="#e94560", fg="white",
                                  activebackground="#c73652", relief=tk.FLAT, padx=16, pady=14)
        self.btn_play.grid(row=0, column=1, padx=12)

        self.btn_next = tk.Button(nav, text="NEXT  ▶", font=med_font, width=14,
                                  command=self.next_cue, bg="#16213e", fg="white",
                                  activebackground="#0f3460", relief=tk.FLAT, padx=8, pady=10)
        self.btn_next.grid(row=0, column=2, padx=12)

        tk.Label(self, text="SPACEBAR = NEXT CUE", font=small_font,
                 fg="#a0a0b0", bg="#1a1a2e").pack()

        panel = tk.Frame(self, bg="#16213e", padx=24, pady=20)
        panel.pack(fill=tk.BOTH, expand=True, padx=24, pady=16)

        self.lbl_cue_id = tk.Label(panel, text="", font=big_font, fg="#e94560", bg="#16213e", anchor="w")
        self.lbl_cue_id.pack(fill=tk.X)

        self.lbl_name = tk.Label(panel, text="", font=tkfont.Font(size=20, weight="bold"),
                                 fg="white", bg="#16213e", anchor="w", wraplength=820, justify=tk.LEFT)
        self.lbl_name.pack(fill=tk.X, pady=(8, 4))

        self.lbl_meta = tk.Label(panel, text="", font=med_font, fg="#a0d2ff", bg="#16213e", anchor="w")
        self.lbl_meta.pack(fill=tk.X, pady=4)

        tk.Label(panel, text="TRIGGER DIALOGUE", font=small_font, fg="#a0a0b0",
                 bg="#16213e", anchor="w").pack(fill=tk.X, pady=(16, 2))
        self.lbl_trigger = tk.Label(panel, text="", font=med_font, fg="#f5f5f5", bg="#16213e",
                                    anchor="w", wraplength=820, justify=tk.LEFT)
        self.lbl_trigger.pack(fill=tk.X)

        tk.Label(panel, text="UPCOMING CUE", font=small_font, fg="#a0a0b0",
                 bg="#16213e", anchor="w").pack(fill=tk.X, pady=(16, 2))
        self.lbl_upcoming = tk.Label(panel, text="", font=med_font, fg="#7ec8a3", bg="#16213e",
                                     anchor="w", wraplength=820, justify=tk.LEFT)
        self.lbl_upcoming.pack(fill=tk.X)

        self.status = tk.Label(self, text="", font=small_font, fg="#a0a0b0", bg="#1a1a2e")
        self.status.pack(pady=(0, 12))

    def _bind_keys(self):
        self.bind("<space>", self._on_space)
        self.bind("<Left>", lambda e: self.prev_cue())
        self.bind("<Right>", lambda e: self.next_cue())
        self.bind("<Return>", lambda e: self.play_cue())
        self.bind("<Escape>", self._on_escape)

    def _on_space(self, _event=None):
        self.next_cue()
        return "break"

    def _on_escape(self, _event=None):
        self.stop_all()
        return "break"

    def _refresh(self):
        c = self.cues[self.index]
        nxt = self.cues[self.index + 1] if self.index + 1 < len(self.cues) else None

        self.lbl_cue_id.config(text=f"{c['id']}  •  Page {c['page']}  •  {c['category']}")
        self.lbl_name.config(text=c["name"])
        self.lbl_meta.config(
            text=f"Asset: {c['asset_id']}  |  {c.get('playback_mode', '')}  |  "
                 f"Scene: {c['scene']}  |  Priority: {c['priority']}  |  "
                 f"Fade: {c['fade']}  |  Cue Vol: {c['volume']}  |  "
                 f"Asset Vol: {c.get('suggested_volume', '')}  |  Loop: {c['loop']}"
        )
        self.lbl_trigger.config(text=c["trigger"])
        if nxt:
            self.lbl_upcoming.config(text=f"{nxt['id']} (p.{nxt['page']}) — {nxt['name']}")
        else:
            self.lbl_upcoming.config(text="(end of show)")
        self.status.config(text=f"Cue {self.index + 1} of {len(self.cues)}")

    def play_cue(self):
        c = self.cues[self.index]
        if not self.player:
            self.status.config(text="Playback unavailable — install python-vlc and VLC")
            return
        ok, message = self.player.play_cue(c)
        prefix = "▶" if ok else "⚠"
        self.status.config(
            text=f"{prefix} {c['id']} — {message}  [{c.get('asset_id')}]"
        )

    def stop_all(self):
        if self.player:
            self.player.stop_all()
        c = self.cues[self.index]
        self.status.config(text=f"■ Stopped all playback (ESC) — cue {c['id']}")

    def next_cue(self):
        if self.index < len(self.cues) - 1:
            self.index += 1
            self._refresh()

    def prev_cue(self):
        if self.index > 0:
            self.index -= 1
            self._refresh()

    def _on_close(self):
        if self.player:
            self.player.stop_all()
        self.destroy()


def main():
    app = SoundboardApp()
    app.mainloop()


if __name__ == "__main__":
    main()
