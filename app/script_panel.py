"""Scrollable screenplay PDF panel with cue highlights and page sync."""

from __future__ import annotations

import os
import tkinter as tk
from pathlib import Path
from tkinter import font as tkfont

try:
    import fitz  # PyMuPDF
except ImportError as exc:
    raise ImportError("pymupdf is required. Install: pip install pymupdf") from exc

try:
    from PIL import Image, ImageTk
except ImportError as exc:
    raise ImportError("pillow is required. Install: pip install pillow") from exc

from cue_script_index import build_page_index, cue_type, is_background_stop, search_snippets

ROOT = Path(__file__).resolve().parent.parent

FX_COLOR = "#e94560"
BG_COLOR = "#4a90d9"
BG_STOP_COLOR = "#f5a623"
ACTIVE_OUTLINE = "#ffffff"
MARGIN_BADGE_WIDTH = 118


def resolve_screenplay_pdf(root: Path = ROOT) -> Path | None:
    env = os.environ.get("WHAS_SCREENPLAY_PDF", "").strip()
    candidates = [
        Path(env) if env else None,
        root / "docs" / "Wet Hot American Summer_v2.pdf",
        root / "Wet Hot American Summer_v2.pdf",
        root / "docs" / "AnnotatedScreenplay.pdf",
    ]
    for path in candidates:
        if path and path.is_file():
            return path
    return None


