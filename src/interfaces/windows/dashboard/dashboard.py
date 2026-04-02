import customtkinter as ctk
from interfaces.components.mensajes import Alerts
from PIL import Image
import os
from interfaces.windows.roles.roles import RolesFrame
from interfaces.windows.unidad.unidad import UnidadFrame

class ModuleCard(ctk.CTkFrame):
    def __init__(self, master, title, icon_path, description, command, color="#186ccf", bg_color="#ffffff", extra_padx=0):
        super().__init__(master, fg_color=bg_color, border_width=1, border_color="#e0e0e0", corner_radius=15, cursor="hand2")
        self.command = command
        self.accent_color = color
        self.base_bg = bg_color
        
        try:
            pil_img = Image.open(icon_path)
            ctk_img = ctk.CTkImage(light_image=pil_img, size=(60, 60))
            self.lbl_icon = ctk.CTkLabel(self, image=ctk_img, text="")
        except Exception:
            self.lbl_icon = ctk.CTkLabel(self, text="📦", font=("Arial", 48))
            
        self.lbl_icon.pack(pady=(25, 5), padx=(extra_padx, 0))
        
        # Titulo
        self.lbl_title = ctk.CTkLabel(self, text=title, font=("Arial", 18, "bold"), text_color=self.accent_color)
        self.lbl_title.pack(pady=5)
        
        # Descripcion
        self.lbl_desc = ctk.CTkLabel(self, text=description, font=("Arial", 12), text_color="#7f8c8d")
        self.lbl_desc.pack(pady=(0, 25), padx=20)
        
        # Eventos para animar la tarjeta al pasar el mouse
        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.off_hover)
        self.bind("<Button-1>", lambda e: self.command())
        
        # Propagar eventos de los hijos hacia el padre para que toda la tarjeta sea clickable
        for child in self.winfo_children():
            child.bind("<Enter>", self.on_hover)
            child.bind("<Leave>", self.off_hover)
            child.bind("<Button-1>", lambda e: self.command())

    def on_hover(self, event=None):
        self.configure(fg_color="#ffffff", border_color=self.accent_color, border_width=2)
        
    def off_hover(self, event=None):
        self.configure(fg_color=self.base_bg, border_color="#e0e0e0", border_width=1)

