import customtkinter as ctk
from services.usuarios.usuarios import UsuarioService
from interfaces.components.mensajes import Alerts

class RestablecerPasswordModal(ctk.CTkToplevel):
    def __init__(self, master, user_data, parent_view=None, **kwargs):
        super().__init__(master, **kwargs)
        self.withdraw() 
        self.parent_view = parent_view
        
        # Datos iniciales
        self.user_id = user_data.idUsuarios
        self.username = user_data.nombreUsuarios
        
        # --- CAPA DE OPACIDAD (OVERLAY) ---
        self.overlay = ctk.CTkToplevel(self.master)
        self.overlay.withdraw()
        self.overlay.geometry(f"{self.overlay.winfo_screenwidth()}x{self.overlay.winfo_screenheight()}+0+0")
        self.overlay.overrideredirect(True)
        self.overlay.configure(fg_color="black")
        self.overlay.attributes("-alpha", 0.5)
        
        # --- MODAL CONFIG ---
        self.overrideredirect(True)
        self.width = 450
        self.height = 320
        
        # Centrar el modal en pantalla
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.target_x = ((screen_width // 2) - (self.width // 2)) + 150
        self.target_y = (screen_height // 2) - (self.height // 2)
        
        # Parámetros para la animación
        self.current_y = self.target_y - 80 
        self.geometry(f"{self.width}x{self.height}+{self.target_x}+{int(self.current_y)}")
        self.configure(fg_color="white")
        self.attributes("-alpha", 1.0)
        
        self.overlay.deiconify()
        self.deiconify()
        
        # --- CONTENEDOR PRINCIPAL ---
        self.container = ctk.CTkFrame(self, fg_color="white", corner_radius=10, border_width=1, border_color="#e0e0e0")
        self.container.pack(fill="both", expand=True)
        
        # 1. HEADER (Color Rojo Pastel: #ff6b6b)
        self.header = ctk.CTkFrame(self.container, fg_color="#ff6b6b", height=50, corner_radius=10)
        self.header.pack(fill="x", side="top")
        self.header.pack_propagate(False)
        
        self.lbl_title = ctk.CTkLabel(self.header, text="Restablecer Contraseña", font=("Arial", 18, "bold"), text_color="white")
        self.lbl_title.pack(side="left", padx=20)
        
        self.btn_close = ctk.CTkButton(
            self.header, text="×", width=30, height=30, 
            fg_color="transparent", text_color="white", 
            hover_color="#ee5253", font=("Arial", 24),
            command=self.close_modal
        )
        self.btn_close.pack(side="right", padx=10)
        
        # 2. BODY
        self.body = ctk.CTkFrame(self.container, fg_color="white")
        self.body.pack(fill="both", expand=True, padx=40, pady=(20, 5))
        
        # Información del usuario
        self.lbl_info = ctk.CTkLabel(
            self.body, 
            text=f"Ingresa la nueva contraseña para:\n'{self.username}'", 
            font=("Arial", 13), 
            text_color="#7f8c8d",
            justify="center"
        )
        self.lbl_info.pack(pady=(0, 15))
        
        # Campo: Nueva Contraseña
        self.lbl_pass = ctk.CTkLabel(self.body, text="Nueva Contraseña", font=("Arial", 14, "bold"), text_color="#34495e")
        self.lbl_pass.pack(anchor="w", pady=(0, 5))
        self.entry_pass = ctk.CTkEntry(
            self.body, placeholder_text="Escribe aquí...", show="*",
            height=45, corner_radius=8, font=("Arial", 14), border_width=2
        )
        self.entry_pass.pack(fill="x")
        self.entry_pass.focus()
        
        # 3. FOOTER
        self.footer = ctk.CTkFrame(self.container, fg_color="#f8f9fa", height=55, corner_radius=10)
        self.footer.pack(fill="x", side="bottom")
        self.footer.pack_propagate(False)
        
        self.btn_aceptar = ctk.CTkButton(
            self.footer, text="Cambiar", 
            fg_color="#186ccf", hover_color="#186ccf",
            width=100, height=35, corner_radius=8,
            command=self.save_password
        )
        self.btn_aceptar.pack(side="right", padx=(0, 30), pady=(5, 10))

        self.btn_cancelar = ctk.CTkButton(
            self.footer, text="Cancelar", 
            fg_color="#F25838", hover_color="#F25838",
            width=90, height=35, corner_radius=8,
            command=self.close_modal
        )
        self.btn_cancelar.pack(side="right", padx=10, pady=(5, 10))

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

    def save_password(self):
        nuevo_pass = self.entry_pass.get().strip()
        
        if not nuevo_pass:
            Alerts.show_error("Campo requerido", "Debes ingresar una nueva contraseña.", master=self)
            return
            
        if len(nuevo_pass) < 4:
            Alerts.show_warning("Contraseña muy corta", "La contraseña debe tener al menos 4 caracteres.", master=self)
            return

        if UsuarioService.reset_password(self.user_id, nuevo_pass):
            Alerts.show_success("¡Éxito!", f"La contraseña de '{self.username}' ha sido actualizada.", master=self)
            self.close_modal()
        else:
            Alerts.show_error("Error", "No se pudo actualizar la contraseña.", master=self)
