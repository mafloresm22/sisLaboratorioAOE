import customtkinter as ctk
from services.laboratorios.laboratorios import LaboratorioService
from interfaces.components.mensajes import Alerts

class EditLaboratorioModal(ctk.CTkToplevel):
    def __init__(self, master, lab_data, parent_view=None, **kwargs):
        super().__init__(master, **kwargs)
        self.withdraw()
        self.parent_view = parent_view
        self.id_lab = lab_data.idLaboratorios
        self.old_nombre = lab_data.nombreLaboratorios
        self.old_piso = lab_data.pisoLaboratorios
        
        # --- CAPA DE OPACIDAD ---
        self.overlay = ctk.CTkToplevel(self.master)
        self.overlay.withdraw()
        self.overlay.geometry(f"{self.overlay.winfo_screenwidth()}x{self.overlay.winfo_screenheight()}+0+0")
        self.overlay.overrideredirect(True)
        self.overlay.configure(fg_color="black")
        self.overlay.attributes("-alpha", 0.5)
        
        # --- MODAL CONFIG ---
        self.overrideredirect(True)
        self.width = 500
        self.height = 380
        
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.target_x = ((screen_width // 2) - (self.width // 2)) + 150
        self.target_y = (screen_height // 2) - (self.height // 2)
        
        self.current_y = self.target_y - 80 
        self.geometry(f"{self.width}x{self.height}+{self.target_x}+{int(self.current_y)}")
        self.configure(fg_color="white")
        self.attributes("-alpha", 1.0)
        
        self.overlay.deiconify()
        self.deiconify()
        
        # --- CONTENEDOR ---
        self.container = ctk.CTkFrame(self, fg_color="white", corner_radius=10, border_width=1, border_color="#e0e0e0")
        self.container.pack(fill="both", expand=True)
        
        # 1. HEADER (Color Ámbar/Naranja para Edición)
        self.header = ctk.CTkFrame(self.container, fg_color="#f39c12", height=50, corner_radius=10)
        self.header.pack(fill="x", side="top")
        self.header.pack_propagate(False)
        
        self.lbl_title = ctk.CTkLabel(self.header, text="Editar Laboratorio", font=("Arial", 18, "bold"), text_color="white")
        self.lbl_title.pack(side="left", padx=20)
        
        self.btn_close = ctk.CTkButton(
            self.header, text="×", width=30, height=30, 
            fg_color="transparent", text_color="white", 
            hover_color="#e74c3c", font=("Arial", 24),
            command=self.close_modal
        )
        self.btn_close.pack(side="right", padx=10)
        
        # 2. BODY
        self.body = ctk.CTkFrame(self.container, fg_color="white")
        self.body.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Nombre
        self.lbl_field = ctk.CTkLabel(self.body, text="Nombre del Laboratorio", font=("Arial", 14, "bold"), text_color="#34495e")
        self.lbl_field.pack(anchor="w", pady=(0, 5))
        
        self.entry_nombre = ctk.CTkEntry(
            self.body, height=45, corner_radius=8, font=("Arial", 14), border_width=2
        )
        self.entry_nombre.pack(fill="x", pady=(0, 15))
        self.entry_nombre.insert(0, self.old_nombre)
        
        # Piso
        self.lbl_piso = ctk.CTkLabel(self.body, text="Piso / Ubicación", font=("Arial", 14, "bold"), text_color="#34495e")
        self.lbl_piso.pack(anchor="w", pady=(0, 5))
        
        self.entry_piso = ctk.CTkEntry(
            self.body, height=45, corner_radius=8, font=("Arial", 14), border_width=2
        )
        self.entry_piso.pack(fill="x")
        self.entry_piso.insert(0, self.old_piso)

        # 3. FOOTER
        self.footer = ctk.CTkFrame(self.container, fg_color="#f8f9fa", height=60, corner_radius=10)
        self.footer.pack(fill="x", side="bottom")
        self.footer.pack_propagate(False)
        
        self.btn_aceptar = ctk.CTkButton(
            self.footer, text="Actualizar", 
            fg_color="#f39c12", hover_color="#e67e22",
            width=100, height=35, corner_radius=8,
            command=self.update_laboratorio
        )
        self.btn_aceptar.pack(side="right", padx=(0, 30), pady=12)

        self.btn_cancelar = ctk.CTkButton(
            self.footer, text="Cancelar", 
            fg_color="#F25838", hover_color="#F25838",
            width=100, height=35, corner_radius=8,
            command=self.close_modal
        )
        self.btn_cancelar.pack(side="right", padx=10, pady=12)

        self.animate_entry()
        self.attributes("-topmost", True)
        self.grab_set()

    def animate_entry(self):
        if self.current_y < self.target_y:
            distancia = self.target_y - self.current_y
            self.current_y += (distancia * 0.2) + 1
            self.geometry(f"{self.width}x{self.height}+{self.target_x}+{int(self.current_y)}")
            self.after(10, self.animate_entry)

    def close_modal(self):
        self.grab_release()
        self.animate_exit()

    def animate_exit(self):
        try:
            alpha = float(self.attributes("-alpha"))
            overlay_alpha = float(self.overlay.attributes("-alpha"))
            if alpha > 0:
                self.current_y += 10
                new_alpha = max(0, alpha - 0.1)
                new_overlay_alpha = max(0, overlay_alpha - 0.05)
                self.attributes("-alpha", new_alpha)
                self.overlay.attributes("-alpha", new_overlay_alpha)
                self.geometry(f"{self.width}x{self.height}+{self.target_x}+{int(self.current_y)}")
                self.after(10, self.animate_exit)
            else:
                self.overlay.destroy()
                self.destroy()
        except:
            try: self.overlay.destroy()
            except: pass
            try: self.destroy()
            except: pass

    def update_laboratorio(self):
        nuevo_nombre = self.entry_nombre.get().strip()
        nuevo_piso = self.entry_piso.get().strip()

        if not nuevo_nombre or not nuevo_piso:
            Alerts.show_error("Campos requeridos", "Todos los campos son obligatorios.", master=self)
            return
        
        if nuevo_nombre == self.old_nombre and nuevo_piso == self.old_piso:
            self.close_modal()
            return

        resultado = LaboratorioService.update_laboratorio(self.id_lab, nuevo_nombre, nuevo_piso)
        
        if resultado == "exists":
            Alerts.show_warning("Ya existe", f"Ya existe otro laboratorio con el nombre '{nuevo_nombre}'.", master=self)
        elif resultado:
            Alerts.show_success("Éxito", "El laboratorio ha sido actualizado correctamente.", master=self)
            if self.parent_view:
                self.parent_view.load_data()
            self.close_modal()
        else:
            Alerts.show_error("Error", "No se pudo actualizar el laboratorio.", master=self)
