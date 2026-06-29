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
ASSETS_PATH = ROOT / "data" / "assets.json"

sys.path.insert(0, str(APP_DIR))
from cue_script_index import cue_type, queue_index_for_page  # noqa: E402
from playback import VLCPlaybackEngine  # noqa: E402
from script_panel import ScriptPanel  # noqa: E402


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


class SoundboardApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("WHAS Table Read — Soundboard + Script")
        self.configure(bg="#1a1a2e")

        self.all_cues = self._load_cues()
        self.foreground_cues = [c for c in self.all_cues if cue_type(c) == "FOREGROUND"]
        self.background_cues = [c for c in self.all_cues if cue_type(c) == "BACKGROUND"]
        self.assets_by_id = self._load_assets()
        self.fg_index = 0
        self.bg_index = 0
        self.player = self._init_player()
        self._fade_job: str | None = None
        self._tick_job: str | None = None
        self._ignore_mismatch_for: str | None = None
        self._script_sync_lock = False
        self.script_panel: ScriptPanel | None = None

        self._build_ui()
        self._bind_keys()
        self._refresh_foreground()
        self._refresh_background()
        self._start_background_tick()
        self._sync_script_from_foreground()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._maximize_window()

    def _maximize_window(self):
        try:
            self.state("zoomed")
        except tk.TclError:
            w = self.winfo_screenwidth()
            h = self.winfo_screenheight()
            self.geometry(f"{w}x{h}")

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

    def _load_assets(self) -> dict[str, dict]:
        if not ASSETS_PATH.exists():
            return {}
        assets = json.loads(ASSETS_PATH.read_text(encoding="utf-8"))
        return {a["id"]: a for a in assets}

    def _asset_label(self, asset_id: str | None) -> str:
        if not asset_id:
            return "— (none)"
        asset = self.assets_by_id.get(asset_id)
        if asset:
            return asset["name"]
        return asset_id

    def _foreground_cue(self) -> dict:
        return self.foreground_cues[self.fg_index]

    def _background_cue(self) -> dict:
        return self.background_cues[self.bg_index]

    def _bg_index_for_asset(self, asset_id: str) -> int | None:
        for i, cue in enumerate(self.background_cues):
            if cue.get("asset_id") == asset_id:
                return i
        return None

    def _build_ui(self):
        med_font = tkfont.Font(family="Helvetica", size=12)
        small_font = tkfont.Font(family="Helvetica", size=10)

        self.paned = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashwidth=5, bg="#1a1a2e")
        self.paned.pack(fill=tk.BOTH, expand=True)

        controls = tk.Frame(self.paned, bg="#1a1a2e", width=400)
        self.paned.add(controls, minsize=360)

        script_host = tk.Frame(self.paned, bg="#0a0a12")
        self.paned.add(script_host, minsize=500)

        tk.Label(
            controls, text="WET HOT AMERICAN SUMMER", font=tkfont.Font(size=16, weight="bold"),
            fg="#e94560", bg="#1a1a2e", wraplength=360,
        ).pack(pady=(10, 2), padx=12)

        self._build_background_panel(controls, med_font, small_font)

        tk.Label(controls, text="EFFECTS", font=tkfont.Font(size=11, weight="bold"),
                 fg="#a0d2ff", bg="#1a1a2e").pack(anchor="w", padx=12, pady=(8, 0))

        nav = tk.Frame(controls, bg="#1a1a2e")
        nav.pack(pady=4, padx=8)

        self.btn_prev = tk.Button(nav, text="◀ PREV", font=med_font, width=8,
                                  command=self.prev_foreground, bg="#16213e", fg="white",
                                  activebackground="#0f3460", relief=tk.FLAT, padx=6, pady=8)
        self.btn_prev.grid(row=0, column=0, padx=4)

        self.btn_play = tk.Button(nav, text="▶ GO", font=tkfont.Font(size=22, weight="bold"),
                                  width=6, command=self.play_foreground_cue, bg="#e94560", fg="white",
                                  activebackground="#c73652", relief=tk.FLAT, padx=10, pady=10)
        self.btn_play.grid(row=0, column=1, padx=4)

        self.btn_next = tk.Button(nav, text="NEXT ▶", font=med_font, width=8,
                                  command=self.next_foreground, bg="#16213e", fg="white",
                                  activebackground="#0f3460", relief=tk.FLAT, padx=6, pady=8)
        self.btn_next.grid(row=0, column=2, padx=4)

        tk.Label(controls, text="Space = next effect  |  Enter = GO  |  Esc = stop all",
                 font=small_font, fg="#a0a0b0", bg="#1a1a2e", wraplength=360).pack(padx=12)

        panel = tk.Frame(controls, bg="#16213e", padx=14, pady=12)
        panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=(6, 8))

        self.sync_banner = tk.Frame(panel, bg="#16213e")
        self.sync_banner.pack(fill=tk.X, pady=(0, 8))
        self.lbl_sync = tk.Label(self.sync_banner, text="", font=med_font,
                                 bg="#16213e", anchor="w", wraplength=330, justify=tk.LEFT)
        self.lbl_sync.pack(fill=tk.X)

        self.lbl_cue_id = tk.Label(panel, text="", font=tkfont.Font(size=14, weight="bold"),
                                   fg="#e94560", bg="#16213e", anchor="w")
        self.lbl_cue_id.pack(fill=tk.X)

        self.lbl_name = tk.Label(panel, text="", font=tkfont.Font(size=15, weight="bold"),
                                 fg="white", bg="#16213e", anchor="w", wraplength=330, justify=tk.LEFT)
        self.lbl_name.pack(fill=tk.X, pady=(6, 4))

        self.lbl_meta = tk.Label(panel, text="", font=small_font, fg="#a0d2ff", bg="#16213e",
                                 anchor="w", wraplength=330, justify=tk.LEFT)
        self.lbl_meta.pack(fill=tk.X, pady=4)

        tk.Label(panel, text="TRIGGER", font=small_font, fg="#a0a0b0",
                 bg="#16213e", anchor="w").pack(fill=tk.X, pady=(8, 2))
        self.lbl_trigger = tk.Label(panel, text="", font=med_font, fg="#f5f5f5", bg="#16213e",
                                    anchor="w", wraplength=330, justify=tk.LEFT)
        self.lbl_trigger.pack(fill=tk.X)

        tk.Label(panel, text="UPCOMING EFFECT", font=small_font, fg="#a0a0b0",
                 bg="#16213e", anchor="w").pack(fill=tk.X, pady=(8, 2))
        self.lbl_upcoming = tk.Label(panel, text="", font=med_font, fg="#7ec8a3", bg="#16213e",
                                     anchor="w", wraplength=330, justify=tk.LEFT)
        self.lbl_upcoming.pack(fill=tk.X)

        self.status = tk.Label(controls, text="", font=small_font, fg="#a0a0b0", bg="#1a1a2e",
                               wraplength=360)
        self.status.pack(pady=(0, 8), padx=12)

        self.script_panel = ScriptPanel(
            script_host,
            self.all_cues,
            on_page_visible=self._on_script_page_visible,
            on_cue_clicked=self._on_script_cue_clicked,
        )
        self.script_panel.pack(fill=tk.BOTH, expand=True)

    def _build_background_panel(self, parent, med_font, small_font):
        panel = tk.Frame(parent, bg="#0f3460", padx=12, pady=10)
        panel.pack(fill=tk.X, padx=10, pady=(6, 0))

        tk.Label(panel, text="BACKGROUND", font=tkfont.Font(size=11, weight="bold"),
                 fg="#a0d2ff", bg="#0f3460").grid(row=0, column=0, columnspan=6, sticky="w")

        tk.Label(panel, text="Queue:", font=small_font, fg="#c0c0d0", bg="#0f3460").grid(
            row=1, column=0, sticky="nw", pady=(6, 0))
        self.lbl_bg_queue = tk.Label(
            panel, text="—", font=small_font, fg="white", bg="#0f3460",
            wraplength=220, justify=tk.LEFT, anchor="w",
        )
        self.lbl_bg_queue.grid(row=1, column=1, columnspan=2, sticky="w", padx=(4, 8), pady=(6, 0))

        bg_nav = tk.Frame(panel, bg="#0f3460")
        bg_nav.grid(row=2, column=0, columnspan=6, sticky="w", pady=(8, 0))
        btn_nav = {"font": small_font, "bg": "#16213e", "fg": "white",
                   "activebackground": "#1a1a2e", "relief": tk.FLAT, "padx": 8, "pady": 4}
        tk.Button(bg_nav, text="◀ PREV", command=self.prev_background, **btn_nav).pack(
            side=tk.LEFT, padx=(0, 4))
        tk.Button(bg_nav, text="GO ▶", command=self.play_background_cue,
                  bg="#e94560", fg="white", font=small_font, relief=tk.FLAT,
                  padx=10, pady=4, activebackground="#c73652").pack(side=tk.LEFT, padx=4)
        tk.Button(bg_nav, text="NEXT ▶", command=self.next_background, **btn_nav).pack(
            side=tk.LEFT, padx=(4, 0))

        tk.Label(panel, text="Playing:", font=small_font, fg="#c0c0d0", bg="#0f3460").grid(
            row=3, column=0, sticky="w", pady=(8, 0))
        self.lbl_bg_name = tk.Label(panel, text="—", font=small_font, fg="white", bg="#0f3460")
        self.lbl_bg_name.grid(row=3, column=1, sticky="w", padx=(4, 0), pady=(8, 0))

        tk.Label(panel, text="Status:", font=small_font, fg="#c0c0d0", bg="#0f3460").grid(
            row=3, column=2, sticky="w", padx=(12, 0), pady=(8, 0))
        self.lbl_bg_status = tk.Label(panel, text="Stopped", font=small_font, fg="#f5d76e", bg="#0f3460")
        self.lbl_bg_status.grid(row=3, column=3, sticky="w", padx=(4, 0), pady=(8, 0))

        tk.Label(panel, text="Elapsed:", font=small_font, fg="#c0c0d0", bg="#0f3460").grid(
            row=4, column=0, sticky="w", pady=(4, 0))
        self.lbl_bg_elapsed = tk.Label(panel, text="0:00", font=small_font, fg="white", bg="#0f3460")
        self.lbl_bg_elapsed.grid(row=4, column=1, sticky="w", padx=(4, 0), pady=(4, 0))

        btn_row = tk.Frame(panel, bg="#0f3460")
        btn_row.grid(row=5, column=0, columnspan=6, sticky="w", pady=(8, 2))

        btn_style = {"font": small_font, "bg": "#16213e", "fg": "white",
                     "activebackground": "#1a1a2e", "relief": tk.FLAT, "padx": 6, "pady": 3}
        tk.Button(btn_row, text="Play", command=self._bg_play, **btn_style).pack(side=tk.LEFT, padx=(0, 4))
        tk.Button(btn_row, text="Pause", command=self._bg_pause, **btn_style).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_row, text="Stop", command=self._bg_stop, **btn_style).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_row, text="Fade Out", command=self._bg_fade_out, **btn_style).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_row, text="Switch", command=self._bg_switch_to_expected, **btn_style).pack(
            side=tk.LEFT, padx=4)

        vol_row = tk.Frame(panel, bg="#0f3460")
        vol_row.grid(row=6, column=0, columnspan=6, sticky="w", pady=(4, 0))
        tk.Label(vol_row, text="Vol:", font=small_font, fg="#c0c0d0", bg="#0f3460").pack(side=tk.LEFT)
        self.bg_volume = tk.IntVar(value=30)
        self.bg_volume_scale = tk.Scale(
            vol_row, from_=0, to=100, orient=tk.HORIZONTAL, length=180,
            variable=self.bg_volume, command=self._on_bg_volume, bg="#0f3460", fg="white",
            highlightthickness=0, troughcolor="#16213e", activebackground="#e94560",
        )
        self.bg_volume_scale.pack(side=tk.LEFT, padx=(6, 0))

    def _bind_keys(self):
        self.bind("<space>", self._on_space)
        self.bind("<Left>", lambda e: self.prev_foreground())
        self.bind("<Right>", lambda e: self.next_foreground())
        self.bind("<Return>", lambda e: self.play_foreground_cue())
        self.bind("<Escape>", self._on_escape)

    def _on_space(self, _event=None):
        self.next_foreground()
        return "break"

    def _on_escape(self, _event=None):
        self.stop_all()
        return "break"

    def _expected_background(self, cue: dict) -> str | None:
        return cue.get("expected_background_asset_id") or None

    def _current_background(self) -> str | None:
        if not self.player:
            return None
        return self.player.current_background_asset_id()

    def _backgrounds_match(self, cue: dict) -> bool | None:
        expected = self._expected_background(cue)
        if not expected:
            return None
        return self._current_background() == expected

    def _active_script_ids(self) -> tuple[str | None, str | None]:
        fg_id = self._foreground_cue()["id"]
        bg_id = self._background_cue()["id"] if self.background_cues else None
        return fg_id, bg_id

    def _sync_script_from_foreground(self):
        if not self.script_panel or not self.script_panel.doc:
            return
        self._script_sync_lock = True
        fg_id, bg_id = self._active_script_ids()
        self.script_panel.scroll_to_cue(self._foreground_cue(), fg_id=fg_id, bg_id=bg_id)
        self.after(300, self._release_script_sync)

    def _sync_script_from_background(self):
        if not self.script_panel or not self.script_panel.doc:
            return
        self._script_sync_lock = True
        fg_id, bg_id = self._active_script_ids()
        self.script_panel.scroll_to_cue(self._background_cue(), fg_id=fg_id, bg_id=bg_id)
        self.after(300, self._release_script_sync)

    def _sync_script_to_queues(self):
        self._sync_script_from_foreground()

    def _release_script_sync(self):
        self._script_sync_lock = False
        if self.script_panel:
            self.script_panel.release_sync_lock()


    def _on_script_page_visible(self, page: int):
        if self._script_sync_lock:
            return
        self._script_sync_lock = True
        new_fg = queue_index_for_page(self.foreground_cues, page)
        new_bg = queue_index_for_page(self.background_cues, page) if self.background_cues else 0
        if new_fg != self.fg_index:
            self.fg_index = new_fg
            self._refresh_foreground()
        if self.background_cues and new_bg != self.bg_index:
            self.bg_index = new_bg
            self._refresh_background()
        if self.script_panel:
            fg_id, bg_id = self._active_script_ids()
            self.script_panel.set_active_cues(fg_id=fg_id, bg_id=bg_id)
        self.after(80, lambda: setattr(self, "_script_sync_lock", False))

    def _asset_summary(self, cue: dict) -> str:
        asset_id = cue.get("asset_id", "")
        asset = self.assets_by_id.get(asset_id, {})
        name = asset.get("name") or asset_id or "—"
        filename = cue.get("asset_filename") or asset.get("filename", "")
        mode = cue.get("playback_mode") or asset.get("playback_mode", "")
        parts = [f"{asset_id} — {name}"]
        if mode:
            parts.append(mode)
        if filename:
            parts.append(Path(filename).name)
        return "  |  ".join(parts)

    def _on_script_cue_clicked(self, cue: dict):
        if cue_type(cue) == "FOREGROUND":
            for i, item in enumerate(self.foreground_cues):
                if item["id"] == cue["id"]:
                    self.fg_index = i
                    self._refresh_foreground()
                    break
            self._sync_script_from_foreground()
            self.status.config(
                text=f"▸ Effect {cue['id']} — {self._asset_summary(cue)}"
            )
        else:
            for i, item in enumerate(self.background_cues):
                if item["id"] == cue["id"]:
                    self.bg_index = i
                    self._refresh_background()
                    break
            self._sync_script_from_background()
            self.status.config(
                text=f"▸ Background {cue['id']} — {self._asset_summary(cue)}"
            )
        self._refresh_sync_banner(self._foreground_cue())

    def _refresh_sync_banner(self, cue: dict):
        match = self._backgrounds_match(cue)
        if match is None:
            self.sync_banner.config(bg="#16213e")
            self.lbl_sync.config(bg="#16213e", fg="#a0a0b0", text="")
            return

        current_label = self._asset_label(self._current_background())
        expected_label = self._asset_label(self._expected_background(cue))

        if match or self._ignore_mismatch_for == cue["id"]:
            self.sync_banner.config(bg="#1b4332")
            self.lbl_sync.config(
                bg="#1b4332", fg="#95d5b2",
                text=f"✓  Background in sync — {expected_label}",
            )
        else:
            self.sync_banner.config(bg="#7f4f00")
            self.lbl_sync.config(
                bg="#7f4f00", fg="#ffe08a",
                text=f"⚠  Expected: {expected_label}  (current: {current_label})",
            )

    def _refresh_background_playback(self):
        if not self.player:
            return
        asset_id = self.player.current_background_asset_id()
        self.lbl_bg_name.config(text=self._asset_label(asset_id))

        if asset_id is None:
            self.lbl_bg_status.config(text="Stopped", fg="#a0a0b0")
        elif self.player.background_is_playing():
            self.lbl_bg_status.config(text="Playing", fg="#7ec8a3")
        elif self.player.background_is_active():
            self.lbl_bg_status.config(text="Paused", fg="#f5d76e")
        else:
            self.lbl_bg_status.config(text="Stopped", fg="#a0a0b0")

        self.lbl_bg_elapsed.config(text=_format_elapsed(self.player.background_elapsed_seconds()))
        self.bg_volume.set(self.player.background_volume())

    def _refresh_background(self):
        if not self.background_cues:
            self.lbl_bg_queue.config(text="(no background cues)")
            self._refresh_background_playback()
            return

        c = self._background_cue()
        nxt = (
            self.background_cues[self.bg_index + 1]
            if self.bg_index + 1 < len(self.background_cues)
            else None
        )
        queue_text = f"{c['id']} p.{c['page']} — {c['name']}\n{self._asset_summary(c)}"
        if nxt:
            queue_text += f"\nNext: {nxt['id']}"
        self.lbl_bg_queue.config(text=queue_text)
        self._refresh_background_playback()

    def _refresh_foreground(self):
        c = self._foreground_cue()
        nxt = (
            self.foreground_cues[self.fg_index + 1]
            if self.fg_index + 1 < len(self.foreground_cues)
            else None
        )
        expected = self._expected_background(c)
        expected_text = self._asset_label(expected) if expected else "—"

        self.lbl_cue_id.config(text=f"{c['id']}  •  p.{c['page']}  •  {c['category']}")
        self.lbl_name.config(text=c["name"])
        self.lbl_meta.config(
            text=(
                f"Asset: {self._asset_summary(c)}  |  "
                f"Scene: {c['scene'][:36]}  |  Vol {c['volume']}  |  "
                f"Expected BG: {expected_text}"
            )
        )
        self.lbl_trigger.config(text=c["trigger"])
        self.lbl_upcoming.config(
            text=f"{nxt['id']} p.{nxt['page']} — {nxt['name']}" if nxt else "(end of effects)"
        )
        self.status.config(
            text=f"Effect {self.fg_index + 1}/{len(self.foreground_cues)}  |  "
                 f"BG queue {self.bg_index + 1}/{len(self.background_cues)}"
        )
        self._refresh_sync_banner(c)

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
        self._refresh_background()
        self._refresh_sync_banner(self._foreground_cue())

    def _bg_fade_out(self):
        if not self.player or not self.player.background_is_active():
            return
        start = self.player.background_volume()

        def finish():
            if self.player:
                self.player.stop_background()
            self._refresh_background()
            self._refresh_sync_banner(self._foreground_cue())

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
            self._refresh_background()
            self._refresh_sync_banner(self._foreground_cue())

        if self.player.background_is_active() and cue.get("category") != "Silence":
            start_vol = self.player.background_volume()

            def after_fade():
                self.player.stop_background()
                run_background()

            self._fade_background_volume(start_vol, 0, 1000, on_complete=after_fade)
        else:
            run_background()

    def play_background_cue(self):
        if self.background_cues:
            self._execute_background_go(self._background_cue())

    def _switch_to_asset(self, asset_id: str) -> tuple[bool, str]:
        if not self.player:
            return False, "Playback unavailable"
        idx = self._bg_index_for_asset(asset_id)
        cue = self.background_cues[idx] if idx is not None else None
        if cue:
            self.bg_index = idx
        else:
            cue = self.player.background_cue_for_asset(asset_id, self.background_cues)
        if not cue:
            return False, f"No background cue for {asset_id}"
        self._execute_background_go(cue)
        return True, f"Switched to {cue['name']}"

    def _bg_switch_to_expected(self):
        expected = self._expected_background(self._foreground_cue())
        if not expected:
            self.status.config(text="No expected background on current effect")
            return
        ok, message = self._switch_to_asset(expected)
        self.status.config(text=f"{'▶' if ok else '⚠'} {message}")

    def _show_mismatch_dialog(self, cue: dict, on_continue):
        expected = self._expected_background(cue)
        current = self._current_background()
        dialog = tk.Toplevel(self)
        dialog.title("Background Out of Sync")
        dialog.configure(bg="#3d1f00")
        dialog.transient(self)
        dialog.grab_set()
        dialog.geometry("420x260")

        tk.Label(dialog, text="⚠ BACKGROUND OUT OF SYNC",
                 font=tkfont.Font(size=14, weight="bold"), fg="#ffe08a", bg="#3d1f00").pack(pady=(16, 10))
        body = tk.Frame(dialog, bg="#3d1f00")
        body.pack(fill=tk.X, padx=20)
        tk.Label(body, text=f"Current: {self._asset_label(current)}", fg="white", bg="#3d1f00",
                 font=tkfont.Font(size=11)).pack(anchor="w")
        tk.Label(body, text=f"Expected: {self._asset_label(expected)}", fg="#95d5b2", bg="#3d1f00",
                 font=tkfont.Font(size=11)).pack(anchor="w", pady=(6, 0))

        btn_row = tk.Frame(dialog, bg="#3d1f00")
        btn_row.pack(pady=16)

        def switch_and_go():
            if expected:
                self._switch_to_asset(expected)
            dialog.destroy()
            on_continue()

        def ignore_and_go():
            self._ignore_mismatch_for = cue["id"]
            dialog.destroy()
            self._refresh_sync_banner(cue)
            on_continue()

        tk.Button(btn_row, text="Switch Background", command=switch_and_go,
                  bg="#e94560", fg="white", relief=tk.FLAT, padx=10, pady=6).pack(side=tk.LEFT, padx=6)
        tk.Button(btn_row, text="Ignore", command=ignore_and_go,
                  bg="#16213e", fg="white", relief=tk.FLAT, padx=10, pady=6).pack(side=tk.LEFT, padx=6)

    def _execute_foreground_go(self, cue: dict):
        if not self.player:
            self.status.config(text="Playback unavailable — install python-vlc and VLC")
            return
        ok, message = self.player.play_foreground(cue)
        self.status.config(text=f"{'▶' if ok else '⚠'} {cue['id']} — {message}")
        self._refresh_background_playback()
        self._refresh_sync_banner(cue)

    def play_foreground_cue(self):
        c = self._foreground_cue()
        if not self.player:
            self.status.config(text="Playback unavailable — install python-vlc and VLC")
            return
        match = self._backgrounds_match(c)
        if match is False and self._ignore_mismatch_for != c["id"]:
            self._show_mismatch_dialog(c, lambda: self._execute_foreground_go(c))
            return
        self._execute_foreground_go(c)

    def stop_all(self):
        self._cancel_fade()
        if self.player:
            self.player.stop_all()
        self.status.config(text=f"■ Stopped all — effect {self._foreground_cue()['id']}")
        self._refresh_background()
        self._refresh_sync_banner(self._foreground_cue())

    def next_foreground(self):
        if self.fg_index < len(self.foreground_cues) - 1:
            self.fg_index += 1
            self._refresh_foreground()
            self._sync_script_from_foreground()

    def prev_foreground(self):
        if self.fg_index > 0:
            self.fg_index -= 1
            self._refresh_foreground()
            self._sync_script_from_foreground()

    def next_background(self):
        if self.bg_index < len(self.background_cues) - 1:
            self.bg_index += 1
            self._refresh_background()
            self._sync_script_from_background()

    def prev_background(self):
        if self.bg_index > 0:
            self.bg_index -= 1
            self._refresh_background()
            self._sync_script_from_background()

    def _on_bg_volume(self, _value):
        if self.player:
            self.player.set_background_volume(self.bg_volume.get())

    def _on_close(self):
        self._cancel_fade()
        if self._tick_job:
            self.after_cancel(self._tick_job)
        if self.player:
            self.player.stop_all()
        if self.script_panel:
            self.script_panel.close()
        self.destroy()


def main():
    app = SoundboardApp()
    app.mainloop()


if __name__ == "__main__":
    main()