class DashboardWindow(ctk.CTkToplevel):
    def __init__(self, master=None, usuario=None):
        super().__init__(master)
        self.views = {} # Inicializar temprano para evitar AttributeError en callbacks
        
        # Para probar el inicio de sesion del usuario de acuerdo al esquema DB
        self.usuario = usuario if usuario else {"nombreUsuarios": "Administrador", "rolId": 1, "nombreRol": "Administrador"}
        
        self.title("Sistema de Laboratorio")
        self.geometry("1470x765")
        self.center_window(1470, 765)
        self.configure(fg_color="#f0f2f5")

        # Configurar grilla base: Fila 0 para navbar, Fila 1 para contenido
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # ==========================================
        # 1. NAVBAR SUPERIOR (MENÚS HORIZONTALES)
        # ==========================================
        self.navbar = ctk.CTkFrame(self, fg_color="#186ccf", corner_radius=0, height=70)
        self.navbar.grid(row=0, column=0, sticky="ew")
        
        # Configuración de 3 columnas para la Navbar
        self.navbar.grid_columnconfigure(0, weight=1) # Logo (izquierda)
        self.navbar.grid_columnconfigure(1, weight=3) # Botones (centro)
        self.navbar.grid_columnconfigure(2, weight=1) # Perfil (derecha)
        
        # --- LOGO ---
        self.logo_frame = ctk.CTkFrame(self.navbar, fg_color="transparent")
        self.logo_frame.grid(row=0, column=0, sticky="w", padx=20, pady=10)

        # Cargar imagen del logo AOE
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
        img_path_aoe = os.path.join(base_dir, "assets", "img", "AOE_img.jpeg")
        
        try:
            logo_img = ctk.CTkImage(light_image=Image.open(img_path_aoe), size=(40, 40))
            self.lbl_logo_img = ctk.CTkLabel(self.logo_frame, image=logo_img, text="")
            self.lbl_logo_img.pack(side="left", padx=(0, 10))
        except Exception:
            pass

        self.lbl_logo = ctk.CTkLabel(self.logo_frame, text="Sistema de Laboratorio", font=("Arial", 18, "bold"), text_color="white", cursor="hand2")
        self.lbl_logo.pack(side="left")
        self.lbl_logo.bind("<Button-1>", lambda e: self.switch_view("Inicio"))
        
        # Permitir que el logo de imagen también sea clickable
        if hasattr(self, 'lbl_logo_img'):
            self.lbl_logo_img.configure(cursor="hand2")
            self.lbl_logo_img.bind("<Button-1>", lambda e: self.switch_view("Inicio"))

        # --- MENÚS (Centro) ---
        self.menu_frame = ctk.CTkFrame(self.navbar, fg_color="transparent")
        self.menu_frame.grid(row=0, column=1, pady=10)
        
        # DEFINICIÓN DE MENÚS Y SUBMENÚS CON ICONOS
        self.menu_items = {
            "Módulos": ["Roles", "Unidad", "Laboratorios", "E.Conservación"],
            "Usuarios": None,
            "Inventario": None,
            "Préstamos": None,
            "Reportes": None
        }
        
        # Mapeo de iconos para la Navbar
        icons_dir = os.path.join(base_dir, "assets", "icons", "dashboard")
        self.menu_icons = {
            "Módulos": os.path.join(icons_dir, "13051347_roles.png"),
            "Usuarios": os.path.join(icons_dir, "7816987_usuario.png"),
            "Inventario": os.path.join(icons_dir, "11458663_inventario.png"),
            "Préstamos": os.path.join(icons_dir, "772938_prestamo.png"),
            "Reportes": os.path.join(icons_dir, "8916436_Reportes.png")
        }
        
        self.nav_buttons = {}
        for item, sub_items in self.menu_items.items():
            # Intentar cargar icono para el botón
            try:
                path = self.menu_icons.get(item)
                icon_img = ctk.CTkImage(light_image=Image.open(path), size=(20, 20)) if path else None
            except:
                icon_img = None
                
            if sub_items:
                btn = ctk.CTkOptionMenu(
                    self.menu_frame, 
                    values=[item] + sub_items,
                    width=210, height=45, corner_radius=22,
                    fg_color="#145cb3", button_color="#104e9a",
                    button_hover_color="#0d47a1", dropdown_fg_color="#186ccf",
                    dropdown_hover_color="#0d47a1", dropdown_text_color="white",
                    dropdown_font=("Arial", 13, "bold"),
                    font=("Arial", 14, "bold"),
                    command=lambda val, name=item: self.handle_nav_click(val, name)
                )
                btn.set(item)
            else:
                btn = ctk.CTkButton(
                    self.menu_frame, text=f" {item}", image=icon_img, compound="left",
                    width=135, height=45, corner_radius=22,
                    fg_color="transparent", hover_color="#145cb3", text_color="white",
                    font=("Arial", 14, "bold"),
                    command=lambda name=item: self.switch_view(name)
                )
            
            btn.pack(side="left", padx=8)
            self.nav_buttons[item] = btn

        # --- PERFIL Y LOGOUT ---
        self.profile_frame = ctk.CTkFrame(self.navbar, fg_color="transparent")
        self.profile_frame.grid(row=0, column=2, sticky="e", padx=20, pady=10)
        
        # Cargar Avatar del Usuario
        img_path_user = os.path.join(base_dir, "assets", "img", "user_552721.png")
        try:
            image_user = Image.open(img_path_user)
            user_avatar = ctk.CTkImage(light_image=image_user, size=(32, 32))
            self.lbl_avatar = ctk.CTkLabel(self.profile_frame, image=user_avatar, text="")
            self.lbl_avatar.pack(side="left", padx=(0, 10))
        except Exception:
            pass

        # Contenedor para Nombre y Rol
        self.user_info_frame = ctk.CTkFrame(self.profile_frame, fg_color="transparent")
        self.user_info_frame.pack(side="left", padx=(0, 8))

        self.lbl_user_name = ctk.CTkLabel(self.user_info_frame, text=self.usuario.get('nombreUsuarios', 'Usuario'), font=("Arial", 14, "bold"), text_color="white", height=20)
        self.lbl_user_name.pack(anchor="w", pady=(0, 0))
        
        rol_display = self.usuario.get('nombreRol', 'Sin Rol')
        
        self.lbl_user_role = ctk.CTkLabel(self.user_info_frame, text=rol_display, font=("Arial", 11), text_color="#d1d1d1", height=12)
        self.lbl_user_role.pack(anchor="w", pady=0)
        
        # Botón de Cerrar Sesión (Icono de Power)
        img_path_power = os.path.join(base_dir, "assets", "img", "power-button_9734668.png")
        try:
            image_power = Image.open(img_path_power)
            power_icon = ctk.CTkImage(light_image=image_power, size=(24, 24))
            self.btn_logout = ctk.CTkButton(
                self.profile_frame, image=power_icon, text="", 
                width=45, height=45, corner_radius=12,
                fg_color="#e74c3c", hover_color="#c0392b",
                command=self.logout
            )
        except Exception:
            # Fallback por si falla la carga de imagen
            self.btn_logout = ctk.CTkButton(
                self.profile_frame, text="X", 
                width=45, height=45, corner_radius=12,
                fg_color="#e74c3c", hover_color="#c0392b",
                command=self.logout
            )
        self.btn_logout.pack(side="left", padx=(5, 0))

        # ==========================================
        # 2. CONTENEDOR PRINCIPAL DE VISTAS
        # ==========================================
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        
        self.create_views()
        
        # Iniciar en la pestaña "Inicio" al cargar el sistema
        self.update() 
        self.switch_view("Inicio")

    def center_window(self, width, height):
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = ((screen_height // 2) - (height // 2)) - 40
        self.geometry(f"{width}x{height}+{x}+{y}")

    def create_views(self):
        """Crea los marcos de contenido para cada opción del menú."""
        # --- 1. Vista INICIO ---
        dash_frame = ctk.CTkFrame(self.main_content, fg_color="white", corner_radius=15)
        ctk.CTkLabel(dash_frame, text="Vista General del Sistema", font=("Arial", 28, "bold"), text_color="#2c3e50").pack(pady=40)
        self.views["Inicio"] = dash_frame
        
        # --- 2. Vista MÓDULOS (Dashboard de Categorías) ---
        mod_frame = ctk.CTkFrame(self.main_content, fg_color="white", corner_radius=15)
        ctk.CTkLabel(mod_frame, text="Gestión de Catálogos / Módulos", font=("Arial", 28, "bold"), text_color="#2c3e50").pack(pady=20)
        
        cards_container = ctk.CTkFrame(mod_frame, fg_color="transparent")
        cards_container.pack(pady=20, padx=40, fill="both", expand=True)
        
        # Crear 4 tarjetas profesionales con iconos profesionales
        icons_dir = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")), "assets", "icons", "dashboard")
        
        module_submenus = {
            "Roles": (os.path.join(icons_dir, "13051347_roles.png"), "Gestión de permisos", "#1976d2", "#e3f2fd"), 
            "Unidad": (os.path.join(icons_dir, "8289236_unidad.png"), "Unidades de medida", "#2e7d32", "#e8f5e9"),
            "Laboratorios": (os.path.join(icons_dir, "7918318_laboratorio.png"), "Sedes y laboratorios", "#7b1fa2", "#f3e5f5"),
            "E.Conservación": (os.path.join(icons_dir, "13500912_estadoConservacion.png"), "Estados de equipos", "#ef6c00", "#fff3e0")
        }
        
        for i, (mod_name, data) in enumerate(module_submenus.items()):
            icon_path, desc_text, color, bg_c = data
            extra_px = 25 if mod_name == "E.Conservación" else 0
            
            card = ModuleCard(
                cards_container, 
                title=mod_name, 
                icon_path=icon_path, 
                description=desc_text,
                color=color,
                bg_color=bg_c,
                command=lambda m=mod_name: self.switch_view(m),
                extra_padx=extra_px
            )
            card.grid(row=0, column=i, padx=15, pady=20, sticky="nsew")
            cards_container.grid_columnconfigure(i, weight=1)
            
        self.views["Módulos"] = mod_frame

        # --- 3. SUB-VISTAS DE MÓDULOS ---
        for mod_name in module_submenus:
            if mod_name == "Roles":
                frame = RolesFrame(self.main_content)
            elif mod_name == "Unidad":
                frame = UnidadFrame(self.main_content)
            else:
                frame = ctk.CTkFrame(self.main_content, fg_color="white", corner_radius=15)
                ctk.CTkLabel(frame, text=f"Administración de {mod_name}", font=("Arial", 28, "bold"), text_color="#2c3e50").pack(pady=40)
            self.views[mod_name] = frame

        # --- 4. Vista USUARIOS ---
        user_frame = ctk.CTkFrame(self.main_content, fg_color="white", corner_radius=15)
        ctk.CTkLabel(user_frame, text="Administración de Usuarios", font=("Arial", 28, "bold"), text_color="#2c3e50").pack(pady=40)
        self.views["Usuarios"] = user_frame
        
        # --- 5. Vista INVENTARIO ---
        inv_frame = ctk.CTkFrame(self.main_content, fg_color="white", corner_radius=15)
        ctk.CTkLabel(inv_frame, text="Gestión de Instrumentos (CRUD)", font=("Arial", 28, "bold"), text_color="#2c3e50").pack(pady=40)
        self.views["Inventario"] = inv_frame
        
        # --- 6. Vista PRÉSTAMOS ---
        pres_frame = ctk.CTkFrame(self.main_content, fg_color="white", corner_radius=15)
        ctk.CTkLabel(pres_frame, text="Módulo de Préstamos y Devoluciones", font=("Arial", 28, "bold"), text_color="#2c3e50").pack(pady=40)
        self.views["Préstamos"] = pres_frame
        
        # --- 7. Vista REPORTES ---
        rep_frame = ctk.CTkFrame(self.main_content, fg_color="white", corner_radius=15)
        ctk.CTkLabel(rep_frame, text="Analíticas y Reportes", font=("Arial", 28, "bold"), text_color="#2c3e50").pack(pady=40)
        self.views["Reportes"] = rep_frame

    def handle_nav_click(self, val, parent_name):
        """Maneja el click en un OptionMenu"""
        if val == parent_name:
            self.switch_view(val)
        else:
            self.switch_view(val)

    def switch_view(self, view_name):
        """Cambia el contenido de la pantalla y resalta el botón activo en la Navbar."""
        if view_name not in self.views:
            return

        # Ocultar todos los frames actuales
        for frame in self.views.values():
            frame.pack_forget()
            
        # Restablecer botones y optionmenus
        for base_name, btn in self.nav_buttons.items():
            if isinstance(btn, ctk.CTkButton):
                btn.configure(fg_color="transparent")
            elif isinstance(btn, ctk.CTkOptionMenu):
                btn.configure(fg_color="#145cb3")
                for item_name, sub_list in self.menu_items.items():
                    if item_name == base_name and sub_list:
                        if view_name in sub_list:
                            btn.set(view_name)
                            btn.configure(fg_color="#0d47a1")
                        elif view_name == base_name:
                            btn.set(item_name)
                            btn.configure(fg_color="#0d47a1")
                        else:
                            btn.set(item_name)

        # Mostrar la vista elegida
        self.views[view_name].pack(fill="both", expand=True)
        
        # Resaltar si es un botón directo
        if view_name in self.nav_buttons and isinstance(self.nav_buttons[view_name], ctk.CTkButton):
            self.nav_buttons[view_name].configure(fg_color="#0d47a1")

    def logout(self):
        Alerts.show_success("Sesión Cerrada", "Has cerrado sesión correctamente.", master=self)
        self.destroy()
        if self.master:
            self.master.deiconify() # Me Lleva al Login

    def on_closing(self):
        self.destroy()
        if self.master:
            self.master.destroy()
        
if __name__ == "__main__":
    app = ctk.CTk()
    app.withdraw()
    win = DashboardWindow(master=app)
    app.mainloop()
