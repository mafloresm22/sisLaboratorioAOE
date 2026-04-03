import customtkinter as ctk
from PIL import Image
import os
from services.usuarios.usuarios import UsuarioService
from interfaces.windows.usuarios.create_usuarios import CreateUsuarioModal
from interfaces.windows.usuarios.edit_usuarios import EditUsuarioModal
from interfaces.windows.usuarios.restablecer_password import RestablecerPasswordModal
from interfaces.windows.usuarios.delete_usuarios import DeleteUsuarioModal

class UserBox(ctk.CTkFrame):
    def __init__(self, master, username, role_name, icon_path, bg_color, hover_color, on_edit=None, on_delete=None, on_reset=None):
        is_admin = role_name.lower() == "administrador"
        
        if is_admin:
            bg_color = "#2482e0" 
            hover_color = "#54a2f0"
            
        super().__init__(master, fg_color=bg_color, corner_radius=15, height=140)
        self.pack_propagate(False)
        
        if is_admin:
            self.configure(border_width=3, border_color="#00d2ff")    

        # --- Contenido superior ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=15, pady=(15, 0))
        
        # Nombre de Usuario
        self.lbl_user = ctk.CTkLabel(self.header_frame, text=username, font=("Arial", 19, "bold"), text_color="white")
        self.lbl_user.pack(anchor="w")
        
        # Rol
        is_admin = role_name.lower() == "administrador"
        role_font = ("Arial", 15, "bold") if is_admin else ("Arial", 14)
        role_color = "#ffffff" if is_admin else "#e0e0e0"

        admin_img = None
        if is_admin:
            try:
                base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
                admin_icon_path = os.path.join(base_dir, "assets", "icons", "roles_img", "13808994.png")
                pil_admin = Image.open(admin_icon_path)
                admin_img = ctk.CTkImage(light_image=pil_admin, size=(20, 20))
            except Exception:
                pass

        if admin_img:
            self.lbl_role = ctk.CTkLabel(self.header_frame, text=f" {role_name}", image=admin_img, compound="left", font=role_font, text_color=role_color)
        else:
            self.lbl_role = ctk.CTkLabel(self.header_frame, text=role_name, font=role_font, text_color=role_color)

        self.lbl_role.pack(anchor="w", pady=(2, 0))
        
        # --- Footer con Botones de Acción ---
        self.actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.actions_frame.pack(side="bottom", fill="x", padx=12, pady=12)
        
        # Contenedor para alinear los botones a la derecha
        self.btn_container = ctk.CTkFrame(self.actions_frame, fg_color="transparent")
        self.btn_container.pack(side="right")
        
        # Botón Eliminar
        self.btn_delete = ctk.CTkButton(
            self.btn_container, text="🗑️", width=38, height=38, corner_radius=19,
            fg_color="#e74c3c", text_color="white", hover_color="#c0392b",
            font=("Segoe UI Emoji", 15), 
            command=on_delete,
            border_width=0
        )
        self.btn_delete.pack(side="right", padx=5)

        # Botón Editar
        self.btn_edit = ctk.CTkButton(
            self.btn_container, text="✏️", width=38, height=38, corner_radius=19,
            fg_color="#f39c12", text_color="white", hover_color="#e67e22",
            font=("Segoe UI Emoji", 15),
            command=on_edit,
            border_width=0
        )
        self.btn_edit.pack(side="right", padx=5)

        # Botón Restablecer password
        self.btn_reset = ctk.CTkButton(
            self.btn_container, text="🔄", width=38, height=38, corner_radius=19,
            fg_color="#1abc9c", text_color="white", hover_color="#16a085",
            font=("Segoe UI Emoji", 15),
            command=on_reset,
            border_width=0
        )
        self.btn_reset.pack(side="right", padx=5)

        try:
            pil_img = Image.open(icon_path)
            ctk_img = ctk.CTkImage(light_image=pil_img, size=(70, 70))
            self.lbl_icon = ctk.CTkLabel(self, image=ctk_img, text="")
        except Exception:
            # Fallback simple si no hay icono
            self.lbl_icon = ctk.CTkLabel(self, font=("Segoe UI Emoji", 80), text="👤", text_color="#ffffff")
            
        self.lbl_icon.place(relx=0.88, rely=0.35, anchor="center")

class UsuariosFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="white", corner_radius=15)
        
        # Grilla de 3 columnas (80% listado, 20% stats)
        self.grid_columnconfigure(0, weight=4)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ==========================================
        # 1. SECCIÓN IZQUIERDA: LISTADO DE USUARIOS
        # ==========================================
        self.left_container = ctk.CTkFrame(self, fg_color="transparent")
        self.left_container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        self.lbl_title = ctk.CTkLabel(
            self.left_container, 
            text="Administración de Usuarios", 
            font=("Arial", 28, "bold"), 
            text_color="#2c3e50"
        )
        self.lbl_title.pack(pady=(0, 20), anchor="w")
        
        # Scrolleable de usuarios
        self.cards_scroll = ctk.CTkScrollableFrame(self.left_container, fg_color="transparent")
        self.cards_scroll.pack(fill="both", expand=True)
        self.cards_scroll.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.load_user_cards()

        # Separador Vertical
        self.separator = ctk.CTkFrame(self, fg_color="#e0e0e0", width=2)
        self.separator.grid(row=0, column=1, sticky="ns", pady=40)

        # ==========================================
        # 2. SECCIÓN DERECHA: ESTADÍSTICAS
        # ==========================================
        self.right_container = ctk.CTkFrame(self, fg_color="transparent")
        self.right_container.grid(row=0, column=2, sticky="nsew", padx=20, pady=20)
        
        # Botón agregar usuario
        self.btn_add_user = ctk.CTkButton(
            self.right_container, 
            text="➕ Agregar Usuario", 
            font=("Arial", 16, "bold"),
            fg_color="#186ccf",
            hover_color="#145cb3",
            height=50,
            corner_radius=10,
            command=self.on_add_user
        )
        self.btn_add_user.pack(fill="x", pady=(0, 30))

        self.lbl_stats_title = ctk.CTkLabel(
            self.right_container, 
            text="Resumen de Usuarios", 
            font=("Arial", 20, "bold"), 
            text_color="#2c3e50"
        )
        self.lbl_stats_title.pack(pady=(0, 15), anchor="w")
        
        self.load_statistics()

    def on_add_user(self):
        modal = CreateUsuarioModal(self.winfo_toplevel(), parent_view=self)

    def on_edit_user(self, user):
        modal = EditUsuarioModal(self.winfo_toplevel(), user_data=user, parent_view=self)

    def on_delete_user(self, user):
        modal = DeleteUsuarioModal(self.winfo_toplevel(), user_data=user, parent_view=self)

    def on_reset_user(self, user):
        modal = RestablecerPasswordModal(self.winfo_toplevel(), user_data=user, parent_view=self)

    def load_user_cards(self):
        for child in self.cards_scroll.winfo_children():
            child.destroy()
            
        users = UsuarioService.get_all_usuarios()
        
        if not users:
            empty_container = ctk.CTkFrame(self.cards_scroll, fg_color="transparent")
            empty_container.pack(fill="both", expand=True, pady=100)
            lbl_empty_icon = ctk.CTkLabel(empty_container, text="👤", font=("Arial", 120), text_color="#d0d0d0")
            lbl_empty_icon.pack()
            lbl_empty_text = ctk.CTkLabel(empty_container, text="No hay Usuarios registrados", font=("Arial", 22, "bold"), text_color="#95a5a6")
            lbl_empty_text.pack(pady=20)
        else:
            icons_dir = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")), "assets", "icons", "dashboard")
            user_icon_path = os.path.join(icons_dir, "7816987_usuario.png")
            
            # Paleta de colores consistente con roles
            paleta = [
                ("#186ccf", "#145cb3"), 
                ("#2e7d32", "#26662a"),
                ("#ef6c00", "#d35400"),
                ("#7b1fa2", "#661b87"),
                ("#c62828", "#b02424")
            ]
            
            for i, user in enumerate(users):
                row = i // 3
                col = i % 3
                colors = paleta[i % len(paleta)]
                
                card = UserBox(
                    self.cards_scroll,
                    username=user.nombreUsuarios,
                    role_name=user.nombreRol,
                    icon_path=user_icon_path,
                    bg_color=colors[0],
                    hover_color=colors[1],
                    on_edit=lambda u=user: self.on_edit_user(u),
                    on_delete=lambda u=user: self.on_delete_user(u),
                    on_reset=lambda u=user: self.on_reset_user(u)
                )
                card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

    def load_statistics(self):
        for child in self.right_container.winfo_children():
            if isinstance(child, ctk.CTkFrame) and getattr(child, 'is_stat', False):
                child.destroy()

        stats_data = UsuarioService.get_usuario_statistics()
        
        # Rutas de iconos profesionales
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
        icons_dir = os.path.join(base_dir, "assets", "icons", "estadisticas")
        
        stats = [
            {"label": "Total Usuarios", "value": str(stats_data['total_usuarios']), "icon_path": os.path.join(icons_dir, "878516_usuarios.png"), "color": "#186ccf"},
            {"label": "Admins", "value": str(stats_data['administradores']), "icon_path": os.path.join(icons_dir, "1295888_Admin.png"), "color": "#28a745"},
            {"label": "Sin Rol", "value": str(stats_data['sin_rol']), "icon_path": os.path.join(icons_dir, "393640_SinRol.png"), "color": "#ffc107"},
        ]
        
        for stat in stats:
            stat_card = ctk.CTkFrame(self.right_container, fg_color="#f8f9fa", border_width=1, border_color="#e0e0e0", corner_radius=10)
            stat_card.pack(fill="x", pady=10)
            stat_card.is_stat = True
            
            # Cargar Icono PNG
            try:
                img = Image.open(stat["icon_path"])
                ctk_img = ctk.CTkImage(light_image=img, size=(32, 32))
                lbl_ico = ctk.CTkLabel(stat_card, image=ctk_img, text="")
            except:
                lbl_ico = ctk.CTkLabel(stat_card, text="📊", font=("Arial", 28))
                
            lbl_ico.pack(side="left", padx=15, pady=15)
            
            text_frame = ctk.CTkFrame(stat_card, fg_color="transparent")
            text_frame.pack(side="left", fill="both", expand=True)
            
            lbl_val = ctk.CTkLabel(text_frame, text=stat["value"], font=("Arial", 20, "bold"), text_color=stat["color"])
            lbl_val.pack(anchor="w", pady=(5, 0))
            
            lbl_lab = ctk.CTkLabel(text_frame, text=stat["label"], font=("Arial", 12), text_color="#7f8c8d")
            lbl_lab.pack(anchor="w", pady=(0, 5))
