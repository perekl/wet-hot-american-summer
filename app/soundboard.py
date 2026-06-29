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
        self.foreground_cues = [c for c in self.all_cues if cue_type(c) == "FOREGROUND"]
        self.background_cues = [c for c in self.all_cues if cue_type(c) == "BACKGROUND"]
        self.assets_by_id = self.project.assets_by_id
        self.fg_index = 0
        self.bg_index = 0
        self.player = self._init_player()
        self._fade_job: str | None = None
        self._tick_job: str | None = None
        self.script_editor: ScriptEditor | None = None
        self._paned_split_done = False
        self._paned_split_retries = 0
        self._active_cue_id: str | None = None
        self._browser_rows: dict[str, tk.Frame] = {}
        self._browser_filter = tk.StringVar(value="")
        self._active_tab = "browser"
        self._browser_canvas_width = 0
        self._browser_resize_job: str | None = None

        self._build_ui()
        self._maximize_window()
        self.update_idletasks()
        self._bind_keys()
        self._rebuild_browser()
        self._refresh_performance()
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

    def _foreground_cue(self) -> dict:
        return self.foreground_cues[self.fg_index]

    def _background_cue(self) -> dict:
        return self.background_cues[self.bg_index]

    def _build_ui(self):
        small_font = tkfont.Font(family="Helvetica", size=10)
        med_font = tkfont.Font(family="Helvetica", size=12)

        self.paned = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashwidth=5, bg="#1a1a2e")
        self.paned.pack(fill=tk.BOTH, expand=True)

        left_host = tk.Frame(self.paned, bg="#1a1a2e")
        self.paned.add(left_host, minsize=280, stretch="always")

        script_host = tk.Frame(self.paned, bg="#0a0a12")
        self.paned.add(script_host, minsize=280, stretch="always")

        tk.Label(
            left_host, text="WET HOT AMERICAN SUMMER", font=tkfont.Font(size=15, weight="bold"),
            fg="#e94560", bg="#1a1a2e", wraplength=360,
        ).pack(pady=(10, 2), padx=12)

        tab_bar = tk.Frame(left_host, bg="#1a1a2e")
        tab_bar.pack(fill=tk.X, padx=12, pady=(4, 0))
        self._tab_buttons: dict[str, tk.Button] = {}
        for tab_id, label in (("browser", "Browser"), ("performance", "Performance")):
            btn = tk.Button(
                tab_bar, text=label, font=small_font, relief=tk.RAISED,
                bg="#16213e", fg="white", activebackground="#0f3460",
                padx=14, pady=4, command=lambda t=tab_id: self._show_tab(t),
            )
            btn.pack(side=tk.LEFT, padx=(0, 4))
            self._tab_buttons[tab_id] = btn

        self.tab_content = tk.Frame(left_host, bg="#1a1a2e")
        self.tab_content.pack(fill=tk.BOTH, expand=True)

        self.browser_tab = tk.Frame(self.tab_content, bg="#1a1a2e")
        self.performance_tab = tk.Frame(self.tab_content, bg="#1a1a2e")

        self._build_browser_tab(self.browser_tab, small_font)
        self._build_performance_tab(self.performance_tab, med_font, small_font)
        self._build_transport(left_host, small_font)
        self._show_tab("browser")

        self.script_editor = ScriptEditor(
            script_host,
            self.project,
            on_cue_selected=self._on_script_cue_clicked,
            on_cues_changed=self._on_project_updated,
        )
        self.script_editor.pack(fill=tk.BOTH, expand=True)

    def _show_tab(self, tab_id: str):
        self._active_tab = tab_id
        self.browser_tab.pack_forget()
        self.performance_tab.pack_forget()
        if tab_id == "browser":
            self.browser_tab.pack(fill=tk.BOTH, expand=True)
        else:
            self.performance_tab.pack(fill=tk.BOTH, expand=True)
        for name, btn in self._tab_buttons.items():
            btn.configure(relief=tk.SUNKEN if name == tab_id else tk.RAISED)

    def _build_browser_tab(self, parent, small_font):
        filter_row = tk.Frame(parent, bg="#1a1a2e")
        filter_row.pack(fill=tk.X, padx=4, pady=(6, 4))
        tk.Label(filter_row, text="Filter:", fg="#a0a0b0", bg="#1a1a2e",
                 font=small_font).pack(side=tk.LEFT)
        ent = tk.Entry(
            filter_row, textvariable=self._browser_filter, bg="#16213e", fg="white",
            insertbackground="white", relief=tk.FLAT,
        )
        ent.pack(side=tk.LEFT, padx=6, fill=tk.X, expand=True)
        self._browser_filter.trace_add("write", lambda *_: self._rebuild_browser())

        list_body = tk.Frame(parent, bg="#1a1a2e")
        list_body.pack(fill=tk.BOTH, expand=True, padx=4)

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

    def _build_performance_tab(self, parent, med_font, small_font):
        bg_panel = tk.Frame(parent, bg="#0f3460", padx=12, pady=10)
        bg_panel.pack(fill=tk.X, padx=8, pady=(6, 0))

        tk.Label(bg_panel, text="BACKGROUND", font=tkfont.Font(size=11, weight="bold"),
                 fg="#a0d2ff", bg="#0f3460").grid(row=0, column=0, columnspan=4, sticky="w")

        tk.Label(bg_panel, text="Queue:", font=small_font, fg="#c0c0d0", bg="#0f3460").grid(
            row=1, column=0, sticky="nw", pady=(6, 0))
        self.lbl_bg_queue = tk.Label(
            bg_panel, text="—", font=small_font, fg="white", bg="#0f3460",
            wraplength=260, justify=tk.LEFT, anchor="w",
        )
        self.lbl_bg_queue.grid(row=1, column=1, columnspan=3, sticky="w", padx=(4, 0), pady=(6, 0))

        bg_nav = tk.Frame(bg_panel, bg="#0f3460")
        bg_nav.grid(row=2, column=0, columnspan=4, sticky="w", pady=(8, 0))
        btn_nav = {"font": small_font, "bg": "#16213e", "fg": "white",
                   "activebackground": "#1a1a2e", "relief": tk.FLAT, "padx": 8, "pady": 4}
        tk.Button(bg_nav, text="◀ PREV", command=self.prev_background, **btn_nav).pack(side=tk.LEFT, padx=(0, 4))
        tk.Button(bg_nav, text="GO ▶", command=self.play_background_cue,
                  bg="#e94560", fg="white", font=small_font, relief=tk.FLAT,
                  padx=10, pady=4, activebackground="#c73652").pack(side=tk.LEFT, padx=4)
        tk.Button(bg_nav, text="NEXT ▶", command=self.next_background, **btn_nav).pack(side=tk.LEFT, padx=(4, 0))

        tk.Label(parent, text="EFFECTS", font=tkfont.Font(size=11, weight="bold"),
                 fg="#a0d2ff", bg="#1a1a2e").pack(anchor="w", padx=12, pady=(10, 0))

        nav = tk.Frame(parent, bg="#1a1a2e")
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

        tk.Label(parent, text="Space = next  |  Enter = GO  |  Esc = stop all",
                 font=small_font, fg="#a0a0b0", bg="#1a1a2e", wraplength=340).pack(padx=12)

        panel = tk.Frame(parent, bg="#16213e", padx=14, pady=12)
        panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=(6, 4))

        self.lbl_cue_id = tk.Label(panel, text="", font=tkfont.Font(size=14, weight="bold"),
                                   fg="#e94560", bg="#16213e", anchor="w")
        self.lbl_cue_id.pack(fill=tk.X)
        self.lbl_name = tk.Label(panel, text="", font=tkfont.Font(size=15, weight="bold"),
                                 fg="white", bg="#16213e", anchor="w", wraplength=320, justify=tk.LEFT)
        self.lbl_name.pack(fill=tk.X, pady=(6, 4))
        self.lbl_meta = tk.Label(panel, text="", font=small_font, fg="#a0d2ff", bg="#16213e",
                                 anchor="w", wraplength=320, justify=tk.LEFT)
        self.lbl_meta.pack(fill=tk.X, pady=4)
        tk.Label(panel, text="TRIGGER", font=small_font, fg="#a0a0b0",
                 bg="#16213e", anchor="w").pack(fill=tk.X, pady=(8, 2))
        self.lbl_trigger = tk.Label(panel, text="", font=med_font, fg="#f5f5f5", bg="#16213e",
                                    anchor="w", wraplength=320, justify=tk.LEFT)
        self.lbl_trigger.pack(fill=tk.X)
        tk.Label(panel, text="UPCOMING EFFECT", font=small_font, fg="#a0a0b0",
                 bg="#16213e", anchor="w").pack(fill=tk.X, pady=(8, 2))
        self.lbl_upcoming = tk.Label(panel, text="", font=med_font, fg="#7ec8a3", bg="#16213e",
                                     anchor="w", wraplength=320, justify=tk.LEFT)
        self.lbl_upcoming.pack(fill=tk.X)

    def _build_transport(self, parent, small_font):
        transport = tk.Frame(parent, bg="#0f3460", padx=12, pady=10)
        transport.pack(fill=tk.X, padx=10, pady=(4, 0))

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

        self.status = tk.Label(parent, text="Click a cue in the script or browser to play.",
                               font=small_font, fg="#a0a0b0", bg="#1a1a2e", wraplength=360)
        self.status.pack(pady=(0, 8), padx=12)

    def _on_browser_configure(self, event=None):
        if event is not None:
            self.browser_canvas.configure(scrollregion=(0, 0, event.width, max(event.height, 1)))

    def _on_browser_canvas_configure(self, event):
        new_width = event.width
        if abs(new_width - self._browser_canvas_width) < 4:
            return
        self._browser_canvas_width = new_width
        if self._browser_resize_job:
            self.after_cancel(self._browser_resize_job)
        self._browser_resize_job = self.after(80, lambda w=new_width: self._apply_browser_width(w))

    def _apply_browser_width(self, width: int):
        self._browser_resize_job = None
        self.browser_canvas.itemconfig(self._browser_window, width=width)

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

    def _set_active_cue(self, cue: dict):
        self._highlight_browser_cue(cue["id"])
        for i, item in enumerate(self.foreground_cues):
            if item["id"] == cue["id"]:
                self.fg_index = i
                break
        for i, item in enumerate(self.background_cues):
            if item["id"] == cue["id"]:
                self.bg_index = i
                break
        self._refresh_performance()

    def _refresh_performance(self):
        if not self.foreground_cues:
            return
        c = self._foreground_cue()
        nxt = (
            self.foreground_cues[self.fg_index + 1]
            if self.fg_index + 1 < len(self.foreground_cues)
            else None
        )
        self.lbl_cue_id.config(text=f"{c['id']}  •  p.{c['page']}  •  {c['category']}")
        self.lbl_name.config(text=c["name"])
        self.lbl_meta.config(
            text=f"Asset: {self._asset_summary(c)}  |  Scene: {c['scene'][:36]}  |  Vol {c['volume']}"
        )
        self.lbl_trigger.config(text=c["trigger"])
        self.lbl_upcoming.config(
            text=f"{nxt['id']} p.{nxt['page']} — {nxt['name']}" if nxt else "(end of effects)"
        )

        if self.background_cues:
            bg = self._background_cue()
            nxt_bg = (
                self.background_cues[self.bg_index + 1]
                if self.bg_index + 1 < len(self.background_cues)
                else None
            )
            queue_text = f"{bg['id']} p.{bg['page']} — {bg['name']}\n{self._asset_summary(bg)}"
            if nxt_bg:
                queue_text += f"\nNext: {nxt_bg['id']}"
            self.lbl_bg_queue.config(text=queue_text)
        else:
            self.lbl_bg_queue.config(text="(no background cues)")

        self.status.config(
            text=f"Effect {self.fg_index + 1}/{len(self.foreground_cues)}  |  "
                 f"BG {self.bg_index + 1}/{len(self.background_cues)}"
        )

    def _sync_script_to_cue(self, cue: dict):
        if self.script_editor:
            self.script_editor.scroll_to_cue(cue, fg_id=cue["id"])

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

    def _on_project_updated(self):
        self.project.load()
        self.all_cues = self.project.get_cues_sorted()
        self.foreground_cues = [c for c in self.all_cues if cue_type(c) == "FOREGROUND"]
        self.background_cues = [c for c in self.all_cues if cue_type(c) == "BACKGROUND"]
        self.assets_by_id = self.project.assets_by_id
        if self.foreground_cues:
            self.fg_index = min(self.fg_index, len(self.foreground_cues) - 1)
        if self.background_cues:
            self.bg_index = min(self.bg_index, len(self.background_cues) - 1)
        self._rebuild_browser()
        self._refresh_performance()

    def _on_script_cue_clicked(self, cue: dict):
        self._play_cue(cue)

    def _play_cue(self, cue: dict):
        self._set_active_cue(cue)
        if cue_type(cue) == "BACKGROUND":
            self._execute_background_go(cue)
        else:
            self._execute_foreground_go(cue)
        self._sync_script_to_cue(cue)
        self.lbl_now_playing.config(text=f"{cue['id']} — {cue['name']}\n{self._asset_summary(cue)}")

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

    def play_background_cue(self):
        if not self.background_cues:
            return
        cue = self._background_cue()
        self._set_active_cue(cue)
        self._execute_background_go(cue)
        self._sync_script_to_cue(cue)
        self.lbl_now_playing.config(text=f"{cue['id']} — {cue['name']}\n{self._asset_summary(cue)}")

    def _execute_foreground_go(self, cue: dict):
        if not self.player:
            self.status.config(text="Playback unavailable — install python-vlc and VLC")
            return
        ok, message = self.player.play_foreground(cue)
        self.status.config(text=f"{'▶' if ok else '⚠'} {cue['id']} — {message}")
        self._refresh_background_playback()

    def play_foreground_cue(self):
        if not self.foreground_cues:
            return
        cue = self._foreground_cue()
        self._set_active_cue(cue)
        self._execute_foreground_go(cue)
        self._sync_script_to_cue(cue)
        self.lbl_now_playing.config(text=f"{cue['id']} — {cue['name']}\n{self._asset_summary(cue)}")

    def stop_all(self):
        self._cancel_fade()
        if self.player:
            self.player.stop_all()
        self.status.config(text="■ Stopped all playback")
        self._refresh_background_playback()

    def next_foreground(self):
        if self.fg_index < len(self.foreground_cues) - 1:
            self.fg_index += 1
            self._refresh_performance()
            self._sync_script_to_cue(self._foreground_cue())

    def prev_foreground(self):
        if self.fg_index > 0:
            self.fg_index -= 1
            self._refresh_performance()
            self._sync_script_to_cue(self._foreground_cue())

    def next_background(self):
        if self.bg_index < len(self.background_cues) - 1:
            self.bg_index += 1
            self._refresh_performance()
            self._sync_script_to_cue(self._background_cue())

    def prev_background(self):
        if self.bg_index > 0:
            self.bg_index -= 1
            self._refresh_performance()
            self._sync_script_to_cue(self._background_cue())

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
