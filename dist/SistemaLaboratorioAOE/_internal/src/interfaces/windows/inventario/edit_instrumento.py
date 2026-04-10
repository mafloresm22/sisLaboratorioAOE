import customtkinter as ctk
from PIL import Image
import os
from tkinter import filedialog
from services.instrumentos.instrumentos import InstrumentoService
from services.laboratorios.laboratorios import LaboratorioService
from services.unidad.unidad import UnidadService
from database.connection import DatabaseConnection
from models.instrumentos.instrumentos import Instrumento
from interfaces.components.mensajes import Alerts
from utils.paths import get_resource_path, get_storage_path

# Directorio de iconos (usando get_resource_path para compatibilidad con .exe)
_ICONS_DIR = os.path.join("assets", "icons", "buttons")

class EditInstrumentoModal(ctk.CTkToplevel):
    def __init__(self, master, instrumento, parent_view=None, usuario=None, **kwargs):
        super().__init__(master, **kwargs)
        self.withdraw()
        self.instrumento = instrumento
        self.parent_view = parent_view
        self.usuario = usuario 
        self.image_path = instrumento.imagenInstrumento

        # --- CAPA DE OPACIDAD (OVERLAY) ---
        self.overlay = ctk.CTkToplevel(self.master)
        self.overlay.withdraw()
        self.overlay.geometry(f"{self.overlay.winfo_screenwidth()}x{self.overlay.winfo_screenheight()}+0+0")
        self.overlay.overrideredirect(True)
        self.overlay.configure(fg_color="black")
        self.overlay.attributes("-alpha", 0.0)

        # --- MODAL ---
        self.overrideredirect(True)
        self.width = 1150 
        self.height = 680

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

        # 1. HEADER (Color NARANJA solicitado)
        self.header = ctk.CTkFrame(self.container, fg_color="#e67e22", height=50, corner_radius=20)
        self.header.pack(fill="x", side="top", padx=2, pady=2)
        self.header.pack_propagate(False)

        try:
            icon_path = get_resource_path(os.path.join(_ICONS_DIR, "edit_3808637.png"))
            header_img = ctk.CTkImage(Image.open(icon_path), size=(20, 20))
            ctk.CTkLabel(self.header, text="", image=header_img).pack(side="left", padx=(20, 10))
        except: pass

        ctk.CTkLabel(self.header, text=f"Editar Instrumento: ID {self.instrumento.idInstrumento}", font=("Outfit", 18, "bold"), text_color="white").pack(side="left")

        ctk.CTkButton(
            self.header, text="✕", width=30, height=30,
            fg_color="transparent", text_color="white",
            hover_color="#d35400", font=("Arial", 16), corner_radius=15,
            command=self.close_modal
        ).pack(side="right", padx=10)

        # 2. BODY
        self.body = ctk.CTkFrame(self.container, fg_color="white")
        self.body.pack(fill="both", expand=True, padx=30, pady=15)
        
        self._build_form_grid()
        self._load_instrumento_data()

        # 3. FOOTER
        self.footer = ctk.CTkFrame(self.container, fg_color="#fdfdfd", height=70, corner_radius=20)
        self.footer.pack(fill="x", side="bottom", padx=2, pady=2)
        self.footer.pack_propagate(False)

        ctk.CTkFrame(self.footer, fg_color="#f1f2f6", height=1).pack(fill="x", side="top")

        ctk.CTkButton(
            self.footer, text="Actualizar Registro",
            fg_color="#e67e22", hover_color="#d35400",
            width=180, height=40, corner_radius=10,
            font=("Outfit", 14, "bold"),
            command=self.update_instrumento
        ).pack(side="right", padx=(0, 30), pady=12)

        ctk.CTkButton(
            self.footer, text="Cancelar",
            fg_color="#fc3268", hover_color="#d35400",
            text_color="white", width=110, height=40, corner_radius=10,
            font=("Outfit", 14, "bold"),
            command=self.close_modal
        ).pack(side="right", padx=10, pady=12)

        self.animate_entry()
        self.attributes("-topmost", True)
        self.grab_set()

    def _label(self, master, text):
        return ctk.CTkLabel(master, text=text, font=("Outfit", 13, "bold"), text_color="#34495e")

    def _build_form_grid(self):
        self.body.grid_columnconfigure(0, weight=1)
        self.body.grid_columnconfigure(1, weight=1)
        self.body.grid_columnconfigure(2, weight=1)
        self.body.grid_columnconfigure(3, weight=0, minsize=210)

        # --- SECCIÓN DATOS ---
        f_desc = ctk.CTkFrame(self.body, fg_color="transparent")
        f_desc.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 15))
        self._label(f_desc, "Descripción del Instrumento").pack(anchor="w")
        self.entry_descripcion = ctk.CTkTextbox(f_desc, height=65, corner_radius=10, border_width=2, border_color="#dcdde1", font=("Outfit", 12))
        self.entry_descripcion.pack(fill="x", pady=(5, 0))

        self._label(self.body, "Cantidad").grid(row=1, column=0, sticky="w", padx=5)
        self._label(self.body, "Marca").grid(row=1, column=1, sticky="w", padx=5)
        self._label(self.body, "Modelo").grid(row=1, column=2, sticky="w", padx=5)
        
        self.entry_cantidad = ctk.CTkEntry(self.body, height=38, corner_radius=8, border_width=2)
        self.entry_cantidad.grid(row=2, column=0, sticky="ew", padx=10, pady=(4, 15))
        
        self.entry_marca = ctk.CTkEntry(self.body, height=38, corner_radius=8, border_width=2)
        self.entry_marca.grid(row=2, column=1, sticky="ew", padx=10, pady=(4, 15))
        
        self.entry_modelo = ctk.CTkEntry(self.body, height=38, corner_radius=8, border_width=2)
        self.entry_modelo.grid(row=2, column=2, sticky="ew", padx=10, pady=(4, 15))

        self._label(self.body, "Serie").grid(row=3, column=0, sticky="w", padx=5)
        self._label(self.body, "Color").grid(row=3, column=1, sticky="w", padx=5)
        self._label(self.body, "Tamaño").grid(row=3, column=2, sticky="w", padx=5)
        
        self.entry_serie = ctk.CTkEntry(self.body, height=38, corner_radius=8, border_width=2)
        self.entry_serie.grid(row=4, column=0, sticky="ew", padx=10, pady=(4, 15))
        
        self.entry_color = ctk.CTkEntry(self.body, height=38, corner_radius=8, border_width=2)
        self.entry_color.grid(row=4, column=1, sticky="ew", padx=10, pady=(4, 15))
        
        self.combo_tamano = ctk.CTkComboBox(self.body, values=["Grande", "Mediano", "Pequeño"], height=38, corner_radius=8, border_width=2, state="readonly")
        self.combo_tamano.grid(row=4, column=2, sticky="ew", padx=10, pady=(4, 15))

        self._label(self.body, "Laboratorio").grid(row=5, column=0, sticky="w", padx=5)
        self._label(self.body, "Unidad de Medida").grid(row=5, column=1, sticky="w", padx=5)
        self._label(self.body, "Estado Conser.").grid(row=5, column=2, sticky="w", padx=5)
        
        self.labs_data = [lab for lab in LaboratorioService.get_all_laboratorios()] # En edición mostramos todos por si acaso
        lab_names = [lab.nombreLaboratorios for lab in self.labs_data]
        self.combo_lab = ctk.CTkComboBox(self.body, values=lab_names, height=38, corner_radius=8, border_width=2, state="readonly", command=self._on_lab_changed)
        self.combo_lab.grid(row=6, column=0, sticky="ew", padx=10, pady=(4, 0))
        
        self.unidades_data = UnidadService.get_all_unidades()
        unidad_names = [u.nombreUnidad for u in self.unidades_data]
        self.combo_unidad = ctk.CTkComboBox(self.body, values=unidad_names, height=38, corner_radius=8, border_width=2, state="readonly")
        self.combo_unidad.grid(row=6, column=1, sticky="ew", padx=10, pady=(4, 0))
        
        self.estados_data = self._load_estados_from_db()
        estado_names = [e["nombre"] for e in self.estados_data]
        self.combo_estado = ctk.CTkComboBox(self.body, values=estado_names, height=38, corner_radius=8, border_width=2, state="readonly")
        self.combo_estado.grid(row=6, column=2, sticky="ew", padx=10, pady=(4, 0))

        self.lbl_piso_info = ctk.CTkLabel(self.body, text="", font=("Outfit", 12, "italic"), text_color="#95a5a6", anchor="w")
        self.lbl_piso_info.grid(row=7, column=0, sticky="w", padx=15, pady=(2, 0))

        # --- COLUMNA DERECHA: FOTO ---
        f_foto = ctk.CTkFrame(self.body, fg_color="#f8f9fa", corner_radius=15, border_width=1, border_color="#ecf0f1")
        f_foto.grid(row=0, column=3, rowspan=8, sticky="nsew", padx=(10, 0))
        
        self._label(f_foto, "Imagen del Instrumento").pack(pady=(15, 10))
        
        self.photo_preview = ctk.CTkLabel(f_foto, text="Previsualización", width=180, height=180, fg_color="#e0e0e0", corner_radius=10, text_color="#7f8c8d")
        self.photo_preview.pack(padx=15, pady=10)
        
        ctk.CTkButton(
            f_foto, text="Cambiar Imagen", fg_color="#34495e", hover_color="#2c3e50",
            width=160, height=32, corner_radius=8, command=self._pick_image
        ).pack(pady=10)
        
        self.lbl_photo_name = ctk.CTkLabel(f_foto, text="", font=("Outfit", 11), text_color="#95a5a6", wraplength=200)
        self.lbl_photo_name.pack(pady=2)

    def _load_instrumento_data(self):
        # Texto
        self.entry_descripcion.insert("1.0", self.instrumento.descripcionInstrumento or "")
        self.entry_cantidad.insert(0, f"{self.instrumento.cantidadInstrumento:g}")
        self.entry_marca.insert(0, self.instrumento.marcaInstrumento or "")
        self.entry_modelo.insert(0, self.instrumento.modeloInstrumento or "")
        self.entry_serie.insert(0, self.instrumento.serieInstrumento or "")
        self.entry_color.insert(0, self.instrumento.colorInstrumento or "")
        
        # Combos
        self.combo_tamano.set(self.instrumento.tamanoInstrumento or "Mediano")
        
        lab_name = next((l.nombreLaboratorios for l in self.labs_data if l.idLaboratorios == self.instrumento.laboratorioId), "")
        if lab_name: 
            self.combo_lab.set(lab_name)
            self._on_lab_changed(lab_name)
            
        unidad_name = next((u.nombreUnidad for u in self.unidades_data if u.idUnidad == self.instrumento.unidadId), "")
        if unidad_name: self.combo_unidad.set(unidad_name)
        
        estado_name = next((e["nombre"] for e in self.estados_data if e["id"] == self.instrumento.idEstadoCons), "")
        if estado_name: self.combo_estado.set(estado_name)

        # Imagen
        if self.instrumento.imagenInstrumento:
            self._load_image_preview(self.instrumento.imagenInstrumento)

    def _load_image_preview(self, path):
        try:
            full_path = get_storage_path(path)
            
            if not os.path.exists(full_path):
                full_path = path if os.path.isabs(path) else get_resource_path(path)
            
            if os.path.exists(full_path):
                img = Image.open(full_path)
                preview = ctk.CTkImage(img, size=(180, 180))
                self.photo_preview.configure(text="", image=preview)
                self.lbl_photo_name.configure(text=os.path.basename(path))
        except Exception as e:
            print(f"Error cargando preview en edición: {e}")

    def _pick_image(self):
        self.attributes("-topmost", False)
        path = filedialog.askopenfilename(parent=self, title="Seleccionar Imagen", filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.bmp *.webp")])
        self.attributes("-topmost", True)
        self.focus_set()
        
        if path:
            self.image_path = path
            self.lbl_photo_name.configure(text=f"Nueva: {os.path.basename(path)}")
            try:
                img = Image.open(path)
                preview = ctk.CTkImage(img, size=(180, 180))
                self.photo_preview.configure(text="", image=preview)
            except: pass

    def _load_estados_from_db(self):
        conn = DatabaseConnection.get_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT idEstadoCons, nombreEstado FROM EstadoConservacion ORDER BY idEstadoCons DESC")
            return [{"id": row[0], "nombre": row[1]} for row in cursor.fetchall()]
        except: return []
        finally:
            if conn: conn.close()

    def _on_lab_changed(self, selected_name):
        for lab in self.labs_data:
            if lab.nombreLaboratorios == selected_name:
                piso = lab.pisoLaboratorios or "—"
                self.lbl_piso_info.configure(text=f"📍 Piso {piso}")
                break

    def update_instrumento(self):
        desc = self.entry_descripcion.get("1.0", "end-1c").strip()
        cant = self.entry_cantidad.get().strip()
        lab_name = self.combo_lab.get()
        unidad_name = self.combo_unidad.get()
        estado_name = self.combo_estado.get()

        if not desc:
            Alerts.show_error("Campo requerido", "La descripción es obligatoria.", master=self)
            return

        try:
            cant_val = float(cant) if cant else 0.0
        except:
            Alerts.show_error("Error", "La cantidad debe ser numérica.", master=self)
            return

        lab_id = next((l.idLaboratorios for l in self.labs_data if l.nombreLaboratorios == lab_name), None)
        piso = next((l.pisoLaboratorios for l in self.labs_data if l.nombreLaboratorios == lab_name), None)
        unidad_id = next((u.idUnidad for u in self.unidades_data if u.nombreUnidad == unidad_name), None)
        estado_id = next((e["id"] for e in self.estados_data if e["nombre"] == estado_name), None)
        usuario_id = self.usuario.get("idUsuarios") if self.usuario else self.instrumento.usuarioId
        tamano = self.combo_tamano.get()

        if not all([lab_id, unidad_id, estado_id]):
            Alerts.show_error("Error", "Por favor seleccione todas las opciones.", master=self)
            return

        # Actualizar objeto modelo
        self.instrumento.descripcionInstrumento = desc
        self.instrumento.cantidadInstrumento = cant_val
        self.instrumento.marcaInstrumento = self.entry_marca.get().strip() or "..."
        self.instrumento.modeloInstrumento = self.entry_modelo.get().strip() or "..."
        self.instrumento.serieInstrumento = self.entry_serie.get().strip() or "..."
        self.instrumento.colorInstrumento = self.entry_color.get().strip() or "..."
        self.instrumento.tamanoInstrumento = tamano
        self.instrumento.pisoInstrumento = piso
        self.instrumento.idEstadoCons = estado_id
        self.instrumento.laboratorioId = lab_id
        self.instrumento.unidadId = unidad_id
        self.instrumento.imagenInstrumento = self.image_path

        if InstrumentoService.update_instrumento(self.instrumento):
            Alerts.show_success("Éxito", "Instrumento actualizado correctamente.", master=self)
            if self.parent_view:
                self.parent_view.all_data = [] # Forzar recarga
                self.parent_view.load_data()
            self.close_modal()
        else:
            Alerts.show_error("Error", "No se pudo actualizar el registro.", master=self)

    def close_modal(self):
        self.grab_release()
        self.animate_exit()

    def animate_entry(self):
        try:
            alpha = float(self.attributes("-alpha"))
            overlay_alpha = float(self.overlay.attributes("-alpha"))

            if alpha < 1.0: self.attributes("-alpha", min(1.0, alpha + 0.12))
            if overlay_alpha < 0.5: self.overlay.attributes("-alpha", min(0.5, overlay_alpha + 0.05))

            if self.current_y < self.target_y:
                self.current_y += (self.target_y - self.current_y) * 0.15 + 0.5
                self.geometry(f"+{self.target_x}+{int(self.current_y)}")
                self.after(8, self.animate_entry)
            elif alpha < 1.0 or overlay_alpha < 0.5:
                self.after(8, self.animate_entry)
        except: pass

    def animate_exit(self):
        try:
            alpha = float(self.attributes("-alpha"))
            if alpha > 0:
                self.current_y += 18
                self.attributes("-alpha", max(0, alpha - 0.15))
                self.overlay.attributes("-alpha", max(0, float(self.overlay.attributes("-alpha")) - 0.08))
                self.geometry(f"+{self.target_x}+{int(self.current_y)}")
                self.after(8, self.animate_exit)
            else:
                self.overlay.destroy()
                self.destroy()
        except: pass
