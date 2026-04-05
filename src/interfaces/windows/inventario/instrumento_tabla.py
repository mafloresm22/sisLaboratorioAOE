import os
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
from tksheet import Sheet

_IMG_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../../../../assets/icons/dashboard/default_instrumento.png",
    )
)
_IMG_SIZE = 38  
_HEADER_BG  = "#4a90d9"
_TABLE_BG   = "#ffffff"
_ALT_ROW_BG = "#f4f8fd"

_COLS: list[tuple[str, int]] = [
    ("N°",         46),
    ("FOTO",        58),
    ("DESCRIPCIÓN",320), 
    ("CANT.",       76),
    ("MARCA",      110),
    ("MODELO",     110),
    ("SERIE",      100),
    ("COLOR",      110),
    ("TAMAÑO",      90),
    ("CONSERV.",    75),
    ("UBICACIÓN",  135),
    ("PISO",        72),
]
HEADERS    = [c[0] for c in _COLS]
COL_WIDTHS = [c[1] for c in _COLS]

# Índices clave
_FLEX_COL = HEADERS.index("DESCRIPCIÓN")
_FOTO_COL = HEADERS.index("FOTO")       
_CONS_COL = HEADERS.index("CONSERV.") 

_CONSERV_FG: dict[int, str] = {
    5: "#27ae60",
    4: "#186ccf",
    3: "#d68910",
    2: "#c0392b",
}
_ROW_COLORS = (_TABLE_BG, _ALT_ROW_BG)


