import customtkinter as ctk
from interfaces.components.mensajes import Alerts
from PIL import Image
import os

class DashboardWindow(ctk.CTkToplevel):
    def __init__(self, master=None, usuario=None):
        super().__init__(master)
        
        # Al cerrar la ventana desde la X cerramos completamente la app (Login incluido)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Para probar el inicio de sesion del usuario
        self.usuario = usuario if usuario else {"nombre": "Administrador", "rol": 1}
        
        self.title("Sistema de Laboratorio")
        self.geometry("1420x730")
        self.center_window(1420, 730)
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

        self.lbl_logo = ctk.CTkLabel(self.logo_frame, text="Sistema de Laboratorio", font=("Arial", 18, "bold"), text_color="white")
        self.lbl_logo.pack(side="left")

        # --- MENÚS (Centro) ---
        self.menu_frame = ctk.CTkFrame(self.navbar, fg_color="transparent")
        self.menu_frame.grid(row=0, column=1, pady=10)
        
        menu_items = ["Inicio", "Inventario", "Préstamos", "Reportes"]
        self.nav_buttons = {}
        
        for item in menu_items:
            btn = ctk.CTkButton(
                self.menu_frame, text=item, 
                width=120, height=40, corner_radius=20,
                fg_color="transparent", hover_color="#145cb3", text_color="white",
                font=("Arial", 14, "bold"),
                command=lambda name=item: self.switch_view(name)
            )
            btn.pack(side="left", padx=10)
            self.nav_buttons[item] = btn

        # --- PERFIL Y LOGOUT ---
        self.profile_frame = ctk.CTkFrame(self.navbar, fg_color="transparent")
        self.profile_frame.grid(row=0, column=2, sticky="e", padx=20, pady=10)
        
        self.lbl_user = ctk.CTkLabel(self.profile_frame, text=f"Hola, {self.usuario['nombre']}", font=("Arial", 14), text_color="white")
        self.lbl_user.pack(side="left", padx=(0, 15))
        
        self.btn_logout = ctk.CTkButton(
            self.profile_frame, text="Cerrar Sesión", width=120, height=35,
            fg_color="#e74c3c", hover_color="#c0392b", corner_radius=15,
            font=("Arial", 12, "bold"), command=self.logout
        )
        self.btn_logout.pack(side="left")

        # ==========================================
        # 2. CONTENEDOR PRINCIPAL DE VISTAS
        # ==========================================
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        
        # Inicializar diccionario de vistas
        self.views = {}
        self.create_views()
        
        # Iniciar en la pestaña "Inicio"
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
        # 1. Vista INICIO
        dash_frame = ctk.CTkFrame(self.main_content, fg_color="white", corner_radius=15)
        ctk.CTkLabel(dash_frame, text="Vista General del Sistema", font=("Arial", 28, "bold"), text_color="#2c3e50").pack(pady=40)
        self.views["Inicio"] = dash_frame
        
        # 2. Vista INVENTARIO
        inv_frame = ctk.CTkFrame(self.main_content, fg_color="white", corner_radius=15)
        ctk.CTkLabel(inv_frame, text="Gestión de Instrumentos (CRUD)", font=("Arial", 28, "bold"), text_color="#2c3e50").pack(pady=40)
        self.views["Inventario"] = inv_frame
        
        # 3. Vista PRÉSTAMOS
        pres_frame = ctk.CTkFrame(self.main_content, fg_color="white", corner_radius=15)
        ctk.CTkLabel(pres_frame, text="Módulo de Préstamos y Devoluciones", font=("Arial", 28, "bold"), text_color="#2c3e50").pack(pady=40)
        self.views["Préstamos"] = pres_frame
        
        # 4. Vista REPORTES
        rep_frame = ctk.CTkFrame(self.main_content, fg_color="white", corner_radius=15)
        ctk.CTkLabel(rep_frame, text="Analíticas y Reportes", font=("Arial", 28, "bold"), text_color="#2c3e50").pack(pady=40)
        self.views["Reportes"] = rep_frame

    def switch_view(self, view_name):
        """Cambia el contenido de la pantalla y resalta el botón activo en la Navbar."""
        # Ocultar todos los frames actuales
        for frame in self.views.values():
            frame.pack_forget()
            
        # Restablecer botones a transparentes
        for btn in self.nav_buttons.values():
            btn.configure(fg_color="transparent")
            
        # Mostrar la vista elegida ocupando todo el espacio
        self.views[view_name].pack(fill="both", expand=True)
        
        # Resaltar botón presionado (color azul más oscuro)
        self.nav_buttons[view_name].configure(fg_color="#0d47a1")

    def logout(self):
        """Efectúa el cierre de sesión."""
        Alerts.show_success("Sesión Cerrada", "Has cerrado sesión correctamente.", master=self)
        self.destroy()
        if self.master:
            self.master.deiconify() # Muestra la ventana de Login de nuevo

    def on_closing(self):
        """Cierra la aplicación por completo."""
        self.destroy()
        if self.master:
            self.master.destroy()
        
if __name__ == "__main__":
    app = ctk.CTk()
    app.withdraw() # Oculta la base
    win = DashboardWindow(master=app)
    app.mainloop()