class ScriptPanel(tk.Frame):
    """PDF script viewer with cue overlays and bidirectional page sync."""

    def __init__(
        self,
        parent,
        cues: list[dict],
        *,
        on_page_visible=None,
        on_cue_clicked=None,
        pdf_path: Path | None = None,
    ):
        super().__init__(parent, bg="#0a0a12")
        self.cues = cues
        self.foreground_cues = [c for c in cues if cue_type(c) == "FOREGROUND"]
        self.background_cues = [c for c in cues if cue_type(c) == "BACKGROUND"]
        self.page_index = build_page_index(cues)
        self.on_page_visible = on_page_visible
        self.on_cue_clicked = on_cue_clicked
        self._sync_lock = False
        self._scroll_job: str | None = None
        self._active_fg_id: str | None = None
        self._active_bg_id: str | None = None

        self.pdf_path = pdf_path or resolve_screenplay_pdf()
        self.doc: fitz.Document | None = None
        self.page_count = 0
        self.zoom = 1.15
        self.page_gap = 14
        self.page_tops: list[int] = []
        self.page_heights: list[int] = []
        self._photo_refs: list[ImageTk.PhotoImage] = []
        self._page_items: dict[int, list[int]] = {}

        self._build_ui()
        self._load_pdf()

    def _build_ui(self):
        header = tk.Frame(self, bg="#0a0a12")
        header.pack(fill=tk.X, padx=8, pady=(8, 4))

        tk.Label(
            header, text="SCRIPT", font=tkfont.Font(size=12, weight="bold"),
            fg="#a0d2ff", bg="#0a0a12",
        ).pack(side=tk.LEFT)

        self.lbl_pdf = tk.Label(header, text="", font=tkfont.Font(size=9),
                                fg="#8090a8", bg="#0a0a12")
        self.lbl_pdf.pack(side=tk.LEFT, padx=(12, 0))

        legend = tk.Frame(header, bg="#0a0a12")
        legend.pack(side=tk.RIGHT)
        for label, color in (("FX", FX_COLOR), ("BG", BG_COLOR), ("BG STOP", BG_STOP_COLOR)):
            tk.Label(legend, text=f"■ {label}", fg=color, bg="#0a0a12",
                     font=tkfont.Font(size=9)).pack(side=tk.LEFT, padx=6)

        body = tk.Frame(self, bg="#0a0a12")
        body.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(body, bg="#12121c", highlightthickness=0)
        self.vscroll = tk.Scrollbar(body, orient=tk.VERTICAL, command=self._on_scrollbar)
        self.canvas.configure(yscrollcommand=self.vscroll.set)
        self.vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas.bind("<Configure>", self._on_resize)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", self._on_mousewheel)
        self.canvas.bind("<Button-5>", self._on_mousewheel)

    def _load_pdf(self):
        if not self.pdf_path or not self.pdf_path.is_file():
            self.lbl_pdf.config(text="(no screenplay PDF — run tools/generate_annotated_screenplay.py)")
            self.canvas.create_text(
                40, 40, anchor="nw", fill="#a0a0b0",
                text="Place Wet Hot American Summer_v2.pdf in docs/\n"
                     "or run: python tools/generate_annotated_screenplay.py",
                font=tkfont.Font(size=12),
            )
            return

        self.doc = fitz.open(str(self.pdf_path))
        self.page_count = len(self.doc)
        self.lbl_pdf.config(text=self.pdf_path.name)
        self._layout_pages()
        self._render_visible_pages()
        self.after(100, self._notify_visible_page)

    def set_sync_lock(self, locked: bool) -> None:
        self._sync_lock = locked

    def _on_scrollbar(self, *args):
        self.canvas.yview(*args)
        self._schedule_page_notify()

    def _on_mousewheel(self, event):
        if event.num == 5 or getattr(event, "delta", 0) < 0:
            self.canvas.yview_scroll(3, "units")
        else:
            self.canvas.yview_scroll(-3, "units")
        self._schedule_page_notify()
        return "break"

    def _on_resize(self, _event=None):
        if self.doc:
            self._layout_pages()
            self._render_visible_pages()

    def _schedule_page_notify(self):
        if self._scroll_job:
            self.after_cancel(self._scroll_job)
        self._scroll_job = self.after(120, self._notify_visible_page)

    def _layout_pages(self):
        if not self.doc:
            return
        canvas_width = max(self.canvas.winfo_width(), 400)
        self.page_tops = []
        self.page_heights = []
        y = 0
        for page_num in range(self.page_count):
            page = self.doc[page_num]
            scale = (canvas_width - MARGIN_BADGE_WIDTH - 24) / page.rect.width
            scale = min(scale, self.zoom)
            height = int(page.rect.height * scale)
            self.page_tops.append(y)
            self.page_heights.append(height)
            y += height + self.page_gap
        total_height = max(y, self.canvas.winfo_height())
        self.canvas.configure(scrollregion=(0, 0, canvas_width, total_height))

    def _visible_page_range(self) -> tuple[int, int]:
        if not self.page_tops:
            return 0, 0
        top = self.canvas.canvasy(0)
        bottom = self.canvas.canvasy(self.canvas.winfo_height())
        first = 0
        last = self.page_count - 1
        for i, y in enumerate(self.page_tops):
            if y + self.page_heights[i] >= top:
                first = i
                break
        for i in range(first, self.page_count):
            if self.page_tops[i] > bottom:
                last = max(first, i - 1)
                break
        else:
            last = self.page_count - 1
        return first, min(last + 2, self.page_count)

    def _render_visible_pages(self):
        if not self.doc:
            return
        self.canvas.delete("all")
        self._photo_refs.clear()
        self._page_items.clear()

        canvas_width = max(self.canvas.winfo_width(), 400)
        first, last = self._visible_page_range()

        for page_idx in range(first, last):
            page_num = page_idx + 1
            page = self.doc[page_idx]
            scale = (canvas_width - MARGIN_BADGE_WIDTH - 24) / page.rect.width
            scale = min(scale, self.zoom)
            matrix = fitz.Matrix(scale, scale)
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            photo = ImageTk.PhotoImage(image)
            self._photo_refs.append(photo)

            x0 = MARGIN_BADGE_WIDTH + 8
            y0 = self.page_tops[page_idx]
            img_id = self.canvas.create_image(x0, y0, anchor="nw", image=photo)
            items = [img_id]
            items.extend(self._draw_margin_badges(page_num, page_idx, y0))
            items.extend(self._draw_trigger_highlights(page, page_num, page_idx, x0, y0, scale))
            self._page_items[page_idx] = items

    def _cue_color(self, cue: dict, active: bool) -> str:
        if cue_type(cue) == "BACKGROUND" and is_background_stop(cue):
            base = BG_STOP_COLOR
        elif cue_type(cue) == "BACKGROUND":
            base = BG_COLOR
        else:
            base = FX_COLOR
        return base

    def _is_active(self, cue: dict) -> bool:
        cid = cue["id"]
        return cid == self._active_fg_id or cid == self._active_bg_id

    def _draw_margin_badges(self, page_num: int, page_idx: int, y0: int) -> list[int]:
        items: list[int] = []
        page_cues = self.page_index.get(page_num, [])
        badge_x = 6
        badge_w = MARGIN_BADGE_WIDTH - 10
        y = y0 + 6
        for cue in page_cues:
            active = self._is_active(cue)
            fill = self._cue_color(cue, active)
            label = cue["id"]
            if cue_type(cue) == "BACKGROUND":
                label += " BG" if not is_background_stop(cue) else " STOP"
            else:
                label += " FX"
            h = 18
            rect = self.canvas.create_rectangle(
                badge_x, y, badge_x + badge_w, y + h,
                fill=fill, outline=ACTIVE_OUTLINE if active else fill, width=2 if active else 0,
                tags=("cue_badge", cue["id"], cue_type(cue)),
            )
            text = self.canvas.create_text(
                badge_x + 4, y + h / 2, anchor="w", text=label,
                fill="white", font=tkfont.Font(size=8, weight="bold"),
                tags=("cue_badge", cue["id"], cue_type(cue)),
            )
            for item in (rect, text):
                self.canvas.tag_bind(item, "<Button-1>", lambda e, c=cue: self._cue_click(c))
            items.extend([rect, text])
            y += h + 4
        return items

    def _draw_trigger_highlights(
        self, page: fitz.Page, page_num: int, page_idx: int, x0: int, y0: int, scale: float
    ) -> list[int]:
        items: list[int] = []
        for cue in self.page_index.get(page_num, []):
            active = self._is_active(cue)
            color = self._cue_color(cue, active)
            for snippet in search_snippets(cue.get("trigger", "")):
                try:
                    rects = page.search_for(snippet)
                except Exception:
                    rects = []
                if not rects:
                    continue
                for rect in rects[:2]:
                    rx0 = x0 + rect.x0 * scale
                    ry0 = y0 + rect.y0 * scale
                    rx1 = x0 + rect.x1 * scale
                    ry1 = y0 + rect.y1 * scale
                    stipple = "" if active else "gray50"
                    item = self.canvas.create_rectangle(
                        rx0, ry0, rx1, ry1,
                        outline=color, width=3 if active else 1,
                        stipple=stipple,
                        tags=("cue_highlight", cue["id"]),
                    )
                    items.append(item)
                break
        return items

    def _cue_click(self, cue: dict):
        if self.on_cue_clicked:
            self.on_cue_clicked(cue)

    def _notify_visible_page(self):
        self._scroll_job = None
        if not self.page_tops or self._sync_lock:
            return
        center_y = self.canvas.canvasy(self.canvas.winfo_height() / 2)
        page = 1
        for i, top in enumerate(self.page_tops):
            if center_y < top + self.page_heights[i]:
                page = i + 1
                break
        else:
            page = self.page_count
        if self.on_page_visible:
            self.on_page_visible(page)

    def scroll_to_page(self, page: int, *, fg_id: str | None = None, bg_id: str | None = None):
        if not self.doc or not self.page_tops:
            return
        page = max(1, min(page, self.page_count))
        self._active_fg_id = fg_id
        self._active_bg_id = bg_id
        idx = page - 1
        target = self.page_tops[idx]
        total = self.page_tops[-1] + self.page_heights[-1]
        fraction = target / total if total else 0
        self.canvas.yview_moveto(max(0, fraction - 0.02))
        self._render_visible_pages()
        self._schedule_page_notify()

    def set_active_cues(self, *, fg_id: str | None = None, bg_id: str | None = None):
        self._active_fg_id = fg_id
        self._active_bg_id = bg_id
        self._render_visible_pages()

    def close(self):
        if self.doc:
            self.doc.close()
            self.doc = None