# ──────────────────────────────────────────────────────────────
# Componente
# ──────────────────────────────────────────────────────────────
class InstrumentoTabla(ctk.CTkFrame):
    def __init__(self, master, on_edit=None, on_delete=None, **kwargs) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self.on_edit   = on_edit
        self.on_delete = on_delete
        self._items: list    = []
        self._img_ids: list  = []
        self._row_images: list = [] 
        self._default_photo: ImageTk.PhotoImage | None = None

        self._load_default_image()
        self._build_sheet()
        self._bind_events()

        self.after(80, self._resize_flex_col)

    # ── imagen ───────────────────────────────────────────────
    def _load_default_image(self) -> None:
        self._default_photo = self._process_image_path(_IMG_PATH)

    def _process_image_path(self, path: str) -> ImageTk.PhotoImage | None:
        try:
            if not path or not os.path.exists(path):
                return None
            pil = Image.open(path).convert("RGBA").resize(
                (_IMG_SIZE, _IMG_SIZE), Image.LANCZOS
            )
            bg = Image.new("RGBA", pil.size, (255, 255, 255, 255))
            bg.paste(pil, mask=pil.split()[3])
            return ImageTk.PhotoImage(bg.convert("RGB"))
        except Exception as e:
            print(f"[InstrumentoTabla] Error procesando imagen {path}: {e}")
            return None

    # ── construcción ─────────────────────────────────────────
    def _build_sheet(self) -> None:
        self.sheet = Sheet(
            self,
            headers=HEADERS,
            data=[],
            header_bg          = _HEADER_BG,
            header_fg          = "white",
            top_left_bg        = _HEADER_BG,
            top_left_fg        = _HEADER_BG,
            table_bg           = _TABLE_BG,
            table_fg           = "#2c3e50",
            show_row_index     = False,
            header_font        = ("Arial", 11, "bold"),
            font               = ("Arial", 11, "normal"),
            row_height         = 54,
            header_height      = 44,
            show_x_scrollbar   = True,
            show_y_scrollbar   = True,
            outline_thickness  = 0,
        )
        self.sheet.pack(fill="both", expand=True)
        self.sheet.set_column_widths(COL_WIDTHS)

        # Configuración de alineación y bordes
        try:
            self.sheet.set_options(
                table_grid_fg         = _TABLE_BG,
                header_grid_fg        = _HEADER_BG,
                index_grid_fg         = _TABLE_BG,
                header_border_fg      = _HEADER_BG,
                table_selected_cells_border_fg = "#4a90d9",
                align                 = "w", 
                header_align          = "w",
            )
        except Exception:
            pass

        self.sheet.enable_bindings(
            "single_select",
            "row_select",
            "column_width_resize",
            "arrowkeys",
        )

    def _bind_events(self) -> None:
        self.sheet.bind("<Button-3>", self._show_context_menu)
        self.bind("<Configure>", lambda _: self.after_idle(self._on_resize))
        # Redibujar imágenes cuando el canvas se desplaza
        try:
            self.sheet.MT.bind("<B1-Motion>", lambda _: self.after_idle(self._place_images), add="+")
        except Exception:
            pass

    # ── redimensionado ────────────────────────────────────────
    def _on_resize(self) -> None:
        self._resize_flex_col()
        # Redibujar imágenes inmediatamente tras el resize
        self.after(5, self._place_images)

    def _resize_flex_col(self) -> None:
        total = self.sheet.winfo_width()
        if total < 100:
            return
        fixed = sum(w for i, w in enumerate(COL_WIDTHS) if i != _FLEX_COL)
        flex_width = max(150, total - fixed - 16)
        self.sheet.column_width(_FLEX_COL, flex_width)
        self.sheet.redraw()

    # ── imágenes en canvas ────────────────────────────────────
    def _place_images(self) -> None:
        """
        Dibuja las imágenes de self._row_images en el canvas interno.
        """
        if not self._items or not self._row_images:
            return

        try:
            canvas = self.sheet.MT
        except AttributeError:
            return

        # Limpiar previos
        for img_id in self._img_ids:
            try: canvas.delete(img_id)
            except: pass
        self._img_ids.clear()

        # Obtener posiciones del canvas interno
        col_positions = getattr(canvas, 'col_positions', [])
        row_positions = getattr(canvas, 'row_positions', [])

        # Si no hay posiciones calculadas todavía, forzar un redraw interno
        if not col_positions or not row_positions:
            self.sheet.redraw()
            col_positions = getattr(canvas, 'col_positions', [])
            row_positions = getattr(canvas, 'row_positions', [])

        if _FOTO_COL + 1 >= len(col_positions):
            return

        cx = (col_positions[_FOTO_COL] + col_positions[_FOTO_COL + 1]) // 2

        # Dibujar cada imagen de la cache de filas
        for i, photo in enumerate(self._row_images):
            if i + 1 >= len(row_positions) or photo is None:
                continue
            cy = (row_positions[i] + row_positions[i + 1]) // 2
            img_id = canvas.create_image(cx, cy, image=photo, anchor="center")
            self._img_ids.append(img_id)

    # ── población ────────────────────────────────────────────
    def populate(self, items: list) -> None:
        self._items = items
        self._row_images = []

        # Preparar cache de imagenes para estas 30 filas
        for item in items:
            img_path = getattr(item, "imagenInstrumento", None)
            photo = None
            if img_path:
                photo = self._process_image_path(img_path)
            
            # Fallback a default si falla o no hay
            self._row_images.append(photo or self._default_photo)

        rows = [self._to_row(i, it) for i, it in enumerate(items)]
        self.sheet.set_sheet_data(rows, reset_col_positions=False)

        # Colores por fila + badge conservación
        for i, item in enumerate(items):
            row_bg = _ROW_COLORS[i % 2]
            self.sheet.highlight_rows(i, bg=row_bg, redraw=False)
            fg = _CONSERV_FG.get(getattr(item, "idEstadoCons", 0), "#7f8c8d")
            self.sheet.highlight_cells(
                row=i, column=_CONS_COL,
                bg=row_bg, fg=fg,
                redraw=False,
            )

        self.sheet.redraw()
        self.after_idle(self._resize_flex_col)
        self.after(5, self._place_images)

    # ── helpers ──────────────────────────────────────────────
    @staticmethod
    def _to_row(index: int, item) -> list:
        return [
            str(index + 1).zfill(2),                           # 0: N°
            "",                                                # 1: FOTO
            item.descripcionInstrumento or "Sin descripción",  # 2: DESCRIPCIÓN
            f"{item.cantidadInstrumento} und.",
            item.marcaInstrumento  or "—",
            item.modeloInstrumento or "—",
            item.serieInstrumento  or "—",
            item.colorInstrumento  or "—",
            item.tamanoInstrumento or "—",
            str(item.idEstadoCons),
            getattr(item, "nombre_laboratorio", "—"),
            item.pisoInstrumento   or "—",
        ]

    def _selected_item(self):
        rows = self.sheet.get_selected_rows()
        if rows:
            idx = list(rows)[0]
            if 0 <= idx < len(self._items):
                return self._items[idx]
        return None

    # ── menú contextual ──────────────────────────────────────
    def _show_context_menu(self, event: tk.Event) -> None:
        canvas = self.sheet.MT
        # Identificar qué fila se clickeó
        r = canvas.identify_row(y=event.y)
        if r is None or r < 0 or r >= len(self._items):
            return
        
        # Seleccionar la fila visualmente antes de abrir el menú
        self.sheet.select_row(r)
        item = self._items[r]

        menu = tk.Menu(self, tearoff=0, font=("Arial", 12))
        menu.add_command(
            label="  ✏️   Editar",
            command=lambda: self.on_edit(item) if self.on_edit else None,
        )
        menu.add_separator()
        menu.add_command(
            label="  🗑️   Eliminar",
            command=lambda: self.on_delete(item) if self.on_delete else None,
        )
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
