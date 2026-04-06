import customtkinter as ctk
from PIL import Image
import os

# Directorio de iconos de botones
_ICONS_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "..", "assets", "icons", "buttons"
))

class ShowInstrumentoModal(ctk.CTkToplevel):
    def __init__(self, master, instrumento, **kwargs):
        super().__init__(master, **kwargs)
        self.withdraw()
        self.instrumento = instrumento
        
        # --- CAPA DE OPACIDAD (OVERLAY) ---
        self.overlay = ctk.CTkToplevel(self.master)
        self.overlay.withdraw()
        self.overlay.geometry(f"{self.overlay.winfo_screenwidth()}x{self.overlay.winfo_screenheight()}+0+0")
        self.overlay.overrideredirect(True)
        self.overlay.configure(fg_color="black")
        self.overlay.attributes("-alpha", 0.5)

        # --- MODAL ---
        self.overrideredirect(True)
        self.width = 900
        self.height = 540

        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.target_x = (screen_width // 2) - (self.width // 2)
        self.target_y = (screen_height // 2) - (self.height // 2)

        self.current_y = self.target_y - 80
        self.geometry(f"{self.width}x{self.height}+{self.target_x}+{int(self.current_y)}")
        self.configure(fg_color="white")
        self.attributes("-alpha", 0.0)

        self.overlay.deiconify()
        self.deiconify()

        # --- CONTENEDOR PRINCIPAL ---
        self.container = ctk.CTkFrame(self, fg_color="white", corner_radius=25, border_width=1, border_color="#ecf0f1")
        self.container.pack(fill="both", expand=True)

        # 1. HEADER (Celeste)
        self.header = ctk.CTkFrame(self.container, fg_color="#3897f5", height=60, corner_radius=25)
        self.header.pack(fill="x", side="top", padx=2, pady=2)
        self.header.pack_propagate(False)

        try:
            icon_path = os.path.join(_ICONS_DIR, "show_8358982.png")
            header_img = ctk.CTkImage(Image.open(icon_path), size=(24, 24))
            ctk.CTkLabel(self.header, text="", image=header_img).pack(side="left", padx=(25, 10))
        except: pass

        ctk.CTkLabel(self.header, text="Detalle Técnico de Instrumento", font=("Outfit", 20, "bold"), text_color="white").pack(side="left")

        ctk.CTkButton(
            self.header, text="✕", width=35, height=35,
            fg_color="transparent", text_color="white",
            hover_color="#e74c3c", font=("Arial", 18, "bold"), corner_radius=18,
            command=self.close_modal
        ).pack(side="right", padx=15)

        # 2. BODY (Formato DNI / Ficha Técnica)
        self.body = ctk.CTkFrame(self.container, fg_color="white")
        self.body.pack(fill="both", expand=True, padx=35, pady=25)
        
        self.body.grid_columnconfigure(0, weight=0, minsize=320) # Foto (como DNI)
        self.body.grid_columnconfigure(1, weight=1)              # Datos
        self.body.grid_rowconfigure(0, weight=1)

        # --- COLUMNA IZQUIERDA: TARJETA FOTO ---
        f_dni_photo = ctk.CTkFrame(self.body, fg_color="#fcfcfc", corner_radius=20, border_width=1, border_color="#f0f0f0")
        f_dni_photo.grid(row=0, column=0, sticky="nsew", padx=(0, 25))
        
        # ID Único en la esquina
        ctk.CTkLabel(f_dni_photo, text=f"REF: {str(instrumento.idInstrumento).zfill(6)}", 
                    font=("Courier New", 12, "bold"), text_color="#7f8c8d").place(relx=0.05, rely=0.05)
        
        # Previsualización Imagen
        self.photo_label = ctk.CTkLabel(f_dni_photo, text="SIN IMAGEN", width=280, height=280, 
                                        fg_color="#f1f2f6", corner_radius=15, text_color="#bdc3c7", font=("Outfit", 14, "bold"))
        self.photo_label.pack(padx=20, pady=(45, 15))
        
        # Intentar cargar imagen
        self._load_instrumento_image()

        # Estado Cons. Badge
        status_colors = {5: "#27ae60", 4: "#2980b9", 3: "#f39c12", 2: "#e74c3c"}
        status_names  = {5: "NUEVO", 4: "BUENO", 3: "REGULAR", 2: "MALO"}
        cid = instrumento.idEstadoCons or 4
        
        f_badge = ctk.CTkFrame(f_dni_photo, fg_color=status_colors.get(cid, "#95a5a6"), corner_radius=10)
        f_badge.pack(pady=5, padx=20, fill="x")
        ctk.CTkLabel(f_badge, text=status_names.get(cid, "DESCONOCIDO"), text_color="white", 
                    font=("Outfit", 13, "bold")).pack(pady=4)

        # --- COLUMNA DERECHA: DATOS ---
        f_data = ctk.CTkFrame(self.body, fg_color="transparent")
        f_data.grid(row=0, column=1, sticky="nsew")

        # Descripción Grande
        desc_lbl = ctk.CTkLabel(f_data, text=instrumento.descripcionInstrumento or "Sin descripción", 
                                font=("Outfit", 22, "bold"), text_color="#2c3e50", wraplength=480, justify="left", anchor="w")
        desc_lbl.pack(fill="x", pady=(0, 15))

        # Grid de detalles
        f_grid = ctk.CTkFrame(f_data, fg_color="transparent")
        f_grid.pack(fill="both", expand=True)
        f_grid.grid_columnconfigure((0, 1), weight=1)

        self._add_field(f_grid, "MARCA", instrumento.marcaInstrumento, 0, 0)
        self._add_field(f_grid, "MODELO", instrumento.modeloInstrumento, 0, 1)
        self._add_field(f_grid, "SERIE", instrumento.serieInstrumento, 1, 0)
        self._add_field(f_grid, "COLOR", instrumento.colorInstrumento, 1, 1)
        self._add_field(f_grid, "TAMAÑO", instrumento.tamanoInstrumento, 2, 0)
        self._add_field(f_grid, "CANTIDAD", f"{instrumento.cantidadInstrumento} Unidades", 2, 1)
        self._add_field(f_grid, "UBICACIÓN", getattr(instrumento, 'nombre_laboratorio', 'No asignado'), 3, 0)
        self._add_field(f_grid, "PISO", f"Nivel {instrumento.pisoInstrumento or '—'}", 3, 1)
        self._add_field(f_grid, "ESTADO ACTUAL", (instrumento.estado or "DISPONIBLE").upper(), 4, 0, color="#27ae60")

        # 3. FOOTER
        self.footer = ctk.CTkFrame(self.container, fg_color="#fdfdfd", height=60, corner_radius=25)
        self.footer.pack(fill="x", side="bottom", padx=2, pady=2)
        self.footer.pack_propagate(False)

        ctk.CTkButton(
            self.footer, text="Cerrar Vista",
            fg_color="#34495e", hover_color="#2c3e50",
            width=140, height=35, corner_radius=8,
            font=("Outfit", 13, "bold"),
            command=self.close_modal
        ).pack(side="right", padx=30, pady=12)

        self.animate_entry()
        self.attributes("-topmost", True)
        self.grab_set()

    def _add_field(self, master, label, value, row, col, color="#2c3e50"):
        f = ctk.CTkFrame(master, fg_color="transparent")
        f.grid(row=row, column=col, sticky="nw", pady=8, padx=5)
        
        ctk.CTkLabel(f, text=label, font=("Outfit", 11, "bold"), text_color="#95a5a6").pack(anchor="w")
        ctk.CTkLabel(f, text=str(value or "—"), font=("Outfit", 14), text_color=color).pack(anchor="w")

    def _load_instrumento_image(self):
        if not self.instrumento.imagenInstrumento:
            return

        try:
            # Resolver path completo
            root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
            full_path = os.path.join(root_dir, self.instrumento.imagenInstrumento)
            
            if os.path.exists(full_path):
                img = Image.open(full_path)
                # Mantener proporción o recortar?
                # Para "DNI" suele ser un encuadre cuadrado o 4:3
                ctk_img = ctk.CTkImage(img, size=(280, 280))
                self.photo_label.configure(text="", image=ctk_img)
            else:
                # Si falló la ruta relativa, intentar como absoluta
                if os.path.exists(self.instrumento.imagenInstrumento):
                    img = Image.open(self.instrumento.imagenInstrumento)
                    ctk_img = ctk.CTkImage(img, size=(280, 280))
                    self.photo_label.configure(text="", image=ctk_img)
        except Exception as e:
            print(f"Error cargando imagen en detalle: {e}")

    def close_modal(self):
        self.grab_release()
        self.animate_exit()

    def animate_entry(self):
        try:
            alpha = float(self.attributes("-alpha"))
            if alpha < 1.0: self.attributes("-alpha", min(1.0, alpha + 0.15))
            if self.current_y < self.target_y:
                self.current_y += (self.target_y - self.current_y) * 0.18 + 0.5
                self.geometry(f"+{self.target_x}+{int(self.current_y)}")
                self.after(8, self.animate_entry)
            elif alpha < 1.0: self.after(8, self.animate_entry)
        except: pass

    def animate_exit(self):
        try:
            alpha = float(self.attributes("-alpha"))
            if alpha > 0:
                self.current_y += 15
                self.attributes("-alpha", max(0, alpha - 0.18))
                self.overlay.attributes("-alpha", max(0, float(self.overlay.attributes("-alpha")) - 0.1))
                self.geometry(f"+{self.target_x}+{int(self.current_y)}")
                self.after(8, self.animate_exit)
            else:
                self.overlay.destroy()
                self.destroy()
        except: pass
