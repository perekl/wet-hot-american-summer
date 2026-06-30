"""Editable screenplay view replacing the PDF panel."""

from __future__ import annotations

import re
import tkinter as tk
from tkinter import font as tkfont, messagebox

from cue_dialogs import ask_edit_cue, ask_new_cue
from script_model import ScriptProject, _marker_kind

FX_COLOR = "#e94560"
BG_COLOR = "#4a90d9"
BG_STOP_COLOR = "#f5a623"
MUSIC_COLOR = "#b57edc"
PARA_SELECT_BG = "#1e3a5f"
PAGE_COLOR = "#8090a8"
SCENE_COLOR = "#a0d2ff"


def _cue_type(cue: dict) -> str:
    if cue.get("cue_type"):
        return cue["cue_type"]
    if cue.get("category") == "Ambience":
        return "BACKGROUND"
    return "FOREGROUND"


def _marker_color(cue: dict) -> str:
    kind = _marker_kind(cue)
    if kind == "BG":
        return BG_COLOR
    if kind == "BG_STOP":
        return BG_STOP_COLOR
    if kind == "MUSIC":
        return MUSIC_COLOR
    return FX_COLOR


def _marker_label(cue: dict) -> str:
    num = cue["id"].split("-")[-1]
    kind = _marker_kind(cue)
    if kind == "BG_STOP":
        return f"[BG STOP-{num}] {cue['name']}"
    if kind == "MUSIC":
        return f"[MUSIC-{num}] {cue['name']}"
    if kind == "BG":
        return f"[BG-{num}] {cue['name']}"
    return f"[FX-{num}] {cue['name']}"


def _tokenize(text: str) -> list[tuple[str, int]]:
    return [(m.group(), m.start()) for m in re.finditer(r"\S+|\s+", text)]


def _word_at_char_offset(para_text: str, offset: int) -> tuple[str, int] | None:
    if not para_text.strip():
        return None
    offset = max(0, min(offset, len(para_text)))
    last: tuple[str, int] | None = None
    for match in re.finditer(r"\S+", para_text):
        if match.start() <= offset <= match.end():
            return match.group(), match.start()
        if match.start() > offset:
            return match.group(), match.start()
        last = (match.group(), match.start())
    return last


