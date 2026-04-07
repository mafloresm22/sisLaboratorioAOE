import os
import customtkinter as ctk
from PIL import Image
from tksheet import Sheet

_HEADER_BG  = "#4a90d9"
_TABLE_BG   = "#ffffff"
_ALT_ROW_BG = "#f4f8fd"

_COLS: list[tuple[str, int]] = [
    ("N°",         46),
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
_CONS_COL = HEADERS.index("CONSERV.") 

_CONSERV_FG: dict[int, str] = {
    5: "#27ae60",
    4: "#186ccf",
    3: "#d68910",
    2: "#c0392b",
}
_ROW_COLORS = (_TABLE_BG, _ALT_ROW_BG)


# Directorio de iconos de botones
_BUTTON_ICONS_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "..", "assets", "icons", "buttons"
))

# ──────────────────────────────────────────────────────────────
# Componente
# ──────────────────────────────────────────────────────────────
class InstrumentoTabla(ctk.CTkFrame):
    def __init__(self, master, on_view=None, on_edit=None, on_delete=None, **kwargs) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self.on_view   = on_view
        self.on_edit   = on_edit
        self.on_delete = on_delete
        self._items: list    = []

        self._build_sheet()
        self._bind_events()

        self.after(80, self._resize_flex_col)

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

        try:
            self.sheet.set_options(
                table_grid_fg         = _TABLE_BG,
                header_grid_fg        = _HEADER_BG,
                index_grid_fg         = _TABLE_BG,
                header_border_fg      = _HEADER_BG,
                table_selected_cells_border_fg = "#4a90d9",
                align                 = "w", 
                header_align          = "w",
                table_selected_rows_border_fg = "#4a90d9",
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
        self.sheet.MT.bind("<Button-3>", self._show_context_menu)
        self.bind("<Configure>", lambda _: self.after_idle(self._on_resize))

    # ── redimensionado ────────────────────────────────────────
    def _on_resize(self) -> None:
        self._resize_flex_col()

    def _resize_flex_col(self) -> None:
        total = self.sheet.winfo_width()
        if total < 100:
            return
        fixed = sum(w for i, w in enumerate(COL_WIDTHS) if i != _FLEX_COL)
        flex_width = max(150, total - fixed - 16)
        self.sheet.column_width(_FLEX_COL, flex_width)
        self.sheet.redraw()

    # ── población ────────────────────────────────────────────
    def populate(self, items: list) -> None:
        self._items = items
        rows = [self._to_row(i, it) for i, it in enumerate(items)]
        self.sheet.set_sheet_data(rows, reset_col_positions=False)

        for i, item in enumerate(items):
            row_bg = _ROW_COLORS[i % 2]
            self.sheet.highlight_rows(i, bg=row_bg, redraw=False)
            
            fg = _CONSERV_FG.get(getattr(item, "idEstadoCons", 0), "#7f8c8d")
            self.sheet.highlight_cells(row=i, column=_CONS_COL, bg=row_bg, fg=fg, redraw=False)

        self.sheet.redraw()
        self.after_idle(self._resize_flex_col)

    # ── helpers ──────────────────────────────────────────────
    @staticmethod
    def _to_row(index: int, item) -> list:
        return [
            str(item.idInstrumento).zfill(2),
            item.descripcionInstrumento or "Sin descripción",
            f"{item.cantidadInstrumento:g} {getattr(item, 'nombre_unidad', 'und.')}",
            item.marcaInstrumento  or "—",
            item.modeloInstrumento or "—",
            item.serieInstrumento  or "—",
            item.colorInstrumento  or "—",
            item.tamanoInstrumento or "—",
            str(item.idEstadoCons),
            getattr(item, "nombre_laboratorio", "—"),
            item.pisoInstrumento   or "—",
        ]

    # ── Menú Contextual ──────────────────────────────
    def _show_context_menu(self, event) -> None:
        canvas = self.sheet.MT
        r = canvas.identify_row(y=event.y)
        if r is None or r < 0 or r >= len(self._items): return
        
        self.sheet.select_row(r)
        item = self._items[r]
        
        ContextMenu(self, event.x_root, event.y_root, item, 
                          self.on_view, self.on_edit, self.on_delete)


class ContextMenu(ctk.CTkToplevel):
    def __init__(self, master, x, y, item, on_view, on_edit, on_delete):
        super().__init__(master)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(fg_color="white")
        
        self.item = item
        self.on_view = on_view
        self.on_edit = on_edit
        self.on_delete = on_delete
        
        # Cargar Iconos
        self._load_icons()
        
        # Main Frame with Shadow Effect (Simulated)
        self.main_container = ctk.CTkFrame(self, fg_color="white", corner_radius=12, border_width=1, border_color="#e0e0e0")
        self.main_container.pack(padx=2, pady=2)
        
        # Header Info
        header = ctk.CTkFrame(self.main_container, fg_color="#f8f9fa", height=40, corner_radius=0)
        header.pack(fill="x", side="top")
        ctk.CTkLabel(header, text="Opciones de Registro", font=("Arial", 11, "bold"), text_color="#7f8c8d").pack(padx=15, pady=8)
        ctk.CTkFrame(self.main_container, fg_color="#eeeeee", height=1).pack(fill="x")

        # Buttons
        self._add_option("Ver Detalles", self.img_view, lambda: self._exec(self.on_view))
        self._add_option("Editar Registro", self.img_edit, lambda: self._exec(self.on_edit))
        ctk.CTkFrame(self.main_container, fg_color="#f1f1f1", height=1).pack(fill="x", padx=10)
        self._add_option("Eliminar Registro", self.img_delete, lambda: self._exec(self.on_delete))

        # Placement
        self.update_idletasks()
        self.geometry(f"+{x}+{y}")
        
        # Close logic
        self.bind("<FocusOut>", lambda e: self.destroy())
        self.after(100, lambda: self.focus_set())

    def _load_icons(self):
        def _get(name):
            p = os.path.join(_BUTTON_ICONS_DIR, name)
            return ctk.CTkImage(Image.open(p), size=(18, 18)) if os.path.exists(p) else None
        
        self.img_view = _get("show_8358982.png")
        self.img_edit = _get("edit_3808637.png")
        self.img_delete = _get("delete_2550318.png")

    def _add_option(self, text, icon, command):
        btn = ctk.CTkButton(
            self.main_container, text=f"  {text}", image=icon, font=("Arial", 13),
            fg_color="transparent", text_color="#2c3e50", anchor="w",
            height=38, width=200, corner_radius=0,
            hover_color="#f1f2f6",
            command=command
        )
        btn.pack(fill="x", padx=2, pady=1)

    def _exec(self, callback):
        self.destroy()
        if callback: callback(self.item)
