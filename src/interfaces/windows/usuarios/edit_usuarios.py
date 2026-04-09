import customtkinter as ctk
from services.usuarios.usuarios import UsuarioService
from services.Roles.roles import RoleService
from interfaces.components.mensajes import Alerts

class EditUsuarioModal(ctk.CTkToplevel):
    def __init__(self, master, user_data, parent_view=None, **kwargs):
        super().__init__(master, **kwargs)
        self.withdraw()
        self.parent_view = parent_view
        
        # Datos iniciales del usuario
        self.user_id = user_data.idUsuarios
        self.old_nombre = user_data.nombreUsuarios
        self.old_nombres = user_data.nombresCompletosUsuarios
        self.old_apellidos = user_data.apellidosCompletosUsuarios
        self.old_rol_id = user_data.rolId
        self.old_rol_nombre = user_data.nombreRol
        
        # Cargar roles para el combo
        self.roles = RoleService.get_all_roles()
        self.roles_map = {r.nombreRol: r.idRol for r in self.roles}
        self.role_options = list(self.roles_map.keys()) if self.roles_map else ["Sin Roles Disponibles"]
        
        # --- CAPA DE OPACIDAD (OVERLAY) ---
        self.overlay = ctk.CTkToplevel(self.master)
        self.overlay.withdraw()
        self.overlay.geometry(f"{self.overlay.winfo_screenwidth()}x{self.overlay.winfo_screenheight()}+0+0")
        self.overlay.overrideredirect(True)
        self.overlay.configure(fg_color="black")
        self.overlay.attributes("-alpha", 0.5)
        
        # --- MODAL CONFIG ---
        self.overrideredirect(True)
        self.width = 500
        self.height = 480
        
        # Centrar el modal en pantalla
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
        
        self.lbl_title = ctk.CTkLabel(self.header, text="Editar Usuario", font=("Arial", 18, "bold"), text_color="white")
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
        self.body.pack(fill="both", expand=True, padx=40, pady=(20, 5))
        
        # Campo: Nombre
        self.lbl_nombre = ctk.CTkLabel(self.body, text="Nombre de Usuario", font=("Arial", 14, "bold"), text_color="#34495e")
        self.lbl_nombre.pack(anchor="w", pady=(0, 5))
        self.entry_nombre = ctk.CTkEntry(
            self.body, height=45, corner_radius=8, font=("Arial", 14), border_width=2
        )
        self.entry_nombre.pack(fill="x", pady=(0, 15))
        self.entry_nombre.insert(0, self.old_nombre)

        # Campos: Nombres y Apellidos
        self.row_names = ctk.CTkFrame(self.body, fg_color="transparent")
        self.row_names.pack(fill="x", pady=(0, 15))
        self.row_names.grid_columnconfigure((0, 1), weight=1)

        # Nombres
        self.col_nombres = ctk.CTkFrame(self.row_names, fg_color="transparent")
        self.col_nombres.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        ctk.CTkLabel(self.col_nombres, text="Nombres", font=("Arial", 14, "bold"), text_color="#34495e").pack(anchor="w", pady=(0, 5))
        self.entry_nombres = ctk.CTkEntry(self.col_nombres, height=45, corner_radius=8, font=("Arial", 14), border_width=2)
        self.entry_nombres.pack(fill="x")
        self.entry_nombres.insert(0, self.old_nombres or "")

        # Apellidos
        self.col_apellidos = ctk.CTkFrame(self.row_names, fg_color="transparent")
        self.col_apellidos.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        ctk.CTkLabel(self.col_apellidos, text="Apellidos", font=("Arial", 14, "bold"), text_color="#34495e").pack(anchor="w", pady=(0, 5))
        self.entry_apellidos = ctk.CTkEntry(self.col_apellidos, height=45, corner_radius=8, font=("Arial", 14), border_width=2)
        self.entry_apellidos.pack(fill="x")
        self.entry_apellidos.insert(0, self.old_apellidos or "")
        
        # Campo: Rol
        self.lbl_rol = ctk.CTkLabel(self.body, text="Rol del Usuario", font=("Arial", 14, "bold"), text_color="#34495e")
        self.lbl_rol.pack(anchor="w", pady=(0, 5))
        
        # Validar si el rol actual existe en las opciones, si no usar el de por defecto
        current_role_val = self.old_rol_nombre if self.old_rol_nombre in self.role_options else self.role_options[0]
        self.role_var = ctk.StringVar(value=current_role_val)
        
        self.menu_rol = ctk.CTkComboBox(
            self.body, values=self.role_options, variable=self.role_var,
            height=45, corner_radius=8, font=("Arial", 14), border_width=2,
            fg_color="white", border_color="#d0d0d0", 
            button_color="#186ccf", button_hover_color="#145cb3",
            dropdown_fg_color="white", dropdown_text_color="#2c3e50",
            dropdown_hover_color="#f0f0f0", dropdown_font=("Arial", 14),
            state="readonly"
        )
        self.menu_rol.pack(fill="x")
        
        # 3. FOOTER
        self.footer = ctk.CTkFrame(self.container, fg_color="#f8f9fa", height=55, corner_radius=10)
        self.footer.pack(fill="x", side="bottom")
        self.footer.pack_propagate(False)
        
        self.btn_aceptar = ctk.CTkButton(
            self.footer, text="Actualizar", 
            fg_color="#f39c12", hover_color="#e67e22",
            width=110, height=35, corner_radius=8,
            command=self.update_usuario
        )
        self.btn_aceptar.pack(side="right", padx=(0, 30), pady=(5, 10))

        self.btn_cancelar = ctk.CTkButton(
            self.footer, text="Cancelar", 
            fg_color="#F25838", hover_color="#F25838",
            width=100, height=35, corner_radius=8,
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

    def update_usuario(self):
        nuevo_nombre = self.entry_nombre.get().strip()
        nuevos_nombres = self.entry_nombres.get().strip()
        nuevos_apellidos = self.entry_apellidos.get().strip()
        nuevo_rol_nombre = self.role_var.get()
        
        if not nuevo_nombre or not nuevos_nombres or not nuevos_apellidos:
            Alerts.show_error("Campo requerido", "Todos los campos son obligatorios.", master=self)
            return
            
        nuevo_rol_id = self.roles_map.get(nuevo_rol_nombre)
        
        # Verificar si hubo cambios
        if (nuevo_nombre == self.old_nombre and 
            nuevos_nombres == self.old_nombres and 
            nuevos_apellidos == self.old_apellidos and 
            nuevo_rol_id == self.old_rol_id):
            self.close_modal()
            return

        resultado = UsuarioService.update_usuario(self.user_id, nuevo_nombre, nuevo_rol_id, nuevos_nombres, nuevos_apellidos)
        
        if resultado == "exists":
            Alerts.show_warning("Ya existe", f"El nombre '{nuevo_nombre}' ya está siendo usado por otro usuario.", master=self)
        elif resultado:
            Alerts.show_success("Éxito", "Usuario actualizado correctamente.", master=self)
            if self.parent_view:
                self.parent_view.load_user_cards()
                self.parent_view.load_statistics()
            self.close_modal()
        else:
            Alerts.show_error("Error", "No se pudo actualizar el usuario.", master=self)
