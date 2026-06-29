#!/usr/bin/env python3
"""Wet Hot American Summer — live table-read soundboard."""

from __future__ import annotations

import subprocess
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

sys.path.insert(0, str(APP_DIR))
from cue_script_index import cue_type  # noqa: E402
from playback import VLCPlaybackEngine  # noqa: E402
from script_editor import (  # noqa: E402
    BG_COLOR,
    BG_STOP_COLOR,
    FX_COLOR,
    MUSIC_COLOR,
    ScriptEditor,
    _marker_color,
    _marker_label,
)
from script_model import ScriptProject, _marker_kind  # noqa: E402


def _format_elapsed(seconds: float) -> str:
    total = max(0, int(seconds))
    minutes, secs = divmod(total, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def resolve_volume_from_cue(cue: dict) -> int:
    volume = cue.get("volume")
    if isinstance(volume, int):
        return max(0, min(100, volume))
    if isinstance(volume, str) and volume.isdigit():
        return max(0, min(100, int(volume)))
    return max(0, min(100, int(cue.get("suggested_volume", 70))))


BROWSER_GROUPS = (
    ("MUSIC", MUSIC_COLOR, "MUSIC"),
    ("FX", FX_COLOR, "SOUND EFFECTS"),
    ("BG", BG_COLOR, "BACKGROUND"),
    ("BG_STOP", BG_STOP_COLOR, "BACKGROUND STOP"),
)


class SoundboardApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("WHAS Table Read — Soundboard + Script")
        self.configure(bg="#1a1a2e")

        self.project = ScriptProject(ROOT)
        if not self.project.script_exists():
            subprocess.run(
                [sys.executable, str(ROOT / "tools" / "import_screenplay.py")],
                check=True,
                cwd=str(ROOT),
            )
        self.project.load()
        self.all_cues = self.project.get_cues_sorted()
        self.assets_by_id = self.project.assets_by_id
        self.player = self._init_player()
        self._fade_job: str | None = None
        self._tick_job: str | None = None
        self.script_editor: ScriptEditor | None = None
        self._paned_split_done = False
        self._paned_split_retries = 0
        self._active_cue_id: str | None = None
        self._browser_rows: dict[str, tk.Frame] = {}
        self._browser_filter = tk.StringVar(value="")

        self._build_ui()
        self._maximize_window()
        self.update_idletasks()
        self._bind_keys()
        self._rebuild_browser()
        self._start_background_tick()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _maximize_window(self):
        try:
            self.state("zoomed")
        except tk.TclError:
            w = self.winfo_screenwidth()
            h = self.winfo_screenheight()
            self.geometry(f"{w}x{h}")
        self._paned_split_done = False
        self._paned_split_retries = 0
        self.after_idle(self._set_paned_50_50)
        self.after(100, self._set_paned_50_50)
        self.after(300, self._set_paned_50_50)

    def _set_paned_50_50(self, _event=None):
        if self._paned_split_done:
            return
        self.update_idletasks()
        width = self.paned.winfo_width()
        if width <= 100:
            width = self.winfo_width()
        if width <= 100:
            if self._paned_split_retries < 40:
                self._paned_split_retries += 1
                self.after(50, self._set_paned_50_50)
            return

        minsize = 280
        target = max(minsize, min(width - minsize, width // 2))
        try:
            self.paned.sash_place(0, target, 0)
            self._paned_split_done = True
        except tk.TclError:
            if self._paned_split_retries < 40:
                self._paned_split_retries += 1
                self.after(50, self._set_paned_50_50)

    def _on_paned_configure(self, event):
        if event.widget is self.paned and not self._paned_split_done:
            self._set_paned_50_50()

    def _init_player(self) -> VLCPlaybackEngine | None:
        try:
            return VLCPlaybackEngine(ROOT)
        except ImportError as exc:
            print(exc, file=sys.stderr)
            return None

    def _asset_label(self, asset_id: str | None) -> str:
        if not asset_id:
            return "— (none)"
        asset = self.assets_by_id.get(asset_id)
        if asset:
            return asset["name"]
        return asset_id

    def _asset_summary(self, cue: dict) -> str:
        asset_id = cue.get("asset_id", "")
        asset = self.assets_by_id.get(asset_id, {})
        name = asset.get("name") or asset_id or "—"
        return f"{asset_id} — {name}"

    def _build_ui(self):
        small_font = tkfont.Font(family="Helvetica", size=10)

        self.paned = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashwidth=5, bg="#1a1a2e")
        self.paned.pack(fill=tk.BOTH, expand=True)

        browser_host = tk.Frame(self.paned, bg="#1a1a2e")
        self.paned.add(browser_host, minsize=280, stretch="always")

        script_host = tk.Frame(self.paned, bg="#0a0a12")
        self.paned.add(script_host, minsize=280, stretch="always")
        self.paned.bind("<Configure>", self._on_paned_configure)

        self._build_sound_browser(browser_host, small_font)

        self.script_editor = ScriptEditor(
            script_host,
            self.project,
            on_cue_selected=self._on_script_cue_clicked,
            on_cues_changed=self._on_project_updated,
        )
        self.script_editor.pack(fill=tk.BOTH, expand=True)

    def _build_sound_browser(self, parent, small_font):
        tk.Label(
            parent, text="WET HOT AMERICAN SUMMER", font=tkfont.Font(size=15, weight="bold"),
            fg="#e94560", bg="#1a1a2e", wraplength=360,
        ).pack(pady=(10, 2), padx=12)

        tk.Label(
            parent, text="SOUND BROWSER", font=tkfont.Font(size=11, weight="bold"),
            fg="#a0d2ff", bg="#1a1a2e",
        ).pack(anchor="w", padx=12, pady=(4, 0))

        filter_row = tk.Frame(parent, bg="#1a1a2e")
        filter_row.pack(fill=tk.X, padx=12, pady=(6, 4))
        tk.Label(filter_row, text="Filter:", fg="#a0a0b0", bg="#1a1a2e",
                 font=small_font).pack(side=tk.LEFT)
        ent = tk.Entry(
            filter_row, textvariable=self._browser_filter, bg="#16213e", fg="white",
            insertbackground="white", relief=tk.FLAT, width=28,
        )
        ent.pack(side=tk.LEFT, padx=6, fill=tk.X, expand=True)
        self._browser_filter.trace_add("write", lambda *_: self._rebuild_browser())

        list_body = tk.Frame(parent, bg="#1a1a2e")
        list_body.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 4))

        self.browser_canvas = tk.Canvas(list_body, bg="#12121c", highlightthickness=0)
        browser_scroll = tk.Scrollbar(list_body, orient=tk.VERTICAL, command=self.browser_canvas.yview)
        self.browser_canvas.configure(yscrollcommand=browser_scroll.set)
        browser_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.browser_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.browser_inner = tk.Frame(self.browser_canvas, bg="#12121c")
        self._browser_window = self.browser_canvas.create_window(
            (0, 0), window=self.browser_inner, anchor="nw",
        )
        self.browser_inner.bind("<Configure>", self._on_browser_configure)
        self.browser_canvas.bind("<Configure>", self._on_browser_canvas_configure)
        self.browser_canvas.bind("<MouseWheel>", self._on_browser_mousewheel)
        self.browser_canvas.bind("<Button-4>", self._on_browser_mousewheel)
        self.browser_canvas.bind("<Button-5>", self._on_browser_mousewheel)

        transport = tk.Frame(parent, bg="#0f3460", padx=12, pady=10)
        transport.pack(fill=tk.X, padx=10, pady=(0, 8))

        tk.Label(transport, text="NOW PLAYING", font=tkfont.Font(size=10, weight="bold"),
                 fg="#a0d2ff", bg="#0f3460").pack(anchor="w")
        self.lbl_now_playing = tk.Label(
            transport, text="—", font=small_font, fg="white", bg="#0f3460",
            wraplength=320, justify=tk.LEFT, anchor="w",
        )
        self.lbl_now_playing.pack(fill=tk.X, pady=(4, 6))

        btn_row = tk.Frame(transport, bg="#0f3460")
        btn_row.pack(fill=tk.X, pady=(0, 6))
        btn_style = {"font": small_font, "bg": "#16213e", "fg": "white",
                     "activebackground": "#1a1a2e", "relief": tk.FLAT, "padx": 8, "pady": 4}
        tk.Button(btn_row, text="Stop All", command=self.stop_all, **btn_style).pack(side=tk.LEFT, padx=(0, 4))
        tk.Button(btn_row, text="BG Play", command=self._bg_play, **btn_style).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_row, text="BG Pause", command=self._bg_pause, **btn_style).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_row, text="BG Stop", command=self._bg_stop, **btn_style).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_row, text="Fade Out", command=self._bg_fade_out, **btn_style).pack(side=tk.LEFT, padx=4)

        status_row = tk.Frame(transport, bg="#0f3460")
        status_row.pack(fill=tk.X)
        self.lbl_bg_status = tk.Label(status_row, text="BG: Stopped", font=small_font,
                                      fg="#f5d76e", bg="#0f3460", anchor="w")
        self.lbl_bg_status.pack(side=tk.LEFT)
        self.lbl_bg_elapsed = tk.Label(status_row, text="0:00", font=small_font,
                                       fg="white", bg="#0f3460", anchor="e")
        self.lbl_bg_elapsed.pack(side=tk.RIGHT)

        vol_row = tk.Frame(transport, bg="#0f3460")
        vol_row.pack(fill=tk.X, pady=(6, 0))
        tk.Label(vol_row, text="BG Vol:", font=small_font, fg="#c0c0d0", bg="#0f3460").pack(side=tk.LEFT)
        self.bg_volume = tk.IntVar(value=30)
        self.bg_volume_scale = tk.Scale(
            vol_row, from_=0, to=100, orient=tk.HORIZONTAL, length=220,
            variable=self.bg_volume, command=self._on_bg_volume, bg="#0f3460", fg="white",
            highlightthickness=0, troughcolor="#16213e", activebackground="#e94560",
        )
        self.bg_volume_scale.pack(side=tk.LEFT, padx=(6, 0))

        self.status = tk.Label(parent, text="Click a cue in the script or sound browser to play.",
                               font=small_font, fg="#a0a0b0", bg="#1a1a2e", wraplength=360)
        self.status.pack(pady=(0, 8), padx=12)

    def _on_browser_configure(self, event=None):
        if event is not None:
            self.browser_canvas.configure(scrollregion=(0, 0, event.width, max(event.height, 1)))

    def _on_browser_canvas_configure(self, event):
        self.browser_canvas.itemconfig(self._browser_window, width=event.width)

    def _on_browser_mousewheel(self, event):
        if event.num == 5:
            self.browser_canvas.yview_scroll(3, "units")
        elif event.num == 4:
            self.browser_canvas.yview_scroll(-3, "units")
        else:
            delta = event.delta
            if delta:
                steps = max(1, abs(delta) // 120)
                self.browser_canvas.yview_scroll(-steps if delta > 0 else steps, "units")
        return "break"

    def _cue_matches_filter(self, cue: dict, query: str) -> bool:
        if not query:
            return True
        asset = self.assets_by_id.get(cue.get("asset_id", ""), {})
        hay = " ".join([
            cue.get("id", ""), cue.get("name", ""), cue.get("category", ""),
            cue.get("trigger", ""), str(cue.get("page", "")), asset.get("name", ""),
        ]).lower()
        return query in hay

    def _rebuild_browser(self):
        for child in self.browser_inner.winfo_children():
            child.destroy()
        self._browser_rows.clear()

        query = self._browser_filter.get().strip().lower()
        small_font = tkfont.Font(family="Helvetica", size=9)

        for kind, _color, title in BROWSER_GROUPS:
            cues = [
                c for c in self.all_cues
                if _marker_kind(c) == kind and self._cue_matches_filter(c, query)
            ]
            if not cues:
                continue

            tk.Label(
                self.browser_inner, text=title, font=tkfont.Font(size=10, weight="bold"),
                fg="#a0d2ff", bg="#12121c", anchor="w",
            ).pack(fill=tk.X, padx=8, pady=(10, 4))

            for cue in cues:
                self._add_browser_row(cue, small_font)

        self.browser_inner.update_idletasks()
        self.browser_canvas.configure(scrollregion=self.browser_canvas.bbox("all"))
        self._highlight_browser_cue(self._active_cue_id)

    def _add_browser_row(self, cue: dict, small_font):
        color = _marker_color(cue)
        row = tk.Frame(self.browser_inner, bg=color, cursor="hand2")
        row.pack(fill=tk.X, padx=8, pady=2)
        row._cue_id = cue["id"]  # type: ignore[attr-defined]
        row._base_color = color  # type: ignore[attr-defined]
        self._browser_rows[cue["id"]] = row

        asset_name = self._asset_label(cue.get("asset_id"))
        tk.Label(
            row, text=_marker_label(cue), font=tkfont.Font(size=9, weight="bold"),
            fg="white", bg=color, anchor="w",
        ).pack(fill=tk.X, padx=8, pady=(4, 0))
        tk.Label(
            row, text=f"p.{cue.get('page', '?')}  •  {asset_name}",
            font=small_font, fg="#f0f0f0", bg=color, anchor="w",
        ).pack(fill=tk.X, padx=8, pady=(0, 4))

        for widget in row.winfo_children():
            widget.bind("<Button-1>", lambda e, c=cue: self._play_cue(c))
        row.bind("<Button-1>", lambda e, c=cue: self._play_cue(c))

    def _highlight_browser_cue(self, cue_id: str | None):
        self._active_cue_id = cue_id
        for cid, row in self._browser_rows.items():
            base = row._base_color  # type: ignore[attr-defined]
            active = cid == cue_id
            row.configure(bg="#ffffff" if active else base)
            for i, child in enumerate(row.winfo_children()):
                child.configure(
                    bg="#ffffff" if active else base,
                    fg="#1a1a2e" if active else ("white" if i == 0 else "#f0f0f0"),
                )

    def _bind_keys(self):
        self.bind("<Escape>", self._on_escape)

    def _on_escape(self, _event=None):
        self.stop_all()
        return "break"

    def _on_project_updated(self):
        self.project.load()
        self.all_cues = self.project.get_cues_sorted()
        self.assets_by_id = self.project.assets_by_id
        self._rebuild_browser()

    def _on_script_cue_clicked(self, cue: dict):
        self._play_cue(cue, from_script=True)

    def _play_cue(self, cue: dict, *, from_script: bool = False):
        self._highlight_browser_cue(cue["id"])
        if cue_type(cue) == "BACKGROUND":
            self._execute_background_go(cue)
        else:
            self._execute_foreground_go(cue)

        if self.script_editor:
            self.script_editor.scroll_to_cue(cue, fg_id=cue["id"])
        elif not from_script:
            pass

        self.lbl_now_playing.config(text=f"{cue['id']} — {cue['name']}\n{self._asset_summary(cue)}")
        self.status.config(text=f"▶ {cue['id']} — {cue['name']}")

    def _refresh_background_playback(self):
        if not self.player:
            return
        asset_id = self.player.current_background_asset_id()
        if asset_id is None:
            self.lbl_bg_status.config(text="BG: Stopped", fg="#a0a0b0")
        elif self.player.background_is_playing():
            self.lbl_bg_status.config(text=f"BG: {self._asset_label(asset_id)}", fg="#7ec8a3")
        elif self.player.background_is_active():
            self.lbl_bg_status.config(text=f"BG: Paused — {self._asset_label(asset_id)}", fg="#f5d76e")
        else:
            self.lbl_bg_status.config(text="BG: Stopped", fg="#a0a0b0")

        self.lbl_bg_elapsed.config(text=_format_elapsed(self.player.background_elapsed_seconds()))
        self.bg_volume.set(self.player.background_volume())

    def _start_background_tick(self):
        self._refresh_background_playback()
        self._tick_job = self.after(500, self._start_background_tick)

    def _cancel_fade(self):
        if self._fade_job:
            self.after_cancel(self._fade_job)
            self._fade_job = None

    def _fade_background_volume(self, start: int, end: int, duration_ms: int, on_complete=None):
        self._cancel_fade()
        if not self.player or duration_ms <= 0:
            if self.player:
                self.player.set_background_volume(end)
            if on_complete:
                on_complete()
            return

        steps = max(1, duration_ms // 50)
        delta = (end - start) / steps

        def step(remaining: int, volume: float):
            if not self.player:
                return
            vol = int(round(volume))
            self.player.set_background_volume(vol)
            self.bg_volume.set(vol)
            if remaining <= 1:
                self._fade_job = None
                if on_complete:
                    on_complete()
                return
            self._fade_job = self.after(50, lambda: step(remaining - 1, volume + delta))

        step(steps, float(start))

    def _bg_play(self):
        if self.player:
            self.player.resume_background()

    def _bg_pause(self):
        if self.player:
            self.player.pause_background()

    def _bg_stop(self):
        if not self.player:
            return
        self._cancel_fade()
        self.player.stop_background()
        self._refresh_background_playback()

    def _bg_fade_out(self):
        if not self.player or not self.player.background_is_active():
            return
        start = self.player.background_volume()

        def finish():
            if self.player:
                self.player.stop_background()
            self._refresh_background_playback()

        self._fade_background_volume(start, 0, 1500, on_complete=finish)

    def _execute_background_go(self, cue: dict):
        if not self.player:
            self.status.config(text="Playback unavailable — install python-vlc and VLC")
            return

        def run_background():
            ok, message = self.player.play_background(cue, fade_in_ms=800)
            if ok and cue.get("category") != "Silence":
                self._fade_background_volume(0, resolve_volume_from_cue(cue), 800)
            prefix = "▶" if ok else "⚠"
            self.status.config(text=f"{prefix} BG {cue['id']} — {message}")
            self._refresh_background_playback()

        if self.player.background_is_active() and cue.get("category") != "Silence":
            start_vol = self.player.background_volume()

            def after_fade():
                self.player.stop_background()
                run_background()

            self._fade_background_volume(start_vol, 0, 1000, on_complete=after_fade)
        else:
            run_background()

    def _execute_foreground_go(self, cue: dict):
        if not self.player:
            self.status.config(text="Playback unavailable — install python-vlc and VLC")
            return
        ok, message = self.player.play_foreground(cue)
        self.status.config(text=f"{'▶' if ok else '⚠'} {cue['id']} — {message}")
        self._refresh_background_playback()

    def stop_all(self):
        self._cancel_fade()
        if self.player:
            self.player.stop_all()
        self.status.config(text="■ Stopped all playback")
        self._refresh_background_playback()

    def _on_bg_volume(self, _value):
        if self.player:
            self.player.set_background_volume(self.bg_volume.get())

    def _on_close(self):
        self._cancel_fade()
        if self._tick_job:
            self.after_cancel(self._tick_job)
        if self.player:
            self.player.stop_all()
        if self.script_editor:
            self.script_editor.close()
        self.destroy()


def main():
    app = SoundboardApp()
    app.mainloop()


if __name__ == "__main__":
    main()
