import customtkinter as ctk
from PIL import Image
import os
from utils.excel_importer import ExcelImporter
from services.instrumentos.instrumentos import InstrumentoService
from interfaces.windows.inventario.instrumento_tabla import InstrumentoTabla
from interfaces.windows.inventario.show_estadoConservacion import LegendConservacionModal
from interfaces.windows.inventario.create_instrumentos import CreateInstrumentoModal
from interfaces.windows.inventario.show_instrumentos import ShowInstrumentoModal

# Directorio de iconos de botones
_BUTTON_ICONS_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "..", "assets", "icons", "buttons"
))


class InstrumentosFrame(ctk.CTkFrame):
    def __init__(self, master, usuario=None, **kwargs):
        super().__init__(master, **kwargs)
        self.usuario = usuario
        self.configure(fg_color="white", corner_radius=15)

        # Paginación
        self.current_page   = 1
        self.items_per_page = 30
        self.all_data       = []
        self.filtered_data  = []

        # Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_table()
        self._build_pagination()
        self.load_data()

    # ──────────────────────────────────────────────────────────
    # UI
    # ──────────────────────────────────────────────────────────
    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=25, pady=(25, 15))

        ctk.CTkLabel(
            header, text="Gestión de Inventario",
            font=("Arial", 28, "bold"), text_color="#2c3e50",
        ).pack(side="left")

        actions = ctk.CTkFrame(header, fg_color="transparent")
        actions.pack(side="right")

        self.search_entry = ctk.CTkEntry(
            actions, placeholder_text="🔍 Buscar instrumento...",
            width=300, height=40, font=("Arial", 13),
            border_color="#d1d8e0", corner_radius=10,
        )
        self.search_entry.pack(side="left", padx=(0, 15))
        self.search_entry.bind("<KeyRelease>", self.filter_data)

        def _btn(text, color, hover, cmd, icon_name, w=150):
            img_path = os.path.join(_BUTTON_ICONS_DIR, icon_name)
            img = ctk.CTkImage(Image.open(img_path), size=(20, 20))
            return ctk.CTkButton(
                actions, text=text, image=img, width=w, height=45, corner_radius=10,
                fg_color=color, hover_color=hover, text_color="white",
                font=("Arial", 13, "bold"), command=cmd,
            )

        _btn(" Ver Leyenda",       "#3498db", "#2980b9", self.on_show_legend,    "show_8358982.png"  ).pack(side="left", padx=(0, 10))
        _btn(" Importar Excel",    "#8e44ad", "#732d91", self.on_import_excel,   "other_12283713.png", w=160).pack(side="left", padx=(0, 10))
        _btn(" Agregar Instrumento", "#27ae60", "#219150", self.on_add_instrumento,"add_6902311.png",  w=190).pack(side="left")

    def _build_table(self) -> None:
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=1, column=0, sticky="nsew", padx=25, pady=(0, 10))

        # InstrumentoTabla (tksheet) maneja header + filas + scroll internamente
        self.tabla = InstrumentoTabla(
            container,
            on_view  =self.handle_view,
            on_edit  =self.handle_edit,
            on_delete=self.handle_delete,
        )
        self.tabla.pack(fill="both", expand=True)

    def _build_pagination(self) -> None:
        pag = ctk.CTkFrame(self, fg_color="transparent")
        pag.grid(row=2, column=0, sticky="ew", padx=25, pady=(0, 20))

        def _pbtn(text, cmd):
            return ctk.CTkButton(
                pag, text=text, width=110, height=35, corner_radius=8,
                font=("Arial", 12, "bold"),
                fg_color="#34495e", hover_color="#2c3e50", command=cmd,
            )

        self.btn_prev = _pbtn("◀ Anterior", self.prev_page)
        self.btn_prev.pack(side="left", padx=5)

        self.lbl_pageinfo = ctk.CTkLabel(
            pag, text="Página 1 de 1",
            font=("Arial", 12, "bold"), text_color="#7f8c8d",
        )
        self.lbl_pageinfo.pack(side="left", padx=15)

        self.btn_next = _pbtn("Siguiente ▶", self.next_page)
        self.btn_next.pack(side="left", padx=5)

        self.lbl_total_records = ctk.CTkLabel(
            pag, text="Total: 0 instrumentos registrados",
            font=("Arial", 12, "bold"), text_color="#95a5a6",
        )
        self.lbl_total_records.pack(side="right", padx=10)

    # ──────────────────────────────────────────────────────────
    # DATOS
    # ──────────────────────────────────────────────────────────
    def load_data(self) -> None:
        if not self.all_data:
            self.all_data      = InstrumentoService.get_all_instrumentos()
            self.filtered_data = list(self.all_data)

        total_items = len(self.filtered_data)
        total_pages = max(1, (total_items + self.items_per_page - 1) // self.items_per_page)
        self.current_page = max(1, min(self.current_page, total_pages))

        start = (self.current_page - 1) * self.items_per_page
        datos = self.filtered_data[start : start + self.items_per_page]

        # Estado vacío
        if not self.filtered_data:
            self.tabla.populate([])
            self.lbl_pageinfo.configure(text="Página 0 de 0")
            self.lbl_total_records.configure(text="Total: 0 instrumentos registrados")
            self.btn_prev.configure(state="disabled", fg_color="#95a5a6")
            self.btn_next.configure(state="disabled", fg_color="#95a5a6")
            return

        # Actualizar controles
        self.lbl_pageinfo.configure(text=f"Página {self.current_page} de {total_pages}")
        self.lbl_total_records.configure(text=f"Total: {total_items} instrumentos registrados")
        self.btn_prev.configure(
            state="normal" if self.current_page > 1 else "disabled",
            fg_color="#34495e" if self.current_page > 1 else "#95a5a6",
        )
        self.btn_next.configure(
            state="normal" if self.current_page < total_pages else "disabled",
            fg_color="#34495e" if self.current_page < total_pages else "#95a5a6",
        )

        # Renderizar tabla (instantáneo gracias a tksheet)
        self.tabla.populate(datos)

    # ──────────────────────────────────────────────────────────
    # ACCIONES
    # ──────────────────────────────────────────────────────────
    def handle_view(self, item) -> None:
        ShowInstrumentoModal(self.winfo_toplevel(), item)
    def handle_edit(self, item) -> None:
        from interfaces.components.mensajes import Alerts
        Alerts.show_info("Editar Instrumento", f"Funcionalidad de edición para: {item.descripcionInstrumento}\n(En desarrollo)", master=self.master)

    def handle_delete(self, item) -> None:
        from interfaces.components.mensajes import Alerts
        confirm = Alerts.show_question(
            "Confirmar Eliminación",
            f"¿Está seguro de eliminar el instrumento?\n'{item.descripcionInstrumento}'",
            master=self.master
        )
        if confirm:
            if InstrumentoService.delete_instrumento(item.idInstrumento):
                Alerts.show_success("Eliminado", "El instrumento ha sido eliminado correctamente.", master=self.master)
                self.all_data = []
                self.load_data()
            else:
                Alerts.show_error("Error", "No se pudo eliminar el instrumento.", master=self.master)

    def filter_data(self, _=None) -> None:
        query = self.search_entry.get().lower().strip()
        if not query:
            self.filtered_data = list(self.all_data)
        else:
            self.filtered_data = [
                it for it in self.all_data
                if query in (it.descripcionInstrumento or "").lower()
                or query in (it.marcaInstrumento       or "").lower()
                or query in (it.modeloInstrumento      or "").lower()
                or query in (it.serieInstrumento       or "").lower()
            ]
        self.current_page = 1
        self.load_data()

    def on_show_legend(self) -> None:
        LegendConservacionModal(self.winfo_toplevel())

    def on_add_instrumento(self) -> None:
        CreateInstrumentoModal(self.winfo_toplevel(), parent_view=self, usuario=self.usuario)

    def on_import_excel(self) -> None:
        from interfaces.components.mensajes import Alerts
        success, message = ExcelImporter.importar_instrumentos()
        if success:
            Alerts.show_info("Importación Exitosa", message, master=self.master)
            self.all_data = []
            self.current_page = 1
            self.load_data()
        else:
            if "cancelada" not in message.lower():
                Alerts.show_error("Error de Importación", message, master=self.master)

    def prev_page(self) -> None:
        if self.current_page > 1:
            self.current_page -= 1
            self.load_data()

    def next_page(self) -> None:
        total_pages = max(
            1, (len(self.filtered_data) + self.items_per_page - 1) // self.items_per_page
        )
        if self.current_page < total_pages:
            self.current_page += 1
            self.load_data()


if __name__ == "__main__":
    app = ctk.CTk()
    app.geometry("1400x800")
    InstrumentosFrame(app).pack(fill="both", expand=True, padx=20, pady=20)
    app.mainloop()
