import customtkinter as ctk
from PIL import Image
import os
from services.instrumentos.instrumentos import InstrumentoService
from services.laboratorios.laboratorios import LaboratorioService
from services.unidad.unidad import UnidadService
from database.connection import DatabaseConnection
from models.instrumentos.instrumentos import Instrumento
from interfaces.components.mensajes import Alerts

# Directorio de iconos
_ICONS_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "..", "assets", "icons", "buttons"
))

class CreateInstrumentoModal(ctk.CTkToplevel):
    def __init__(self, master, parent_view=None, usuario=None, **kwargs):
        super().__init__(master, **kwargs)
        self.withdraw()
        self.parent_view = parent_view
        self.usuario = usuario 

        # --- CAPA DE OPACIDAD (OVERLAY) ---
        self.overlay = ctk.CTkToplevel(self.master)
        self.overlay.withdraw()
        self.overlay.geometry(f"{self.overlay.winfo_screenwidth()}x{self.overlay.winfo_screenheight()}+0+0")
        self.overlay.overrideredirect(True)
        self.overlay.configure(fg_color="black")
        self.overlay.attributes("-alpha", 0.5)

        # --- MODAL ---
        self.overrideredirect(True)
        self.width = 850
        self.height = 700

        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.target_x = (screen_width // 2) - (self.width // 2)
        self.target_y = (screen_height // 2) - (self.height // 2)

        self.current_y = self.target_y - 100
        self.geometry(f"{self.width}x{self.height}+{self.target_x}+{int(self.current_y)}")
        self.configure(fg_color="white")
        self.attributes("-alpha", 0.0)

        self.overlay.deiconify()
        self.deiconify()

        # --- CONTENEDOR PRINCIPAL ---
        self.container = ctk.CTkFrame(self, fg_color="white", corner_radius=20, border_width=1, border_color="#ecf0f1")
        self.container.pack(fill="both", expand=True)

        # 1. HEADER
        self.header = ctk.CTkFrame(self.container, fg_color="#3897f5", height=70, corner_radius=20)
        self.header.pack(fill="x", side="top", padx=2, pady=2)
        self.header.pack_propagate(False)

        try:
            icon_path = os.path.join(_ICONS_DIR, "add_6902311.png")
            header_img = ctk.CTkImage(Image.open(icon_path), size=(30, 30))
            ctk.CTkLabel(self.header, text="", image=header_img).pack(side="left", padx=(25, 10))
        except:
            pass

        ctk.CTkLabel(self.header, text="Registrar Nuevo Instrumento", font=("Outfit", 22, "bold"), text_color="white").pack(side="left")

        ctk.CTkButton(
            self.header, text="✕", width=40, height=40,
            fg_color="transparent", text_color="white",
            hover_color="#e74c3c", font=("Arial", 20), corner_radius=20,
            command=self.close_modal
        ).pack(side="right", padx=15)

        # 2. BODY
        self.scroll_body = ctk.CTkScrollableFrame(self.container, fg_color="white", corner_radius=0)
        self.scroll_body.pack(fill="both", expand=True, padx=40, pady=20)

        self._create_form_fields()

        # 3. FOOTER
        self.footer = ctk.CTkFrame(self.container, fg_color="#fdfdfd", height=80, corner_radius=20)
        self.footer.pack(fill="x", side="bottom", padx=2, pady=2)
        self.footer.pack_propagate(False)

        ctk.CTkFrame(self.footer, fg_color="#f1f2f6", height=2).pack(fill="x", side="top")

        ctk.CTkButton(
            self.footer, text="Guardar Registro",
            fg_color="#27ae60", hover_color="#2ecc71",
            width=180, height=45, corner_radius=12,
            font=("Outfit", 15, "bold"),
            command=self.save_instrumento
        ).pack(side="right", padx=(0, 40), pady=15)

        ctk.CTkButton(
            self.footer, text="Cancelar",
            fg_color="transparent", hover_color="#f1f2f6",
            text_color="#7f8c8d", width=120, height=45, corner_radius=12,
            font=("Outfit", 15, "bold"),
            command=self.close_modal
        ).pack(side="right", padx=15, pady=15)

        self.animate_entry()
        self.attributes("-topmost", True)
        self.grab_set()

    def _create_form_fields(self):
        def _label(master, text):
            return ctk.CTkLabel(master, text=text, font=("Outfit", 14, "bold"), text_color="#34495e")

        # --- SECCIÓN: INFORMACIÓN BÁSICA ---
        sec_basic = ctk.CTkFrame(self.scroll_body, fg_color="transparent")
        sec_basic.pack(fill="x", pady=(0, 20))

        _label(sec_basic, "Descripción del Instrumento").pack(anchor="w")
        self.entry_descripcion = ctk.CTkTextbox(
            sec_basic, height=80, corner_radius=12, border_width=2,
            border_color="#dcdde1", font=("Outfit", 13)
        )
        self.entry_descripcion.pack(fill="x", pady=(5, 15))

        # Fila 1: Cantidad y Marca
        row1 = ctk.CTkFrame(sec_basic, fg_color="transparent")
        row1.pack(fill="x", pady=5)

        f_cant = ctk.CTkFrame(row1, fg_color="transparent")
        f_cant.pack(side="left", fill="x", expand=True, padx=(0, 10))
        _label(f_cant, "Cantidad").pack(anchor="w")
        self.entry_cantidad = ctk.CTkEntry(f_cant, placeholder_text="Ej: 10", height=45, corner_radius=10, border_width=2)
        self.entry_cantidad.pack(fill="x", pady=5)

        f_marca = ctk.CTkFrame(row1, fg_color="transparent")
        f_marca.pack(side="left", fill="x", expand=True, padx=(10, 0))
        _label(f_marca, "Marca").pack(anchor="w")
        self.entry_marca = ctk.CTkEntry(f_marca, placeholder_text="Ej: Nikon, Generic...", height=45, corner_radius=10, border_width=2)
        self.entry_marca.pack(fill="x", pady=5)

        # --- SECCIÓN: DETALLES TÉCNICOS ---
        sec_tech = ctk.CTkFrame(self.scroll_body, fg_color="#f8f9fa", corner_radius=15)
        sec_tech.pack(fill="x", pady=10, ipadx=20, ipady=20)

        ctk.CTkLabel(sec_tech, text="Detalles Técnicos", font=("Outfit", 16, "bold"), text_color="#2c3e50").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))

        _label(sec_tech, "Modelo").grid(row=1, column=0, sticky="w")
        self.entry_modelo = ctk.CTkEntry(sec_tech, placeholder_text="Modelo...", width=350, height=45, corner_radius=10, border_width=2)
        self.entry_modelo.grid(row=2, column=0, sticky="w", pady=(5, 15), padx=(0, 20))

        _label(sec_tech, "Serie").grid(row=1, column=1, sticky="w")
        self.entry_serie = ctk.CTkEntry(sec_tech, placeholder_text="Número de serie...", width=350, height=45, corner_radius=10, border_width=2)
        self.entry_serie.grid(row=2, column=1, sticky="w", pady=(5, 15))

        _label(sec_tech, "Color").grid(row=3, column=0, sticky="w")
        self.entry_color = ctk.CTkEntry(sec_tech, placeholder_text="Ej: Negro, Gris...", width=350, height=45, corner_radius=10, border_width=2)
        self.entry_color.grid(row=4, column=0, sticky="w", pady=(5, 15), padx=(0, 20))

        _label(sec_tech, "Tamaño").grid(row=3, column=1, sticky="w")
        self.entry_tamano = ctk.CTkEntry(sec_tech, placeholder_text="Ej: Pequeño, Mediano...", width=350, height=45, corner_radius=10, border_width=2)
        self.entry_tamano.grid(row=4, column=1, sticky="w", pady=(5, 15))

        # --- SECCIÓN: UBICACIÓN, UNIDAD Y ESTADO ---
        sec_loc = ctk.CTkFrame(self.scroll_body, fg_color="transparent")
        sec_loc.pack(fill="x", pady=15)

        # Fila: Laboratorio (al seleccionar → piso se auto-rellena como info)
        f_lab = ctk.CTkFrame(sec_loc, fg_color="transparent")
        f_lab.pack(fill="x", pady=5)
        _label(f_lab, "Laboratorio Asignado").pack(anchor="w")

        self.labs_data = LaboratorioService.get_all_laboratorios()
        lab_names = [lab.nombreLaboratorios for lab in self.labs_data] if self.labs_data else []

        # ComboBox de laboratorio
        self.combo_lab = ctk.CTkComboBox(
            f_lab, values=lab_names, height=45, corner_radius=10, border_width=2,
            state="readonly", command=self._on_lab_changed
        )
        self.combo_lab.pack(fill="x", pady=5)

        # Etiqueta de piso (auto-rellenada al seleccionar laboratorio)
        self.lbl_piso_info = ctk.CTkLabel(
            f_lab, text="", font=("Outfit", 12), text_color="#7f8c8d",
            anchor="w"
        )
        self.lbl_piso_info.pack(anchor="w", padx=5)

        # Inicializar con el primer laboratorio si existe
        if lab_names:
            self.combo_lab.set(lab_names[0])
            self._on_lab_changed(lab_names[0])
        else:
            self.combo_lab.set("Sin laboratorios disponibles")

        # Fila: Unidad y Estado de Conservación
        row_unit_state = ctk.CTkFrame(sec_loc, fg_color="transparent")
        row_unit_state.pack(fill="x", pady=15)

        # Unidad (desde DB)
        f_unidad = ctk.CTkFrame(row_unit_state, fg_color="transparent")
        f_unidad.pack(side="left", fill="x", expand=True, padx=(0, 10))
        _label(f_unidad, "Unidad de Medida").pack(anchor="w")

        self.unidades_data = UnidadService.get_all_unidades()
        unidad_names = [u.nombreUnidad for u in self.unidades_data] if self.unidades_data else []
        self.combo_unidad = ctk.CTkComboBox(
            f_unidad, values=unidad_names, height=45, corner_radius=10, border_width=2, state="readonly"
        )
        self.combo_unidad.pack(fill="x", pady=5)
        if unidad_names:
            self.combo_unidad.set(unidad_names[0])

        # Estado de Conservación (desde DB)
        f_est = ctk.CTkFrame(row_unit_state, fg_color="transparent")
        f_est.pack(side="left", fill="x", expand=True, padx=(10, 0))
        _label(f_est, "Estado de Conservación").pack(anchor="w")

        self.estados_data = self._load_estados_from_db()
        estado_names = [e["nombre"] for e in self.estados_data]
        self.combo_estado = ctk.CTkComboBox(
            f_est, values=estado_names, height=45, corner_radius=10, border_width=2, state="readonly"
        )
        self.combo_estado.pack(fill="x", pady=5)
        # Seleccionar "Bueno" por defecto si existe
        bueno = next((e["nombre"] for e in self.estados_data if "buen" in e["nombre"].lower()), None)
        if bueno:
            self.combo_estado.set(bueno)
        elif estado_names:
            self.combo_estado.set(estado_names[0])

    def _load_estados_from_db(self):
        """Carga los estados de conservación desde la tabla EstadoConservacion."""
        conn = DatabaseConnection.get_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT idEstadoCons, nombreEstado FROM EstadoConservacion ORDER BY idEstadoCons DESC")
            return [{"id": row[0], "nombre": row[1]} for row in cursor.fetchall()]
        except Exception as e:
            print(f"🔴 Error SQL (load_estados): {e}")
            return []
        finally:
            if conn:
                conn.close()

    def _on_lab_changed(self, selected_name):
        """Al cambiar el laboratorio, muestra su piso automáticamente."""
        for lab in self.labs_data:
            if lab.nombreLaboratorios == selected_name:
                piso = lab.pisoLaboratorios or "—"
                self.lbl_piso_info.configure(text=f"📍 Piso: {piso}")
                break

    def animate_entry(self):
        try:
            alpha = float(self.attributes("-alpha"))
            if alpha < 1.0:
                self.attributes("-alpha", min(1.0, alpha + 0.1))
            if self.current_y < self.target_y:
                distancia = self.target_y - self.current_y
                self.current_y += (distancia * 0.15) + 0.5
                self.geometry(f"{self.width}x{self.height}+{self.target_x}+{int(self.current_y)}")
                self.after(10, self.animate_entry)
            elif alpha < 1.0:
                self.after(10, self.animate_entry)
        except:
            pass

    def close_modal(self):
        self.grab_release()
        self.animate_exit()

    def animate_exit(self):
        try:
            alpha = float(self.attributes("-alpha"))
            overlay_alpha = float(self.overlay.attributes("-alpha"))
            if alpha > 0:
                self.current_y += 15
                self.attributes("-alpha", max(0, alpha - 0.15))
                self.overlay.attributes("-alpha", max(0, overlay_alpha - 0.08))
                self.geometry(f"{self.width}x{self.height}+{self.target_x}+{int(self.current_y)}")
                self.after(10, self.animate_exit)
            else:
                self.overlay.destroy()
                self.destroy()
        except:
            pass

    def save_instrumento(self):
        descripcion = self.entry_descripcion.get("1.0", "end-1c").strip()
        cantidad = self.entry_cantidad.get().strip()
        marca = self.entry_marca.get().strip()
        modelo = self.entry_modelo.get().strip()
        serie = self.entry_serie.get().strip()
        color = self.entry_color.get().strip()
        tamano = self.entry_tamano.get().strip()

        if not descripcion:
            Alerts.show_error("Campo requerido", "La descripción es obligatoria.", master=self)
            return

        try:
            cantidad_int = int(cantidad) if cantidad else 0
        except ValueError:
            Alerts.show_error("Error de Dato", "La cantidad debe ser un número entero.", master=self)
            return

        # Laboratorio → ID y piso del mismo registro
        selected_lab_name = self.combo_lab.get()
        lab_id = None
        piso_auto = None
        for lab in self.labs_data:
            if lab.nombreLaboratorios == selected_lab_name:
                lab_id = lab.idLaboratorios
                piso_auto = lab.pisoLaboratorios
                break

        if not lab_id:
            Alerts.show_error("Laboratorio requerido", "Debes seleccionar un laboratorio.", master=self)
            return

        # Unidad → ID
        selected_unidad_name = self.combo_unidad.get()
        unidad_id = None
        for u in self.unidades_data:
            if u.nombreUnidad == selected_unidad_name:
                unidad_id = u.idUnidad
                break

        if not unidad_id:
            Alerts.show_error("Unidad requerida", "Debes seleccionar una unidad de medida.", master=self)
            return

        # Estado → ID desde DB
        selected_estado_name = self.combo_estado.get()
        estado_id = None
        for e in self.estados_data:
            if e["nombre"] == selected_estado_name:
                estado_id = e["id"]
                break

        if not estado_id:
            Alerts.show_error("Estado requerido", "Debes seleccionar un estado de conservación.", master=self)
            return

        # Usuario logueado
        usuario_id = self.usuario.get("idUsuarios") if self.usuario else None
        if not usuario_id:
            Alerts.show_error("Sin sesión", "No se pudo identificar al usuario logueado.", master=self)
            return

        nuevo_inst = Instrumento(
            descripcionInstrumento=descripcion,
            cantidadInstrumento=cantidad_int,
            marcaInstrumento=marca or None,
            modeloInstrumento=modelo or None,
            serieInstrumento=serie or None,
            colorInstrumento=color or None,
            tamanoInstrumento=tamano or None,
            pisoInstrumento=piso_auto,
            idEstadoCons=estado_id,
            usuarioId=usuario_id,
            laboratorioId=lab_id,
            unidadId=unidad_id,
            imagenInstrumento=None
        )

        res = InstrumentoService.create_instrumento(nuevo_inst)

        if res == "exists":
            Alerts.show_warning("Instrumento Duplicado", "Ya existe un instrumento con el mismo modelo, serie, color y tamaño.", master=self)
        elif res:
            Alerts.show_success("Registro Guardado", "El instrumento ha sido registrado exitosamente.", master=self)
            if self.parent_view:
                self.parent_view.all_data = []
                self.parent_view.load_data()
            self.close_modal()
        else:
            Alerts.show_error("Error", "No se pudo guardar el registro en la base de datos.", master=self)