class ScriptEditor(tk.Frame):
    """Scrollable screenplay editor with inline cue markers."""

    def __init__(
        self,
        parent,
        project: ScriptProject,
        *,
        on_cue_selected=None,
        on_cues_changed=None,
    ):
        super().__init__(parent, bg="#0a0a12")
        self.project = project
        self.on_cue_selected = on_cue_selected
        self.on_cues_changed = on_cues_changed
        self._sync_lock = False
        self._scroll_job: str | None = None
        self._active_fg_id: str | None = None
        self._active_bg_id: str | None = None
        self._selected_cue_id: str | None = None
        self._selected_para_id: str | None = None
        self._drag_cue_id: str | None = None
        self._drag_moved = False
        self._drag_start_y = 0
        self._para_frames: dict[str, tk.Frame] = {}
        self._text_widgets: dict[str, tk.Text] = {}
        self._cue_widgets: dict[str, tk.Label] = {}
        self._search_hits: list[tuple[str, str | None]] = []
        self._search_index = 0
        self._rebuild_gen = 0
        self._rebuild_in_progress = False
        self._pending_scroll_para: str | None = None
        self._last_rendered_page = 0
        self._mousewheel_active = False
        self._canvas_width = 0
        self._canvas_resize_job: str | None = None
        self._inner_configure_job: str | None = None

        self._build_ui()
        self._show_loading()
        self.after_idle(self.rebuild)

    def _build_ui(self):
        header = tk.Frame(self, bg="#0a0a12")
        header.pack(fill=tk.X, padx=8, pady=(8, 4))

        tk.Label(header, text="SCREENPLAY", font=tkfont.Font(size=12, weight="bold"),
                 fg="#a0d2ff", bg="#0a0a12").pack(side=tk.LEFT)

        legend = tk.Frame(header, bg="#0a0a12")
        legend.pack(side=tk.RIGHT)
        for label, color in (
            ("FX", FX_COLOR), ("BG", BG_COLOR), ("BG STOP", BG_STOP_COLOR), ("MUSIC", MUSIC_COLOR)
        ):
            tk.Label(legend, text=f"■ {label}", fg=color, bg="#0a0a12",
                     font=tkfont.Font(size=9)).pack(side=tk.LEFT, padx=5)

        search_row = tk.Frame(self, bg="#0a0a12")
        search_row.pack(fill=tk.X, padx=8, pady=(0, 6))
        tk.Label(search_row, text="Search:", fg="#a0a0b0", bg="#0a0a12",
                 font=tkfont.Font(size=10)).pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        ent = tk.Entry(search_row, textvariable=self.search_var, width=32, bg="#16213e", fg="white",
                       insertbackground="white", relief=tk.FLAT)
        ent.pack(side=tk.LEFT, padx=6)
        ent.bind("<Return>", lambda e: self._search_next())
        tk.Button(search_row, text="Find", command=self._search_next, bg="#16213e", fg="white",
                  relief=tk.FLAT, padx=8).pack(side=tk.LEFT, padx=2)
        tk.Button(search_row, text="Clear", command=self._search_clear, bg="#16213e", fg="white",
                  relief=tk.FLAT, padx=8).pack(side=tk.LEFT)

        body = tk.Frame(self, bg="#0a0a12")
        body.pack(fill=tk.BOTH, expand=True)
        self._scroll_body = body

        self.canvas = tk.Canvas(body, bg="#12121c", highlightthickness=0)
        self.vscroll = tk.Scrollbar(body, orient=tk.VERTICAL, command=self._on_scroll)
        self.canvas.configure(yscrollcommand=self.vscroll.set)
        self.vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.inner = tk.Frame(self.canvas, bg="#12121c")
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")

        self.inner.bind("<Configure>", self._on_inner_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind("<Button-3>", self._on_canvas_context)

        for widget in (self, header, search_row, body, self.canvas, self.inner):
            widget.bind("<Enter>", self._activate_mousewheel)
            widget.bind("<Leave>", self._deactivate_mousewheel)

    def _activate_mousewheel(self, _event=None):
        if self._mousewheel_active:
            return
        self._mousewheel_active = True
        self.bind_all("<MouseWheel>", self._on_mousewheel, add="+")
        self.bind_all("<Button-4>", self._on_mousewheel, add="+")
        self.bind_all("<Button-5>", self._on_mousewheel, add="+")

    def _deactivate_mousewheel(self, event):
        x, y = self.winfo_pointerx(), self.winfo_pointery()
        widget = self.winfo_containing(x, y)
        while widget is not None:
            if widget == self:
                return
            widget = widget.master
        self._drop_mousewheel()

    def _drop_mousewheel(self):
        if not self._mousewheel_active:
            return
        self._mousewheel_active = False
        self.unbind_all("<MouseWheel>")
        self.unbind_all("<Button-4>")
        self.unbind_all("<Button-5>")

    def _update_scrollregion(self):
        self.inner.update_idletasks()
        width = max(self.inner.winfo_reqwidth(), self.canvas.winfo_width(), 1)
        height = max(self.inner.winfo_reqheight(), 1)
        self.canvas.configure(scrollregion=(0, 0, width, height))

    def _on_canvas_configure(self, event):
        new_width = event.width
        if abs(new_width - self._canvas_width) < 4:
            return
        self._canvas_width = new_width
        if self._canvas_resize_job:
            self.after_cancel(self._canvas_resize_job)
        self._canvas_resize_job = self.after(80, lambda w=new_width: self._apply_canvas_width(w))

    def _apply_canvas_width(self, width: int):
        self._canvas_resize_job = None
        self.canvas.itemconfig(self.canvas_window, width=width)
        self._reflow_text_heights()

    def _reflow_text_heights(self):
        for text in self._text_widgets.values():
            try:
                text.update_idletasks()
                text.configure(height=self._text_display_lines(text))
            except tk.TclError:
                pass
        self._update_scrollregion()

    def _on_inner_configure(self, event=None):
        if self._inner_configure_job:
            self.after_cancel(self._inner_configure_job)
        self._inner_configure_job = self.after(50, self._apply_scrollregion)

    def _apply_scrollregion(self):
        self._inner_configure_job = None
        if self._rebuild_in_progress:
            return
        self._update_scrollregion()

    def _on_scroll(self, *args):
        self.canvas.yview(*args)
        if not self._sync_lock:
            self._schedule_scroll_notify()

    def _should_handle_mousewheel(self, event) -> bool:
        try:
            if self.grab_current() is not None:
                return False
        except tk.TclError:
            pass
        try:
            widget = self.winfo_containing(event.x_root, event.y_root)
        except tk.TclError:
            return False
        while widget is not None:
            if widget == self:
                return True
            widget = widget.master
        return False

    def _on_mousewheel(self, event):
        if not self._should_handle_mousewheel(event):
            return
        if event.num == 5:
            self.canvas.yview_scroll(3, "units")
        elif event.num == 4:
            self.canvas.yview_scroll(-3, "units")
        else:
            delta = event.delta
            if delta == 0:
                return "break"
            steps = max(1, abs(delta) // 120)
            self.canvas.yview_scroll(-steps if delta > 0 else steps, "units")
        if not self._sync_lock:
            self._schedule_scroll_notify()
        return "break"

    def suspend_mousewheel(self):
        """Release global wheel bindings while a modal child dialog is open."""
        self._drop_mousewheel()

    def _schedule_scroll_notify(self):
        if self._scroll_job:
            self.after_cancel(self._scroll_job)
        self._scroll_job = self.after(150, self._scroll_notify)

    def _scroll_notify(self):
        self._scroll_job = None
        if self._sync_lock:
            return
        # Scroll-driven sync disabled by default to avoid fighting navigation;
        # user can click paragraphs/cues to select.

    def set_sync_lock(self, locked: bool):
        self._sync_lock = locked

    def release_sync_lock(self):
        self._sync_lock = False

    def _show_loading(self):
        for child in self.inner.winfo_children():
            child.destroy()
        tk.Label(
            self.inner, text="Loading screenplay…", fg="#8090a8", bg="#12121c",
            font=tkfont.Font(size=12), pady=24, padx=16,
        ).pack(anchor="w")

    def rebuild(self):
        self._rebuild_gen += 1
        gen = self._rebuild_gen
        for child in self.inner.winfo_children():
            child.destroy()
        self._para_frames.clear()
        self._text_widgets.clear()
        self._cue_widgets.clear()
        self._rebuild_index = 0
        self._last_rendered_page = 0
        self._rebuild_in_progress = True
        self._schedule_rebuild_batch(gen)

    def _schedule_rebuild_batch(self, gen: int):
        if gen != self._rebuild_gen:
            return

        batch_size = 40
        paras = self.project.paragraphs
        end = min(self._rebuild_index + batch_size, len(paras))
        for i in range(self._rebuild_index, end):
            self._render_paragraph(paras[i])
        self._rebuild_index = end

        self.inner.update_idletasks()
        self._update_scrollregion()

        if self._rebuild_index < len(paras):
            self.after(1, lambda: self._schedule_rebuild_batch(gen))
            return

        self._rebuild_in_progress = False
        self._apply_cue_highlight()
        if self._pending_scroll_para:
            para_id = self._pending_scroll_para
            self._pending_scroll_para = None
            self.after(50, lambda: self._scroll_to_paragraph(para_id))

    def _render_paragraph(self, para):
        if para.page != self._last_rendered_page:
            self._last_rendered_page = para.page
            pf = tk.Frame(self.inner, bg="#12121c")
            pf.pack(fill=tk.X, padx=12, pady=(14, 4))
            tk.Label(pf, text=f"— Page {para.page} —", fg=PAGE_COLOR, bg="#12121c",
                     font=tkfont.Font(size=10, weight="bold")).pack(anchor="w")

        frame = tk.Frame(self.inner, bg="#12121c", padx=8, pady=2)
        frame.pack(fill=tk.X, padx=8, pady=1)
        frame._paragraph_id = para.id  # type: ignore[attr-defined]
        self._para_frames[para.id] = frame

        frame.bind("<Button-1>", lambda e, pid=para.id: self._select_paragraph(pid))
        frame.bind("<ButtonRelease-1>", lambda e, pid=para.id: self._drop_on_paragraph(pid))
        frame.bind("<Button-3>", lambda e, pid=para.id: self._paragraph_context(e, pid))

        style = self._para_style(para.type)
        text_row = tk.Frame(frame, bg="#12121c")
        text_row.pack(fill=tk.X, **style.get("pack", {}))
        self._build_text_row(text_row, para, style)

        cues = self.project.cues_after(para.id)
        if cues:
            cue_row = tk.Frame(frame, bg="#12121c")
            cue_row._is_cue_row = True  # type: ignore[attr-defined]
            cue_row.pack(fill=tk.X, pady=(4, 0))
            for cue in cues:
                self._add_cue_chip(cue_row, cue, para.id)

        self._apply_para_highlight(para.id)

    def _para_style(self, para_type: str) -> dict:
        if para_type == "scene_heading":
            return {
                "pack": {},
                "fg": SCENE_COLOR,
                "font": tkfont.Font(size=11, weight="bold"),
                "anchor": "w",
                "wraplength": 680,
            }
        if para_type == "character":
            return {
                "pack": {"padx": 80},
                "fg": "#e0e0e0",
                "font": tkfont.Font(size=10, weight="bold"),
                "anchor": "center",
                "wraplength": 500,
            }
        if para_type == "dialogue":
            return {
                "pack": {"padx": 60},
                "fg": "#f0f0f0",
                "font": tkfont.Font(size=10),
                "anchor": "w",
                "wraplength": 520,
            }
        if para_type == "parenthetical":
            return {
                "pack": {"padx": 90},
                "fg": "#b0b0b0",
                "font": tkfont.Font(size=9, slant="italic"),
                "anchor": "center",
                "wraplength": 400,
            }
        if para_type == "transition":
            return {
                "pack": {},
                "fg": "#c0c0c0",
                "font": tkfont.Font(size=10, weight="bold"),
                "anchor": "e",
                "wraplength": 680,
            }
        return {
            "pack": {},
            "fg": "#d8d8d8",
            "font": tkfont.Font(family="Courier", size=10),
            "anchor": "w",
            "wraplength": 680,
        }

    def _inline_cues_at(self, para_id: str, char_pos: int) -> list[dict]:
        by_id = {c["id"]: c for c in self.project.cues}
        result: list[dict] = []
        for pl in self.project._placements_for(para_id, inline=True):
            if pl.anchor_start == char_pos:
                cue = by_id.get(pl.cue_id)
                if cue:
                    result.append(cue)
        return result

    def _build_text_row(self, parent, para, style: dict):
        text = tk.Text(
            parent,
            wrap=tk.WORD,
            height=1,
            font=style["font"],
            fg=style["fg"],
            bg="#12121c",
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=0,
            padx=0,
            pady=0,
            spacing1=0,
            spacing2=0,
            spacing3=0,
            cursor="xterm",
        )
        text.pack(fill=tk.BOTH, expand=True)
        self._text_widgets[para.id] = text
        self._bind_readonly_text(text)
        text.bind(
            "<Button-3>",
            lambda e, pid=para.id, pt=para.text: self._on_text_context(e, pid, pt, text),
        )

        tokens = _tokenize(para.text or " ")
        if tokens:
            for token, start in tokens:
                for cue in self._inline_cues_at(para.id, start):
                    self._insert_inline_cue_tag(text, para.id, cue, start)
                if token.isspace():
                    text.insert(tk.END, token)
                else:
                    tag = f"wd_{para.id}_{start}"
                    text.insert(tk.END, token, tag)
                    text.tag_configure(tag, foreground=style["fg"])
                    text.tag_bind(
                        tag, "<ButtonRelease-1>",
                        lambda e, pid=para.id, pos=start, w=token: self._drop_on_anchor(pid, pos, w),
                    )

        text.update_idletasks()
        text.configure(height=self._text_display_lines(text))

    def _bind_readonly_text(self, text: tk.Text):
        def block_edit(event):
            if event.state & 0x4 and event.keysym.lower() in ("c", "a"):
                return
            if event.keysym in (
                "Left", "Right", "Up", "Down", "Home", "End",
                "Prior", "Next", "Shift_L", "Shift_R",
            ):
                return
            return "break"

        text.bind("<Key>", block_edit)

    def _char_offset_at_click(self, text: tk.Text, event) -> int:
        try:
            idx = text.index(f"@{event.x},{event.y}")
            count = text.count("1.0", idx, "chars")
            if count:
                return int(count[0] if isinstance(count, tuple) else count)
        except tk.TclError:
            pass
        return -1

    def _source_offset_at_click(
        self, text: tk.Text, para_id: str, para_text: str, event,
    ) -> int:
        click_offset = self._char_offset_at_click(text, event)
        if click_offset < 0:
            return -1

        display_pos = 0
        tokens = _tokenize(para_text or " ")
        if not tokens:
            return 0

        for token, start in tokens:
            for cue in self._inline_cues_at(para_id, start):
                label = f" {_marker_label(cue)} "
                label_len = len(label)
                if display_pos <= click_offset < display_pos + label_len:
                    return start
                display_pos += label_len
            token_len = len(token)
            if display_pos <= click_offset < display_pos + token_len:
                if token.isspace():
                    return start
                return start + min(click_offset - display_pos, max(token_len - 1, 0))
            display_pos += token_len
        last_token, last_start = tokens[-1]
        return last_start + max(0, len(last_token) - 1)

    def _on_text_context(self, event, para_id: str, para_text: str, text: tk.Text):
        source_offset = self._source_offset_at_click(text, para_id, para_text, event)
        if source_offset < 0:
            self._show_paragraph_menu(event, para_id)
            return
        found = _word_at_char_offset(para_text, source_offset)
        if found:
            word, start = found
            self._show_word_menu(event, para_id, start, word)
        else:
            self._show_paragraph_menu(event, para_id)
        return "break"

    def _paragraph_context(self, event, para_id: str):
        text = self._text_widgets.get(para_id)
        para = self.project.paragraph(para_id)
        if text and para:
            x = event.x_root - text.winfo_rootx()
            y = event.y_root - text.winfo_rooty()
            if 0 <= x < text.winfo_width() and 0 <= y < text.winfo_height():
                routed = type("Ev", (), {"x": x, "y": y, "x_root": event.x_root, "y_root": event.y_root})()
                self._on_text_context(routed, para_id, para.text, text)
                return
        self._show_paragraph_menu(event, para_id)

    def _text_display_lines(self, text: tk.Text) -> int:
        try:
            count = text.count("1.0", "end-1c", "displaylines")
            if count:
                return max(1, int(count[0] if isinstance(count, tuple) else count))
        except tk.TclError:
            pass
        return max(1, int(text.index("end-1c").split(".")[0]))

    def _insert_inline_cue_tag(self, text: tk.Text, para_id: str, cue: dict, start: int):
        color = _marker_color(cue)
        tag = f"cue_{para_id}_{cue['id']}_{start}"
        label = f" {_marker_label(cue)} "
        text.insert(tk.END, label, tag)
        text.tag_configure(tag, background=color, foreground="white")
        text.tag_bind(tag, "<Button-3>", lambda e, c=cue: self._cue_tag_context(e, c))
        text.tag_bind(
            tag, "<ButtonRelease-1>",
            lambda e, c=cue: self._on_cue_release(c, para_id, e),
        )
        text.tag_bind(tag, "<ButtonPress-1>", lambda e, c=cue: self._start_drag(c["id"], e))
        self._cue_widgets[cue["id"]] = (text, tag, color)

    def _add_cue_chip(self, parent, cue: dict, paragraph_id: str, *, inline: bool = False):
        color = _marker_color(cue)
        active = cue["id"] in (self._active_fg_id, self._active_bg_id, self._selected_cue_id)
        lbl = tk.Label(
            parent,
            text=f"  {_marker_label(cue)}  ",
            fg="white",
            bg=color,
            font=tkfont.Font(size=9, weight="bold"),
            padx=4,
            pady=2,
            cursor="hand2",
            relief=tk.RAISED if active else tk.FLAT,
            borderwidth=2 if active else 1,
        )
        lbl.pack(anchor="w" if not inline else "center", side=tk.LEFT if inline else tk.TOP, pady=2)
        lbl._cue_id = cue["id"]  # type: ignore[attr-defined]
        self._cue_widgets[cue["id"]] = lbl

        lbl.bind("<Double-Button-1>", lambda e, c=cue: self._cue_edit(c))
        lbl.bind("<Button-3>", lambda e, c=cue: self._show_cue_menu(e, c))
        lbl.bind("<ButtonPress-1>", lambda e, c=cue: self._start_drag(c["id"], e))
        lbl.bind("<B1-Motion>", self._drag_motion)
        lbl.bind(
            "<ButtonRelease-1>",
            lambda e, c=cue, pid=paragraph_id: self._on_cue_release(c, pid, e),
        )

    def _on_cue_release(self, cue: dict, paragraph_id: str, event):
        if self._drag_cue_id == cue["id"] and self._drag_moved:
            self._drag_cue_id = None
            self._drag_moved = False
            return "break"
        self._drag_cue_id = None
        self._drag_moved = False
        self._cue_click(cue)
        return "break"

    def _apply_para_highlight(self, para_id: str):
        frame = self._para_frames.get(para_id)
        if not frame:
            return
        bg = PARA_SELECT_BG if para_id == self._selected_para_id else "#12121c"
        frame.configure(bg=bg)
        text = self._text_widgets.get(para_id)
        if text:
            try:
                text.configure(bg=bg)
            except tk.TclError:
                pass
        for child in frame.winfo_children():
            if child is text or getattr(child, "_is_cue_row", False):
                continue
            try:
                child.configure(bg=bg)
            except tk.TclError:
                pass

    def _apply_cue_highlight(self):
        for cue_id, widget in self._cue_widgets.items():
            active = cue_id in (self._active_fg_id, self._active_bg_id, self._selected_cue_id)
            if isinstance(widget, tuple):
                text, tag, color = widget
                try:
                    text.tag_configure(
                        tag,
                        background="#ffffff" if active else color,
                        foreground="#1a1a2e" if active else "white",
                    )
                except tk.TclError:
                    pass
            else:
                widget.configure(relief=tk.RAISED if active else tk.FLAT, borderwidth=2 if active else 1)

    def _select_paragraph(self, para_id: str):
        self._selected_para_id = para_id
        for pid in self._para_frames:
            self._apply_para_highlight(pid)

    def _cue_click(self, cue: dict):
        self._selected_cue_id = cue["id"]
        pl = self.project.placement_for(cue["id"])
        if pl:
            self._selected_para_id = pl.after_paragraph_id
        self._apply_cue_highlight()
        for pid in self._para_frames:
            self._apply_para_highlight(pid)
        if self.on_cue_selected:
            self.on_cue_selected(cue)

    def _cue_edit(self, cue: dict):
        updated = ask_edit_cue(self, self.project, cue)
        if updated:
            self.project.update_cue(cue["id"], updated)
            self._persist()

    def _start_drag(self, cue_id: str, event):
        self._drag_cue_id = cue_id
        self._drag_moved = False
        self._drag_start_y = event.y_root

    def _drag_motion(self, event):
        if self._drag_cue_id and abs(event.y_root - self._drag_start_y) > 8:
            self._drag_moved = True

    def _drop_on_paragraph(self, para_id: str):
        if not self._drag_cue_id or not self._drag_moved:
            self._drag_cue_id = None
            self._drag_moved = False
            return
        self.project.move_cue(self._drag_cue_id, para_id, anchor_start=-1, anchor_text="")
        self._drag_cue_id = None
        self._drag_moved = False
        self._persist()

    def _drop_on_anchor(self, para_id: str, anchor_start: int, anchor_text: str):
        if not self._drag_cue_id or not self._drag_moved:
            return
        self.project.move_cue(
            self._drag_cue_id, para_id,
            anchor_start=anchor_start, anchor_text=anchor_text,
        )
        self._drag_cue_id = None
        self._drag_moved = False
        self._persist()

    def _persist(self):
        self.project.save_all()
        self.rebuild()
        if self.on_cues_changed:
            self.on_cues_changed()

    def _cue_tag_context(self, event, cue: dict):
        self._show_cue_menu(event, cue)
        return "break"

    def _show_cue_menu(self, event, cue: dict):
        menu = tk.Menu(self, tearoff=0, bg="#16213e", fg="white")
        pl = self.project.placement_for(cue["id"])
        para_id = pl.after_paragraph_id if pl else (self.project.paragraphs[0].id if self.project.paragraphs else "")

        menu.add_command(label="Jump To Cue", command=lambda: self._cue_click(cue))
        menu.add_command(label="Edit Cue…", command=lambda: self._cue_edit(cue))
        menu.add_separator()
        menu.add_command(label="Move Cue Up", command=lambda: self._move_cue(cue["id"], -1))
        menu.add_command(label="Move Cue Down", command=lambda: self._move_cue(cue["id"], 1))
        menu.add_command(label="Duplicate Cue", command=lambda: self._duplicate(cue["id"]))
        menu.add_command(label="Delete Cue", command=lambda: self._delete(cue["id"]))
        menu.add_separator()
        menu.add_command(label="Assign Existing Asset…", command=lambda: self._assign_asset(cue))
        menu.add_command(label="Edit Notes…", command=lambda: self._cue_edit(cue))
        menu.add_separator()
        menu.add_command(label="Add Effect Cue Here", command=lambda: self._add_cue(para_id, "FOREGROUND", "SFX"))
        menu.add_command(label="Add Background Cue Here", command=lambda: self._add_cue(para_id, "BACKGROUND", "Ambience"))
        menu.add_command(label="Add Music Cue Here", command=lambda: self._add_cue(para_id, "FOREGROUND", "Music"))
        menu.tk_popup(event.x_root, event.y_root)

    def _show_paragraph_menu(self, event, para_id: str):
        menu = tk.Menu(self, tearoff=0, bg="#16213e", fg="white")
        menu.add_command(label="Add Effect Cue Here", command=lambda: self._add_cue(para_id, "FOREGROUND", "SFX"))
        menu.add_command(label="Add Background Cue Here", command=lambda: self._add_cue(para_id, "BACKGROUND", "Ambience"))
        menu.add_command(label="Add Music Cue Here", command=lambda: self._add_cue(para_id, "FOREGROUND", "Music"))
        menu.tk_popup(event.x_root, event.y_root)

    def _on_canvas_context(self, event):
        pass

    def _move_cue(self, cue_id: str, direction: int):
        self.project.reorder_cue(cue_id, direction)
        self._persist()

    def _duplicate(self, cue_id: str):
        self.project.duplicate_cue(cue_id)
        self._persist()

    def _delete(self, cue_id: str):
        if messagebox.askyesno("Delete Cue", f"Delete {cue_id}?", parent=self):
            self.project.delete_cue(cue_id)
            self._persist()

    def _assign_asset(self, cue: dict):
        self._cue_edit(cue)

    def _show_word_menu(self, event, para_id: str, anchor_start: int, word: str):
        menu = tk.Menu(self, tearoff=0, bg="#16213e", fg="white")
        quoted = f"'{word}'"
        menu.add_command(
            label=f"Add Effect Cue on {quoted}",
            command=lambda: self._add_cue(
                para_id, "FOREGROUND", "SFX", anchor_start=anchor_start, anchor_text=word,
            ),
        )
        menu.add_command(
            label=f"Add Background Cue on {quoted}",
            command=lambda: self._add_cue(
                para_id, "BACKGROUND", "Ambience", anchor_start=anchor_start, anchor_text=word,
            ),
        )
        menu.add_command(
            label=f"Add Music Cue on {quoted}",
            command=lambda: self._add_cue(
                para_id, "FOREGROUND", "Music", anchor_start=anchor_start, anchor_text=word,
            ),
        )
        menu.tk_popup(event.x_root, event.y_root)

    def _add_cue(
        self,
        para_id: str,
        cue_type: str,
        category: str,
        *,
        anchor_start: int = -1,
        anchor_text: str = "",
    ):
        para = self.project.paragraph(para_id)
        trigger = anchor_text or (para.text[:120] if para else "")
        data = ask_new_cue(
            self,
            self.project,
            default_trigger=trigger,
            anchor_text=anchor_text,
            paragraph_id=para_id,
            cue_type=cue_type,
            category=category,
        )
        if not data:
            return
        data.setdefault("cue_type", cue_type)
        data.setdefault("category", category)
        self.project.add_cue(
            para_id, data, anchor_start=anchor_start, anchor_text=anchor_text or data.get("trigger", ""),
        )
        self._persist()

    def _search_next(self):
        query = self.search_var.get().strip().lower()
        if not query:
            return
        if not self._search_hits or self._search_hits[0][0] != query:
            self._search_hits = self._build_search_hits(query)
            self._search_index = 0
        if not self._search_hits:
            messagebox.showinfo("Search", f"No matches for '{query}'", parent=self)
            return
        if self._search_index >= len(self._search_hits):
            self._search_index = 0
        kind, target_id = self._search_hits[self._search_index]
        self._search_index += 1
        if kind == "paragraph":
            self._select_paragraph(target_id)
            self._scroll_to_paragraph(target_id)
        elif kind == "cue":
            cue = next((c for c in self.project.cues if c["id"] == target_id), None)
            if cue:
                self._cue_click(cue)
                pl = self.project.placement_for(target_id)
                if pl:
                    self._scroll_to_paragraph(pl.after_paragraph_id)

    def _search_clear(self):
        self.search_var.set("")
        self._search_hits = []
        self._search_index = 0

    def _build_search_hits(self, query: str) -> list[tuple[str, str]]:
        hits: list[tuple[str, str]] = []
        for p in self.project.paragraphs:
            hay = f"{p.text} {p.scene} {p.speaker or ''} {p.page}".lower()
            if query in hay or query in p.type.lower():
                hits.append(("paragraph", p.id))
        for c in self.project.cues:
            asset = self.project.assets_by_id.get(c.get("asset_id", ""), {})
            hay = " ".join([
                c.get("id", ""), c.get("name", ""), c.get("trigger", ""),
                c.get("scene", ""), str(c.get("page", "")), asset.get("name", ""),
            ]).lower()
            if query in hay:
                hits.append(("cue", c["id"]))
        return hits

    def _scroll_to_paragraph(self, para_id: str):
        if self._rebuild_in_progress:
            self._pending_scroll_para = para_id
            return
        frame = self._para_frames.get(para_id)
        if not frame:
            self._pending_scroll_para = para_id
            return
        self._sync_lock = True
        self.inner.update_idletasks()
        y = frame.winfo_y()
        height = max(frame.winfo_height(), 40)
        total = max(self.inner.winfo_height(), 1)
        view_h = max(self.canvas.winfo_height(), 200)
        target = y + height / 2 - view_h / 2
        scrollable = max(total - view_h, 1)
        fraction = max(0, min(1, target / scrollable))
        self.canvas.yview_moveto(fraction)
        self.after(200, self.release_sync_lock)

    def scroll_to_cue(self, cue: dict, *, fg_id: str | None = None, bg_id: str | None = None):
        self._active_fg_id = fg_id
        self._active_bg_id = bg_id
        self._selected_cue_id = cue["id"]
        pl = self.project.placement_for(cue["id"])
        if pl:
            self._selected_para_id = pl.after_paragraph_id
        self._apply_cue_highlight()
        for pid in self._para_frames:
            self._apply_para_highlight(pid)
        if pl:
            self._scroll_to_paragraph(pl.after_paragraph_id)

    def set_active_cues(self, *, fg_id: str | None = None, bg_id: str | None = None):
        if self._sync_lock:
            return
        self._active_fg_id = fg_id
        self._active_bg_id = bg_id
        self._apply_cue_highlight()

    def close(self):
        self._drop_mousewheel()
