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
from playback import VLCPlaybackEngine  # noqa: E402


def _format_elapsed(seconds: float) -> str:
    total = max(0, int(seconds))
    minutes, secs = divmod(total, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


class SoundboardApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("WHAS Table Read — Soundboard")
        self.geometry("900x750")
        self.configure(bg="#1a1a2e")

        self.cues = self._load_cues()
        self.assets_by_id = self._load_assets()
        self.index = 0
        self.player = self._init_player()
        self._fade_job: str | None = None
        self._tick_job: str | None = None
        self._ignore_mismatch_for: str | None = None

        self._build_ui()
        self._bind_keys()
        self._refresh()
        self._start_background_tick()
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

    def _build_ui(self):
        title_font = tkfont.Font(family="Helvetica", size=22, weight="bold")
        big_font = tkfont.Font(family="Helvetica", size=18, weight="bold")
        med_font = tkfont.Font(family="Helvetica", size=13)
        small_font = tkfont.Font(family="Helvetica", size=11)

        header = tk.Label(self, text="WET HOT AMERICAN SUMMER", font=title_font,
                          fg="#e94560", bg="#1a1a2e")
        header.pack(pady=(12, 2))

        self._build_background_panel(med_font, small_font)

        nav = tk.Frame(self, bg="#1a1a2e")
        nav.pack(pady=6)

        self.btn_prev = tk.Button(nav, text="◀  PREVIOUS", font=med_font, width=14,
                                  command=self.prev_cue, bg="#16213e", fg="white",
                                  activebackground="#0f3460", relief=tk.FLAT, padx=8, pady=8)
        self.btn_prev.grid(row=0, column=0, padx=12)

        self.btn_play = tk.Button(nav, text="▶  GO", font=tkfont.Font(size=28, weight="bold"),
                                  width=8, command=self.play_cue, bg="#e94560", fg="white",
                                  activebackground="#c73652", relief=tk.FLAT, padx=16, pady=12)
        self.btn_play.grid(row=0, column=1, padx=12)

        self.btn_next = tk.Button(nav, text="NEXT  ▶", font=med_font, width=14,
                                  command=self.next_cue, bg="#16213e", fg="white",
                                  activebackground="#0f3460", relief=tk.FLAT, padx=8, pady=8)
        self.btn_next.grid(row=0, column=2, padx=12)

        tk.Label(self, text="SPACEBAR = NEXT CUE  |  ENTER = GO  |  ESC = STOP ALL",
                 font=small_font, fg="#a0a0b0", bg="#1a1a2e").pack()

        panel = tk.Frame(self, bg="#16213e", padx=24, pady=16)
        panel.pack(fill=tk.BOTH, expand=True, padx=24, pady=(8, 12))

        self.sync_banner = tk.Frame(panel, bg="#16213e")
        self.sync_banner.pack(fill=tk.X, pady=(0, 10))
        self.lbl_sync = tk.Label(self.sync_banner, text="", font=med_font,
                                 bg="#16213e", anchor="w", wraplength=820, justify=tk.LEFT)
        self.lbl_sync.pack(fill=tk.X)

        self.lbl_cue_id = tk.Label(panel, text="", font=big_font, fg="#e94560", bg="#16213e", anchor="w")
        self.lbl_cue_id.pack(fill=tk.X)

        self.lbl_name = tk.Label(panel, text="", font=tkfont.Font(size=20, weight="bold"),
                                 fg="white", bg="#16213e", anchor="w", wraplength=820, justify=tk.LEFT)
        self.lbl_name.pack(fill=tk.X, pady=(8, 4))

        self.lbl_meta = tk.Label(panel, text="", font=med_font, fg="#a0d2ff", bg="#16213e", anchor="w")
        self.lbl_meta.pack(fill=tk.X, pady=4)

        tk.Label(panel, text="TRIGGER DIALOGUE", font=small_font, fg="#a0a0b0",
                 bg="#16213e", anchor="w").pack(fill=tk.X, pady=(12, 2))
        self.lbl_trigger = tk.Label(panel, text="", font=med_font, fg="#f5f5f5", bg="#16213e",
                                    anchor="w", wraplength=820, justify=tk.LEFT)
        self.lbl_trigger.pack(fill=tk.X)

        tk.Label(panel, text="UPCOMING CUE", font=small_font, fg="#a0a0b0",
                 bg="#16213e", anchor="w").pack(fill=tk.X, pady=(12, 2))
        self.lbl_upcoming = tk.Label(panel, text="", font=med_font, fg="#7ec8a3", bg="#16213e",
                                     anchor="w", wraplength=820, justify=tk.LEFT)
        self.lbl_upcoming.pack(fill=tk.X)

        self.status = tk.Label(self, text="", font=small_font, fg="#a0a0b0", bg="#1a1a2e")
        self.status.pack(pady=(0, 10))

    def _build_background_panel(self, med_font, small_font):
        panel = tk.Frame(self, bg="#0f3460", padx=16, pady=12)
        panel.pack(fill=tk.X, padx=24, pady=(8, 0))

        tk.Label(panel, text="BACKGROUND", font=tkfont.Font(size=12, weight="bold"),
                 fg="#a0d2ff", bg="#0f3460").grid(row=0, column=0, columnspan=6, sticky="w")

        tk.Label(panel, text="Current:", font=small_font, fg="#c0c0d0", bg="#0f3460").grid(
            row=1, column=0, sticky="w", pady=(8, 0))
        self.lbl_bg_name = tk.Label(panel, text="—", font=med_font, fg="white", bg="#0f3460")
        self.lbl_bg_name.grid(row=1, column=1, columnspan=2, sticky="w", padx=(4, 16), pady=(8, 0))

        tk.Label(panel, text="Status:", font=small_font, fg="#c0c0d0", bg="#0f3460").grid(
            row=1, column=3, sticky="w", pady=(8, 0))
        self.lbl_bg_status = tk.Label(panel, text="Stopped", font=med_font, fg="#f5d76e", bg="#0f3460")
        self.lbl_bg_status.grid(row=1, column=4, sticky="w", padx=(4, 0), pady=(8, 0))

        tk.Label(panel, text="Elapsed:", font=small_font, fg="#c0c0d0", bg="#0f3460").grid(
            row=2, column=0, sticky="w", pady=(4, 0))
        self.lbl_bg_elapsed = tk.Label(panel, text="0:00", font=med_font, fg="white", bg="#0f3460")
        self.lbl_bg_elapsed.grid(row=2, column=1, sticky="w", padx=(4, 0), pady=(4, 0))

        btn_row = tk.Frame(panel, bg="#0f3460")
        btn_row.grid(row=3, column=0, columnspan=6, sticky="w", pady=(10, 4))

        btn_style = {"font": small_font, "bg": "#16213e", "fg": "white",
                     "activebackground": "#1a1a2e", "relief": tk.FLAT, "padx": 8, "pady": 4}
        tk.Button(btn_row, text="Play", command=self._bg_play, **btn_style).pack(side=tk.LEFT, padx=(0, 6))
        tk.Button(btn_row, text="Pause", command=self._bg_pause, **btn_style).pack(side=tk.LEFT, padx=6)
        tk.Button(btn_row, text="Stop", command=self._bg_stop, **btn_style).pack(side=tk.LEFT, padx=6)
        tk.Button(btn_row, text="Fade Out", command=self._bg_fade_out, **btn_style).pack(side=tk.LEFT, padx=6)
        tk.Button(btn_row, text="Switch", command=self._bg_switch_to_expected, **btn_style).pack(
            side=tk.LEFT, padx=6)

        vol_row = tk.Frame(panel, bg="#0f3460")
        vol_row.grid(row=4, column=0, columnspan=6, sticky="w", pady=(4, 0))
        tk.Label(vol_row, text="Volume:", font=small_font, fg="#c0c0d0", bg="#0f3460").pack(side=tk.LEFT)
        self.bg_volume = tk.IntVar(value=30)
        self.bg_volume_scale = tk.Scale(
            vol_row, from_=0, to=100, orient=tk.HORIZONTAL, length=220,
            variable=self.bg_volume, command=self._on_bg_volume, bg="#0f3460", fg="white",
            highlightthickness=0, troughcolor="#16213e", activebackground="#e94560",
        )
        self.bg_volume_scale.pack(side=tk.LEFT, padx=(8, 0))

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

    def _cue_type(self, cue: dict) -> str:
        if cue.get("cue_type"):
            return cue["cue_type"]
        if cue.get("category") == "Ambience":
            return "BACKGROUND"
        return "FOREGROUND"

    def _expected_background(self, cue: dict) -> str | None:
        expected = cue.get("expected_background_asset_id")
        if expected:
            return expected
        return None

    def _current_background(self) -> str | None:
        if not self.player:
            return None
        return self.player.current_background_asset_id()

    def _backgrounds_match(self, cue: dict) -> bool | None:
        """None when no expectation to check (background cue or no field)."""
        if self._cue_type(cue) == "BACKGROUND":
            return None
        expected = self._expected_background(cue)
        if not expected:
            return None
        current = self._current_background()
        return current == expected

    def _refresh_sync_banner(self, cue: dict):
        match = self._backgrounds_match(cue)
        if match is None:
            self.sync_banner.config(bg="#16213e")
            self.lbl_sync.config(bg="#16213e", fg="#a0a0b0", text="")
            return

        current = self._current_background()
        expected = self._expected_background(cue)
        current_label = self._asset_label(current)
        expected_label = self._asset_label(expected)

        if match or self._ignore_mismatch_for == cue["id"]:
            self.sync_banner.config(bg="#1b4332")
            self.lbl_sync.config(
                bg="#1b4332",
                fg="#95d5b2",
                text=f"✓  Background in sync — {expected_label}",
            )
        else:
            self.sync_banner.config(bg="#7f4f00")
            self.lbl_sync.config(
                bg="#7f4f00",
                fg="#ffe08a",
                text=(
                    f"⚠  Expected background: {expected_label}  "
                    f"(current: {current_label})"
                ),
            )

    def _refresh_background_panel(self):
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

    def _refresh(self):
        c = self.cues[self.index]
        nxt = self.cues[self.index + 1] if self.index + 1 < len(self.cues) else None

        cue_type = self._cue_type(c)
        expected = self._expected_background(c)
        expected_text = self._asset_label(expected) if expected else "—"

        self.lbl_cue_id.config(
            text=f"{c['id']}  •  Page {c['page']}  •  {c['category']}  •  {cue_type}"
        )
        self.lbl_name.config(text=c["name"])
        self.lbl_meta.config(
            text=(
                f"Asset: {c['asset_id']}  |  {c.get('playback_mode', '')}  |  "
                f"Scene: {c['scene']}  |  Priority: {c['priority']}  |  "
                f"Fade: {c['fade']}  |  Cue Vol: {c['volume']}  |  "
                f"Asset Vol: {c.get('suggested_volume', '')}  |  Loop: {c['loop']}  |  "
                f"Expected BG: {expected_text}"
            )
        )
        self.lbl_trigger.config(text=c["trigger"])
        if nxt:
            self.lbl_upcoming.config(text=f"{nxt['id']} (p.{nxt['page']}) — {nxt['name']}")
        else:
            self.lbl_upcoming.config(text="(end of show)")
        self.status.config(text=f"Cue {self.index + 1} of {len(self.cues)}")
        self._refresh_sync_banner(c)
        self._refresh_background_panel()

    def _start_background_tick(self):
        self._refresh_background_panel()
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
        if not self.player:
            return
        self.player.resume_background()

    def _bg_pause(self):
        if not self.player:
            return
        self.player.pause_background()

    def _bg_stop(self):
        if not self.player:
            return
        self._cancel_fade()
        self.player.stop_background()
        self._refresh_background_panel()
        self._refresh_sync_banner(self.cues[self.index])

    def _bg_fade_out(self):
        if not self.player or not self.player.background_is_active():
            return
        start = self.player.background_volume()

        def finish():
            if self.player:
                self.player.stop_background()
            self._refresh_background_panel()
            self._refresh_sync_banner(self.cues[self.index])

        self._fade_background_volume(start, 0, 1500, on_complete=finish)

    def _switch_to_asset(self, asset_id: str) -> tuple[bool, str]:
        if not self.player:
            return False, "Playback unavailable"
        cue = self.player.background_cue_for_asset(asset_id, self.cues)
        if not cue:
            return False, f"No background cue for {asset_id}"
        ok, message = self.player.play_background(cue, fade_in_ms=800)
        if ok:
            target = self.player.background_volume() if self.player.background_volume() else 30
            self._fade_background_volume(0, target, 800)
        self._refresh_background_panel()
        self._refresh_sync_banner(self.cues[self.index])
        return ok, message

    def _bg_switch_to_expected(self):
        cue = self.cues[self.index]
        expected = self._expected_background(cue)
        if not expected:
            self.status.config(text="No expected background on this cue")
            return
        ok, message = self._switch_to_asset(expected)
        prefix = "▶" if ok else "⚠"
        self.status.config(text=f"{prefix} Switched background — {message}")

    def _show_mismatch_dialog(self, cue: dict, on_continue):
        expected = self._expected_background(cue)
        current = self._current_background()
        dialog = tk.Toplevel(self)
        dialog.title("Background Out of Sync")
        dialog.configure(bg="#3d1f00")
        dialog.transient(self)
        dialog.grab_set()
        dialog.geometry("480x280")

        tk.Label(
            dialog, text="⚠  BACKGROUND OUT OF SYNC", font=tkfont.Font(size=16, weight="bold"),
            fg="#ffe08a", bg="#3d1f00",
        ).pack(pady=(20, 12))

        body = tk.Frame(dialog, bg="#3d1f00")
        body.pack(fill=tk.X, padx=24)
        tk.Label(body, text="Current", font=tkfont.Font(size=11), fg="#c0c0d0", bg="#3d1f00").pack(anchor="w")
        tk.Label(body, text=self._asset_label(current), font=tkfont.Font(size=14, weight="bold"),
                 fg="white", bg="#3d1f00").pack(anchor="w", pady=(0, 10))
        tk.Label(body, text="Expected", font=tkfont.Font(size=11), fg="#c0c0d0", bg="#3d1f00").pack(anchor="w")
        tk.Label(body, text=self._asset_label(expected), font=tkfont.Font(size=14, weight="bold"),
                 fg="#95d5b2", bg="#3d1f00").pack(anchor="w")

        btn_row = tk.Frame(dialog, bg="#3d1f00")
        btn_row.pack(pady=20)

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
                  bg="#e94560", fg="white", relief=tk.FLAT, padx=12, pady=8).pack(side=tk.LEFT, padx=8)
        tk.Button(btn_row, text="Ignore", command=ignore_and_go,
                  bg="#16213e", fg="white", relief=tk.FLAT, padx=12, pady=8).pack(side=tk.LEFT, padx=8)

    def _execute_go(self, cue: dict):
        if not self.player:
            self.status.config(text="Playback unavailable — install python-vlc and VLC")
            return

        cue_type = self._cue_type(cue)

        def run_background():
            ok, message = self.player.play_background(cue, fade_in_ms=800)
            if ok and cue.get("category") != "Silence":
                vol = resolve_volume_from_cue(cue)
                self._fade_background_volume(0, vol, 800)
            prefix = "▶" if ok else "⚠"
            self.status.config(text=f"{prefix} {cue['id']} — {message}  [{cue.get('asset_id')}]")
            self._refresh_background_panel()
            self._refresh_sync_banner(cue)

        if cue_type == "BACKGROUND":
            if self.player.background_is_active() and cue.get("category") != "Silence":
                start_vol = self.player.background_volume()
                def after_fade():
                    self.player.stop_background()
                    run_background()
                self._fade_background_volume(start_vol, 0, 1000, on_complete=after_fade)
            else:
                run_background()
            return

        ok, message = self.player.play_foreground(cue)
        prefix = "▶" if ok else "⚠"
        self.status.config(text=f"{prefix} {cue['id']} — {message}  [{cue.get('asset_id')}]")
        self._refresh_background_panel()
        self._refresh_sync_banner(cue)

    def play_cue(self):
        c = self.cues[self.index]
        if not self.player:
            self.status.config(text="Playback unavailable — install python-vlc and VLC")
            return

        if self._cue_type(c) == "FOREGROUND":
            match = self._backgrounds_match(c)
            if match is False and self._ignore_mismatch_for != c["id"]:
                self._show_mismatch_dialog(c, lambda: self._execute_go(c))
                return

        self._execute_go(c)

    def stop_all(self):
        self._cancel_fade()
        if self.player:
            self.player.stop_all()
        c = self.cues[self.index]
        self.status.config(text=f"■ Stopped all playback (ESC) — cue {c['id']}")
        self._refresh_background_panel()
        self._refresh_sync_banner(c)

    def next_cue(self):
        if self.index < len(self.cues) - 1:
            self.index += 1
            self._refresh()

    def prev_cue(self):
        if self.index > 0:
            self.index -= 1
            self._refresh()

    def _on_bg_volume(self, _value):
        if self.player:
            self.player.set_background_volume(self.bg_volume.get())

    def _on_close(self):
        self._cancel_fade()
        if self._tick_job:
            self.after_cancel(self._tick_job)
        if self.player:
            self.player.stop_all()
        self.destroy()


def resolve_volume_from_cue(cue: dict) -> int:
    volume = cue.get("volume")
    if isinstance(volume, int):
        return max(0, min(100, volume))
    if isinstance(volume, str) and volume.isdigit():
        return max(0, min(100, int(volume)))
    return max(0, min(100, int(cue.get("suggested_volume", 70))))


def main():
    app = SoundboardApp()
    app.mainloop()


if __name__ == "__main__":
    main()
