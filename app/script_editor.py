"""Editable screenplay view replacing the PDF panel."""

from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont, messagebox

from cue_dialogs import ask_edit_cue, ask_new_cue
from script_model import ScriptProject, _marker_kind

FX_COLOR = "#e94560"
BG_COLOR = "#4a90d9"
BG_STOP_COLOR = "#f5a623"
PARA_SELECT_BG = "#1e3a5f"
PAGE_COLOR = "#8090a8"
SCENE_COLOR = "#a0d2ff"


def _marker_color(cue: dict) -> str:
    kind = _marker_kind(cue)
    if kind == "BG":
        return BG_COLOR
    if kind == "BG_STOP":
        return BG_STOP_COLOR
    return FX_COLOR


def _marker_label(cue: dict) -> str:
    num = cue["id"].split("-")[-1]
    kind = _marker_kind(cue)
    if kind == "BG_STOP":
        return f"[BG STOP-{num}] {cue['name']}"
    if kind == "BG":
        return f"[BG-{num}] {cue['name']}"
    return f"[FX-{num}] {cue['name']}"


class ScriptEditor(tk.Frame):
    """Scrollable screenplay editor with line-level cue markers."""

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
        self._para_styles = self._build_para_styles()

        self._build_ui()
        self._show_loading()
        self.after_idle(self.rebuild)

    def _build_para_styles(self) -> dict[str, dict]:
        return {
            "scene_heading": {
                "pack": {},
                "fg": SCENE_COLOR,
                "font": tkfont.Font(size=11, weight="bold"),
                "anchor": "w",
                "wraplength": 680,
            },
            "character": {
                "pack": {"padx": 80},
                "fg": "#e0e0e0",
                "font": tkfont.Font(size=10, weight="bold"),
                "anchor": "center",
                "wraplength": 500,
            },
            "dialogue": {
                "pack": {"padx": 60},
                "fg": "#f0f0f0",
                "font": tkfont.Font(size=10),
                "anchor": "w",
                "wraplength": 520,
            },
            "parenthetical": {
                "pack": {"padx": 90},
                "fg": "#b0b0b0",
                "font": tkfont.Font(size=9, slant="italic"),
                "anchor": "center",
                "wraplength": 400,
            },
            "transition": {
                "pack": {},
                "fg": "#c0c0c0",
                "font": tkfont.Font(size=10, weight="bold"),
                "anchor": "e",
                "wraplength": 680,
            },
            "action": {
                "pack": {},
                "fg": "#d8d8d8",
                "font": tkfont.Font(family="Courier", size=10),
                "anchor": "w",
                "wraplength": 680,
            },
        }

    def _build_ui(self):
        header = tk.Frame(self, bg="#0a0a12")
        header.pack(fill=tk.X, padx=8, pady=(8, 4))

        tk.Label(header, text="SCREENPLAY", font=tkfont.Font(size=12, weight="bold"),
                 fg="#a0d2ff", bg="#0a0a12").pack(side=tk.LEFT)

        legend = tk.Frame(header, bg="#0a0a12")
        legend.pack(side=tk.RIGHT)
        for label, color in (
            ("FX", FX_COLOR), ("BG", BG_COLOR), ("BG STOP", BG_STOP_COLOR)
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

        self.canvas = tk.Canvas(body, bg="#12121c", highlightthickness=0)
        self.vscroll = tk.Scrollbar(body, orient=tk.VERTICAL, command=self._on_scroll)
        self.canvas.configure(yscrollcommand=self.vscroll.set)
        self.vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.inner = tk.Frame(self.canvas, bg="#12121c")
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")

        self.inner.bind("<Configure>", self._on_inner_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

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
        self._update_wraplengths(width)
        self._update_scrollregion()

    def _update_wraplengths(self, canvas_width: int):
        wrap = max(280, canvas_width - 48)
        dialogue = max(240, canvas_width - 140)
        self._para_styles["scene_heading"]["wraplength"] = wrap
        self._para_styles["transition"]["wraplength"] = wrap
        self._para_styles["action"]["wraplength"] = wrap
        self._para_styles["dialogue"]["wraplength"] = dialogue
        for frame in self._para_frames.values():
            for child in frame.winfo_children():
                if isinstance(child, tk.Frame):
                    for lbl in child.winfo_children():
                        if isinstance(lbl, tk.Label) and not hasattr(lbl, "_cue_id"):
                            try:
                                lbl.configure(wraplength=wrap)
                            except tk.TclError:
                                pass

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
        self._drop_mousewheel()

    def _schedule_scroll_notify(self):
        if self._scroll_job:
            self.after_cancel(self._scroll_job)
        self._scroll_job = self.after(150, self._scroll_notify)

    def _scroll_notify(self):
        self._scroll_job = None

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
        self._cue_widgets.clear()
        self._rebuild_index = 0
        self._last_rendered_page = 0
        self._rebuild_in_progress = True
        self._schedule_rebuild_batch(gen)

    def _schedule_rebuild_batch(self, gen: int):
        if gen != self._rebuild_gen:
            return

        batch_size = 120
        paras = self.project.paragraphs
        end = min(self._rebuild_index + batch_size, len(paras))
        for i in range(self._rebuild_index, end):
            self._render_paragraph(paras[i])
        self._rebuild_index = end

        if self._rebuild_index < len(paras):
            self.after(1, lambda: self._schedule_rebuild_batch(gen))
            return

        self._rebuild_in_progress = False
        self._update_scrollregion()
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
        frame.bind("<Button-3>", lambda e, pid=para.id: self._show_paragraph_menu(e, pid))

        style = self._para_styles.get(para.type, self._para_styles["action"])
        text_row = tk.Frame(frame, bg="#12121c")
        text_row.pack(fill=tk.X, **style.get("pack", {}))

        lbl = tk.Label(
            text_row,
            text=para.text or " ",
            fg=style["fg"],
            bg="#12121c",
            font=style["font"],
            wraplength=style.get("wraplength", 680),
            justify="left",
            anchor=style.get("anchor", "w"),
        )
        lbl.pack(fill=tk.X)
        lbl.bind("<Button-3>", lambda e, pid=para.id: self._show_paragraph_menu(e, pid))

        cues = self.project.cues_for_paragraph(para.id)
        if cues:
            cue_row = tk.Frame(frame, bg="#12121c")
            cue_row._is_cue_row = True  # type: ignore[attr-defined]
            cue_row.pack(fill=tk.X, pady=(4, 0))
            for cue in cues:
                self._add_cue_chip(cue_row, cue, para.id)

        self._apply_para_highlight(para.id)

    def _add_cue_chip(self, parent, cue: dict, paragraph_id: str):
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
        lbl.pack(side=tk.LEFT, padx=(0, 6), pady=2)
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
        for child in frame.winfo_children():
            if getattr(child, "_is_cue_row", False):
                child.configure(bg=bg)
                for chip in child.winfo_children():
                    chip.configure(bg=chip.cget("bg"))
                continue
            child.configure(bg=bg)
            for lbl in child.winfo_children():
                if not hasattr(lbl, "_cue_id"):
                    lbl.configure(bg=bg)

    def _apply_cue_highlight(self):
        for cue_id, widget in self._cue_widgets.items():
            active = cue_id in (self._active_fg_id, self._active_bg_id, self._selected_cue_id)
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
        dragged = self._drag_cue_id
        self.project.move_cue(dragged, para_id)
        self._drag_cue_id = None
        self._drag_moved = False
        self._persist()

    def _persist(self):
        self.project.save_all()
        self.rebuild()
        if self.on_cues_changed:
            self.on_cues_changed()

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
        menu.add_command(label="Add Effect Cue on Line", command=lambda: self._add_cue(para_id, "FOREGROUND", "SFX"))
        menu.add_command(label="Add Background Cue on Line", command=lambda: self._add_cue(para_id, "BACKGROUND", "Ambience"))
        menu.tk_popup(event.x_root, event.y_root)

    def _show_paragraph_menu(self, event, para_id: str):
        menu = tk.Menu(self, tearoff=0, bg="#16213e", fg="white")
        menu.add_command(label="Add Effect Cue on Line", command=lambda: self._add_cue(para_id, "FOREGROUND", "SFX"))
        menu.add_command(label="Add Background Cue on Line", command=lambda: self._add_cue(para_id, "BACKGROUND", "Ambience"))
        menu.tk_popup(event.x_root, event.y_root)

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

    def _add_cue(self, para_id: str, cue_type: str, category: str):
        para = self.project.paragraph(para_id)
        trigger = para.text[:120] if para else ""
        data = ask_new_cue(
            self,
            self.project,
            default_trigger=trigger,
            paragraph_id=para_id,
            cue_type=cue_type,
            category=category,
        )
        if not data:
            return
        data.setdefault("cue_type", cue_type)
        data.setdefault("category", category)
        self.project.add_cue(para_id, data)
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
