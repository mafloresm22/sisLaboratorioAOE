import customtkinter as ctk
from PIL import Image
import os
from tksheet import Sheet
from services.instrumentos.instrumentos import InstrumentoService
from services.prestamos.prestamos import PrestamoService
from interfaces.windows.prestamos.create_prestamo import CreatePrestamoModal
from utils.paths import get_resource_path, get_storage_path

# Configuración Estética
_BLUE_HEADER = "#186ccf"
_ORANGE_HEADER = "#e67e22"
_ALT_ROW_BG = "#f8f9fa"
_SELECTED_COLOR = "#e3f2fd"

# Definición de anchos fijos para evitar encogimiento
_CAT_COLS = [45, 300, 90, 130] 
_LOAN_COLS = [40, 180, 150, 70, 115]

class PrestamosFrame(ctk.CTkFrame):
    def __init__(self, master, usuario=None, **kwargs):
        super().__init__(master, **kwargs)
        self.usuario = usuario
        self.configure(fg_color="white", corner_radius=15)

        self.all_instruments = []
        self.filtered_instruments = []
        self.selected_instrument = None

        # Layout Principal
        self.grid_columnconfigure(0, weight=1) 
        self.grid_columnconfigure(1, weight=1) 
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0) 

        self._build_header()
        self._build_tables()
        self._build_selection_details()
        
        self.bind("<Configure>", lambda e: self.after(50, self._resize_tables))
        self.load_data()

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=25, pady=(25, 10))

        ctk.CTkLabel(
            header, text="Gestión de Préstamos",
            font=("Arial", 32, "bold"), text_color="#2c3e50",
        ).pack(side="left")

        actions = ctk.CTkFrame(header, fg_color="transparent")
        actions.pack(side="right")

        icon_refresh = ctk.CTkImage(Image.open(get_resource_path(os.path.join("assets", "icons", "buttons", "other_12283713.png"))), size=(20, 20))
        self.btn_refresh = ctk.CTkButton(
            actions, text=" Actualizar Datos", image=icon_refresh, width=170, height=42, corner_radius=10,
            fg_color="#34495e", hover_color="#2c3e50", font=("Arial", 13, "bold"),
            command=self.load_data
        )
        self.btn_refresh.pack(side="right", padx=5)

    def _build_tables(self):
        # --- PANEL IZQUIERDO: CATÁLOGO ---
        left_panel = ctk.CTkFrame(self, fg_color="transparent")
        left_panel.grid(row=1, column=0, sticky="nsew", padx=(25, 15), pady=(0, 10))
        
        top_left = ctk.CTkFrame(left_panel, fg_color="transparent")
        top_left.pack(fill="x", pady=(0, 10))
        
        icon_cat = ctk.CTkImage(Image.open(get_resource_path(os.path.join("assets", "icons", "unidad_img", "package_1274687.png"))), size=(24, 24))
        ctk.CTkLabel(top_left, text=" Catálogo de Instrumentos", image=icon_cat, compound="left", font=("Arial", 18, "bold"), text_color=_BLUE_HEADER).pack(side="left")
        
        self.search_catalog = ctk.CTkEntry(
            top_left, placeholder_text="Buscar instrumento...",
            width=250, height=38, corner_radius=10, border_color="#dcdde1", font=("Arial", 13)
        )
        self.search_catalog.pack(side="right")
        self.search_catalog.bind("<KeyRelease>", self._filter_catalog)

        # Tabla Catálogo
        headers_cat = ["N°", "DESCRIPCIÓN DEL INSTRUMENTO", "STOCK", "UBICACIÓN"]
        self.sheet_catalog = self._create_styled_sheet(left_panel, headers_cat, _BLUE_HEADER)
        self.sheet_catalog.set_column_widths(_CAT_COLS)
        
        # Eventos de selección
        self.sheet_catalog.extra_bindings([
            ("cell_select", self._on_catalog_select),
            ("row_select", self._on_catalog_select)
        ])

        # --- PANEL DERECHO: PRÉSTAMOS ---
        right_panel = ctk.CTkFrame(self, fg_color="transparent")
        right_panel.grid(row=1, column=1, sticky="nsew", padx=(15, 25), pady=(0, 10))

        top_right = ctk.CTkFrame(right_panel, fg_color="transparent")
        top_right.pack(fill="x", pady=(0, 10))
        
        icon_loan = ctk.CTkImage(Image.open(get_resource_path(os.path.join("assets", "icons", "dashboard", "772938_prestamo.png"))), size=(24, 24))
        ctk.CTkLabel(top_right, text=" Préstamos Activos", image=icon_loan, compound="left", font=("Arial", 18, "bold"), text_color=_ORANGE_HEADER).pack(side="left")

        # Tabla Préstamos
        headers_loan = ["N°", "USUARIO SOLICITANTE", "FECHA SOLICITUD", "CANT.", "ESTADO"]
        self.sheet_loans = self._create_styled_sheet(right_panel, headers_loan, _ORANGE_HEADER)
        self.sheet_loans.set_column_widths(_LOAN_COLS)

        # Eventos para la tabla de préstamos
        self.sheet_loans.extra_bindings([
            ("cell_select", self._on_loan_select),
            ("row_select", self._on_loan_select)
        ])

        # Botón para Devolución
        icon_return = ctk.CTkImage(Image.open(get_resource_path(os.path.join("assets", "icons", "buttons", "show_8358982.png"))), size=(20, 20))
        self.btn_devolver = ctk.CTkButton(
            right_panel, text=" FINALIZAR / DEVOLVER", image=icon_return,
            width=220, height=40, corner_radius=10,
            fg_color="#e67e22", hover_color="#d35400",
            font=("Arial", 12, "bold"),
            state="disabled",
            command=self._on_devolver_click
        )
        self.btn_devolver.pack(pady=10, side="right")

    def _create_styled_sheet(self, parent, headers, header_bg):
        sheet = Sheet(
            parent,
            headers=headers,
            header_bg=header_bg,
            header_fg="white",
            header_height=48,
            row_height=65,
            font=("Arial", 12, "normal"),
            header_font=("Arial", 12, "bold"),
            table_bg="white",
            table_fg="#2c3e50",
            show_row_index=False,
            outline_thickness=0,
            all_rows_highlight_color=_SELECTED_COLOR,
            align="w",
            header_align="w"
        )
        sheet.pack(fill="both", expand=True)
        sheet.enable_bindings("single_select", "row_select", "column_width_resize", "arrowkeys")
        return sheet

    def _build_selection_details(self):
        self.details_frame = ctk.CTkFrame(self, fg_color="#f8f9fa", height=110, corner_radius=12, border_width=1, border_color="#e0e0e0")
        self.details_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=25, pady=(5, 20))
        self.details_frame.grid_propagate(False)

        # Info del Instrumento
        self.info_container = ctk.CTkFrame(self.details_frame, fg_color="transparent")
        self.info_container.pack(side="left", fill="both", expand=True, padx=25, pady=10)

        self.lbl_sel_name = ctk.CTkLabel(self.info_container, text="Seleccione un instrumento del catálogo", font=("Arial", 16, "bold"), text_color="#2c3e50", anchor="w")
        self.lbl_sel_name.pack(fill="x", pady=(15, 0))

        self.lbl_sel_detail = ctk.CTkLabel(self.info_container, text="Haga clic en una fila del catálogo izquierdo para ver los detalles.", font=("Arial", 13), text_color="#7f8c8d", anchor="w")
        self.lbl_sel_detail.pack(fill="x", pady=2)

        # Botón PRESTAR
        icon_rocket = ctk.CTkImage(Image.open(get_resource_path(os.path.join("assets", "icons", "buttons", "add_6902311.png"))), size=(20, 20))
        self.btn_prestar = ctk.CTkButton(
            self.details_frame, text=" GENERAR PRÉSTAMO", image=icon_rocket,
            width=200, height=45, corner_radius=10,
            fg_color="#186ccf", hover_color="#145cb3",
            font=("Arial", 14, "bold"),
            state="disabled",
            command=self._on_prestar_click
        )
        self.btn_prestar.pack(side="right", padx=30)

    def _on_catalog_select(self, event=None):
        try:
            row = None
            if isinstance(event, int): row = event
            elif isinstance(event, (list, tuple)) and len(event) > 0: row = event[0]
            elif hasattr(event, "row"): row = event.row
            elif isinstance(event, dict) and "row" in event: row = event["row"]
            
            if row is None:
                selected = self.sheet_catalog.get_currently_selected()
                if selected: row = selected[0]
            
            if row is None or row < 0 or row >= len(self.filtered_instruments): return
                
            self.selected_instrument = self.filtered_instruments[row]
            unidad = getattr(self.selected_instrument, 'nombre_unidad', 'Und.')
            
            self.lbl_sel_name.configure(text=self.selected_instrument.descripcionInstrumento)
            self.lbl_sel_detail.configure(text=f"Marca: {self.selected_instrument.marcaInstrumento}  |  Modelo: {self.selected_instrument.modeloInstrumento}  |  En Stock: {self.selected_instrument.cantidadInstrumento:g} {unidad}")
            self.btn_prestar.configure(state="normal")
            
        except Exception as e:
            print(f"⚠️ Error en Selección: {e}")

    def _on_loan_select(self, event=None):
        try:
            row = None
            if isinstance(event, int): row = event
            elif hasattr(event, "row"): row = event.row
            
            if row is None:
                selected = self.sheet_loans.get_currently_selected()
                if selected: row = selected[0]
            
            if row is None or row < 0: return
                
            # Solo habilitar si el préstamo está 'ACTIVO'
            # (El estado está en la columna 4)
            status = str(self.sheet_loans.get_cell_data(row, 4)).lower()
            if 'activo' in status:
                self.selected_loan_id = int(self.all_loans[row].idPrestamo)
                self.btn_devolver.configure(state="normal")
            else:
                self.btn_devolver.configure(state="disabled")
        except: pass

    def _on_devolver_click(self):
        if not hasattr(self, 'selected_loan_id'): return
        
        from interfaces.components.mensajes import Alerts
        if Alerts.ask_question("Confirmar Devolución", "¿Confirma que los instrumentos han sido devueltos?", master=self):
            if PrestamoService.return_prestamo(self.selected_loan_id):
                Alerts.show_success("Éxito", "Devolución registrada. Stock actualizado.", master=self)
                self.load_data()
                self.btn_devolver.configure(state="disabled")
            else:
                Alerts.show_error("Error", "No se pudo procesar la devolución.", master=self)

    def _on_prestar_click(self):
        if not self.selected_instrument: return
        
        # Abrir el modal y pasarle el instrumento seleccionado y el usuario actual
        modal = CreatePrestamoModal(
            self.winfo_toplevel(), 
            self.selected_instrument, 
            self.usuario if self.usuario else {}, 
            on_success=self.load_data
        )

    def _resize_tables(self, event=None):
        try:
            # Catálogo: Descripción es la columna flexible (índice 1)
            cat_w = self.sheet_catalog.winfo_width()
            if cat_w > 100:
                fixed = _CAT_COLS[0] + _CAT_COLS[2] + _CAT_COLS[3] + 20
                flex_w = max(150, cat_w - fixed)
                self.sheet_catalog.column_width(0, width=_CAT_COLS[0], redraw=False)
                self.sheet_catalog.column_width(1, width=flex_w, redraw=False)
                self.sheet_catalog.column_width(2, width=_CAT_COLS[2], redraw=False)
                self.sheet_catalog.column_width(3, width=_CAT_COLS[3], redraw=False)
                self.sheet_catalog.redraw()

            # Préstamos: Usuario es flexible (índice 1)
            loan_w = self.sheet_loans.winfo_width()
            if loan_w > 100:
                fixed = _LOAN_COLS[0] + _LOAN_COLS[2] + _LOAN_COLS[3] + _LOAN_COLS[4] + 20
                flex_w = max(150, loan_w - fixed)
                self.sheet_loans.column_width(0, width=_LOAN_COLS[0], redraw=False)
                self.sheet_loans.column_width(1, width=flex_w, redraw=False)
                self.sheet_loans.column_width(2, width=_LOAN_COLS[2], redraw=False)
                self.sheet_loans.column_width(3, width=_LOAN_COLS[3], redraw=False)
                self.sheet_loans.column_width(4, width=_LOAN_COLS[4], redraw=False)
                self.sheet_loans.redraw()
        except: pass

    def load_data(self, event=None):
        # 1. Recargar Catálogo
        self.all_instruments = InstrumentoService.get_all_instrumentos()
        self.filtered_instruments = [it for it in self.all_instruments if (it.estado or "").lower() == "disponible"]
        self._render_catalog()
        
        # 2. Recargar Préstamos
        self.all_loans = PrestamoService.get_all_prestamos()
        self._render_loans()

    def _render_loans(self):
        loan_rows = []
        for i, p in enumerate(self.all_loans):
            fecha = p.fechaSolicitud.strftime("%d/%m/%Y %H:%M") if p.fechaSolicitud else "—"
            loan_rows.append([
                str(i+1).zfill(2),
                getattr(p, 'nombre_usuario', 'Desconocido'),
                fecha,
                f"{getattr(p, 'cantidad_solicitada', 0):g}",
                (p.estadoPrestamo or "Pendiente").upper()
            ])
        self.sheet_loans.set_sheet_data(loan_rows, reset_col_positions=False)
        self._apply_zebra_stripes(self.sheet_loans, len(loan_rows))
        self.after_idle(self._resize_tables)

    def _render_catalog(self):
        rows = []
        for i, it in enumerate(self.filtered_instruments):
            unidad = getattr(it, 'nombre_unidad', 'Und.')
            rows.append([
                str(i+1).zfill(2),
                it.descripcionInstrumento,
                f"{it.cantidadInstrumento:g} {unidad}",
                getattr(it, 'nombre_laboratorio', 'N/A')
            ])
        self.sheet_catalog.set_sheet_data(rows, reset_col_positions=False)
        self._apply_zebra_stripes(self.sheet_catalog, len(rows))
        self.after_idle(self._resize_tables)

    def _filter_catalog(self, event=None):
        query = self.search_catalog.get().lower().strip()
        self.filtered_instruments = [
            it for it in self.all_instruments 
            if (it.estado or "").lower() == "disponible" and (query in (it.descripcionInstrumento or "").lower())
        ]
        self._render_catalog()

    def _apply_zebra_stripes(self, sheet, row_count):
        for r in range(row_count):
            bg = "white" if r % 2 == 0 else _ALT_ROW_BG
            sheet.highlight_rows(r, bg=bg, redraw=False)
        sheet.redraw()

if __name__ == "__main__":
    app = ctk.CTk()
    app.geometry("1400x800")
    PrestamosFrame(app).pack(fill="both", expand=True, padx=20, pady=20)
    app.mainloop()
