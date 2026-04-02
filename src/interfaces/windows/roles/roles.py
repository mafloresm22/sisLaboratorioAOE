import customtkinter as ctk
from PIL import Image
import os
from interfaces.windows.roles.create_roles import CreateRoleModal
from interfaces.windows.roles.edit_roles import EditRoleModal
from interfaces.windows.roles.delete_roles import DeleteRoleModal
from services.Roles.roles import RoleService

class SmallBox(ctk.CTkFrame):
    """Tarjeta de Rol estilizada (versión compacta con acciones)."""
    def __init__(self, master, title, icon_path, bg_color, hover_color, on_edit=None, on_delete=None):
        super().__init__(master, fg_color=bg_color, corner_radius=15, height=140)
        self.pack_propagate(False)
        
        # --- Contenido superior ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=15, pady=(15, 0))
        
        # Título del Rol
        self.lbl_title = ctk.CTkLabel(self.header_frame, text=title, font=("Arial", 18, "bold"), text_color="white")
        self.lbl_title.pack(side="left")
        
        # --- Footer con Botones de Acción CIRCULARES ---
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

        try:
            pil_img = Image.open(icon_path)
            ctk_img = ctk.CTkImage(light_image=pil_img, size=(70, 70))
            self.lbl_icon = ctk.CTkLabel(self, image=ctk_img, text="")
        except Exception:
            self.lbl_icon = ctk.CTkLabel(self, font=("Segoe UI Emoji", 80), text_color="#ffffff")
            
        self.lbl_icon.place(relx=0.88, rely=0.35, anchor="center")

class RolesFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="white", corner_radius=15)
        
        # Configurar grilla: 
        # Columna 0: Tabla de Roles (80%)
        # Columna 1: Línea vertical (1px)
        # Columna 2: Estadísticas (20%)
        self.grid_columnconfigure(0, weight=4)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ==========================================
        # 1. SECCIÓN IZQUIERDA: LISTADO DE ROLES
        # ==========================================
        self.left_container = ctk.CTkFrame(self, fg_color="transparent")
        self.left_container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Título de la sección
        self.lbl_title = ctk.CTkLabel(
            self.left_container, 
            text="Administración de Roles", 
            font=("Arial", 28, "bold"), 
            text_color="#2c3e50"
        )
        self.lbl_title.pack(pady=(0, 20), anchor="w")
        
        # Contenedor de cards (Scrolleable si hay muchos roles)
        self.cards_scroll = ctk.CTkScrollableFrame(self.left_container, fg_color="transparent")
        self.cards_scroll.pack(fill="both", expand=True)
        
        self.cards_scroll.grid_columnconfigure((0, 1, 2), weight=1)
        self.load_role_cards()

        # ==========================================
        # 2. SEPARADOR VERTICAL
        # ==========================================
        self.separator = ctk.CTkFrame(self, fg_color="#e0e0e0", width=2)
        self.separator.grid(row=0, column=1, sticky="ns", pady=40)

        # ==========================================
        # 3. SECCIÓN DERECHA: ESTADÍSTICAS
        # ==========================================
        self.right_container = ctk.CTkFrame(self, fg_color="transparent")
        self.right_container.grid(row=0, column=2, sticky="nsew", padx=20, pady=20)
        
        # --- BOTÓN AGREGAR ROL ---
        self.btn_add_role = ctk.CTkButton(
            self.right_container, 
            text="➕ Agregar Nuevo Rol", 
            font=("Arial", 16, "bold"),
            fg_color="#186ccf",
            hover_color="#145cb3",
            height=50,
            corner_radius=10,
            command=self.on_add_role
        )
        self.btn_add_role.pack(fill="x", pady=(0, 30))

        # --- ESTADÍSTICAS ---
        self.lbl_stats_title = ctk.CTkLabel(
            self.right_container, 
            text="Resumen de Roles", 
            font=("Arial", 20, "bold"), 
            text_color="#2c3e50"
        )
        self.lbl_stats_title.pack(pady=(0, 15), anchor="w")
        
        self.load_statistics()

    def on_add_role(self):
        modal = CreateRoleModal(self.winfo_toplevel(), parent_view=self)

    def on_edit_role(self, role):
        modal = EditRoleModal(self.winfo_toplevel(), role_data=role, parent_view=self)

    def on_delete_role(self, role):
        modal = DeleteRoleModal(self.winfo_toplevel(), role_data=role, parent_view=self)

    def load_role_cards(self):
        for child in self.cards_scroll.winfo_children():
            child.destroy()
            
        roles = RoleService.get_all_roles()
        
        if not roles:
            # UI DE ESTADO VACÍO (No hay roles registrados)
            empty_container = ctk.CTkFrame(self.cards_scroll, fg_color="transparent")
            empty_container.pack(fill="both", expand=True, pady=100)
            
            # Icono grande de "vacio" o "sin datos"
            lbl_empty_icon = ctk.CTkLabel(
                empty_container, 
                text="👥", 
                font=("Arial", 120), 
                text_color="#d0d0d0"
            )
            lbl_empty_icon.pack()
            
            # Texto Informativo
            lbl_empty_text = ctk.CTkLabel(
                empty_container, 
                text="No hay Roles registrados", 
                font=("Arial", 22, "bold"), 
                text_color="#95a5a6"
            )
            lbl_empty_text.pack(pady=20)
            
            # Subtexto descriptivo
            lbl_hint = ctk.CTkLabel(
                empty_container, 
                text="Haz clic en 'Agregar Nuevo Rol' para comenzar", 
                font=("Arial", 14), 
                text_color="#bdc3c7"
            )
            lbl_hint.pack()
        else:
            # Si hay roles, los mostramos como SmallBox
            # Paleta de colores y mapeo de iconos profesionales
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
            icons_dir = os.path.join(base_dir, "assets", "icons", "roles_img")
            
            colors = [
                ("#17a2b8", "#138496", os.path.join(icons_dir, "13808994.png")), 
                ("#28a745", "#218838", os.path.join(icons_dir, "2770460.png")),
                ("#ffc107", "#e0a800", os.path.join(icons_dir, "3471381.png")),
                ("#dc3545", "#c82333", os.path.join(icons_dir, "5403817.png")),
                ("#6f42c1", "#59359a", os.path.join(icons_dir, "13030278.png"))
            ]
            
            for i, role in enumerate(roles):
                row = i // 3
                col = i % 3
                
                color_config = colors[i % len(colors)]
                
                card = SmallBox(
                    self.cards_scroll,
                    title=role["nombreRol"],
                    icon_path=color_config[2],
                    bg_color=color_config[0],
                    hover_color=color_config[1],
                    on_edit=lambda r=role: self.on_edit_role(r),
                    on_delete=lambda r=role: self.on_delete_role(r)
                )
                card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

    def load_statistics(self):
        # Limpiar estadísticas actuales
        for child in self.right_container.winfo_children():
            if isinstance(child, ctk.CTkFrame) and not child == self.btn_add_role:
                 if hasattr(child, 'is_stat') and child.is_stat:
                    child.destroy()

        stats_data = RoleService.get_role_statistics()
        
        # Stats components
        stats = [
            {"label": "Total Roles", "value": str(stats_data['total_roles']), "icon": "📋", "color": "#186ccf"},
            {"label": "Permisos Activos", "value": str(stats_data['active_permissions_count']), "icon": "✅", "color": "#28a745"},
            {"label": "Usuarios Sin Rol", "value": str(stats_data['users_without_role']), "icon": "⚠️", "color": "#ffc107"},
        ]
        
        for stat in stats:
            stat_card = ctk.CTkFrame(self.right_container, fg_color="#f8f9fa", border_width=1, border_color="#e0e0e0", corner_radius=10)
            stat_card.pack(fill="x", pady=10)
            stat_card.is_stat = True
            
            # Icono a la izquierda
            lbl_ico = ctk.CTkLabel(stat_card, text=stat["icon"], font=("Arial", 28))
            lbl_ico.pack(side="left", padx=15, pady=15)
            
            # Texto a la derecha
            text_frame = ctk.CTkFrame(stat_card, fg_color="transparent")
            text_frame.pack(side="left", fill="both", expand=True)
            
            lbl_val = ctk.CTkLabel(text_frame, text=stat["value"], font=("Arial", 20, "bold"), text_color=stat["color"])
            lbl_val.pack(anchor="w", pady=(5, 0))
            
            lbl_lab = ctk.CTkLabel(text_frame, text=stat["label"], font=("Arial", 12), text_color="#7f8c8d")
            lbl_lab.pack(anchor="w", pady=(0, 5))
