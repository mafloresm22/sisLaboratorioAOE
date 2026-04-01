import customtkinter as ctk
from PIL import Image
import os
from services.Roles.roles import RoleService
from interfaces.components.mensajes import Alerts

class CreateRoleModal(ctk.CTkToplevel):
    def __init__(self, master, parent_view=None, **kwargs):
        super().__init__(master, **kwargs)
        self.parent_view = parent_view
        
        # --- CAPA DE OPACIDAD (OVERLAY) ---
        self.overlay = ctk.CTkToplevel(self.master)
        self.overlay.geometry(f"{self.overlay.winfo_screenwidth()}x{self.overlay.winfo_screenheight()}+0+0")
        self.overlay.overrideredirect(True)
        self.overlay.configure(fg_color="black")
        self.overlay.attributes("-alpha", 0.5)
        
        # --- MODAL ---
        self.overrideredirect(True)
        self.width = 500
        self.height = 300
        
        # Centrar el modal en pantalla
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.target_x = (screen_width // 2) - (self.width // 2)
        self.target_y = (screen_height // 2) - (self.height // 2)
        
        # Parámetros para la animación
        self.current_y = self.target_y - 80 
        self.geometry(f"{self.width}x{self.height}+{self.target_x}+{int(self.current_y)}")
        self.configure(fg_color="white")
        
        # --- CONTENEDOR PRINCIPAL ---
        self.container = ctk.CTkFrame(self, fg_color="white", corner_radius=10, border_width=1, border_color="#e0e0e0")
        self.container.pack(fill="both", expand=True)
        
        # 1. HEADER
        self.header = ctk.CTkFrame(self.container, fg_color="#f8f9fa", height=50, corner_radius=10)
        self.header.pack(fill="x", side="top")
        self.header.pack_propagate(False)
        
        self.lbl_title = ctk.CTkLabel(self.header, text="Crear Nuevo Rol", font=("Arial", 18, "bold"), text_color="#2c3e50")
        self.lbl_title.pack(side="left", padx=20)
        
        self.btn_close = ctk.CTkButton(
            self.header, text="×", width=30, height=30, 
            fg_color="transparent", text_color="#95a5a6", 
            hover_color="#e74c3c", font=("Arial", 24),
            command=self.close_modal
        )
        self.btn_close.pack(side="right", padx=10)
        
        # 2. BODY
        self.body = ctk.CTkFrame(self.container, fg_color="white")
        self.body.pack(fill="both", expand=True, padx=30, pady=20)
        
        self.lbl_field = ctk.CTkLabel(self.body, text="Nombre del Rol", font=("Arial", 14, "bold"), text_color="#34495e")
        self.lbl_field.pack(anchor="w", pady=(0, 5))
        
        self.entry_nombre = ctk.CTkEntry(
            self.body, 
            placeholder_text="Ej: Administrador, Asistente, Docente...", 
            height=45, 
            corner_radius=8,
            font=("Arial", 14),
            border_width=2
        )
        self.entry_nombre.pack(fill="x")
        
        # 3. FOOTER
        self.footer = ctk.CTkFrame(self.container, fg_color="#f8f9fa", height=60, corner_radius=10)
        self.footer.pack(fill="x", side="bottom")
        self.footer.pack_propagate(False)
        
        self.btn_aceptar = ctk.CTkButton(
            self.footer, text="Aceptar", 
            fg_color="#186ccf", hover_color="#145cb3",
            width=100, height=35, corner_radius=8,
            command=self.save_role
        )
        self.btn_aceptar.pack(side="right", padx=(0, 30), pady=12)

        self.btn_cancelar = ctk.CTkButton(
            self.footer, text="Cancelar", 
            fg_color="#F25838", hover_color="#F25838",
            width=100, height=35, corner_radius=8,
            command=self.close_modal
        )
        self.btn_cancelar.pack(side="right", padx=10, pady=12)

        # Iniciar animación
        self.animate_entry()
        self.attributes("-topmost", True)
        self.grab_set()

    def animate_entry(self):
        """Animación de caída suave."""
        if self.current_y < self.target_y:
            # Movimiento exponencial para que sea suave
            distancia = self.target_y - self.current_y
            if distancia > 1:
                self.current_y += (distancia * 0.2) + 1
            else:
                self.current_y = self.target_y
                
            self.geometry(f"{self.width}x{self.height}+{self.target_x}+{int(self.current_y)}")
            self.after(10, self.animate_entry)

    def close_modal(self):
        self.grab_release()
        self.overlay.destroy()
        self.destroy()

    def save_role(self):
        nombre = self.entry_nombre.get().strip()
        if not nombre:
            Alerts.show_error("Campo requerido", "El nombre del rol es obligatorio.", master=self)
            return
        
        # Llamar al servicio para guardar en DB
        resultado = RoleService.create_role(nombre)
        
        if resultado == "exists":
            Alerts.show_warning("Ya existe", f"El rol '{nombre}' ya se encuentra registrado.", master=self)
        elif resultado:
            Alerts.show_success("Éxito", f"El rol '{nombre}' ha sido creado correctamente.", master=self)
            if self.parent_view:
                self.parent_view.load_role_cards()
                self.parent_view.load_statistics()
            self.close_modal()
        else:
            Alerts.show_error("Error", "No se pudo crear el rol en la base de datos.", master=self)
