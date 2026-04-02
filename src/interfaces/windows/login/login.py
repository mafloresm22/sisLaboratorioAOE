import customtkinter as ctk
from services.auth_service import AuthService
from tkinter import messagebox
from PIL import Image
from interfaces.components.mensajes import Alerts
from interfaces.windows.dashboard.dashboard import DashboardWindow
import os

class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistema de Laboratorio - Antenor Orrego Espinoza")
        
        # Centrar ventana en pantalla
        width = 1200
        height = 700
        self.center_window(width, height)
        
        self.resizable(True, True)
        self.configure(fg_color="#f0f2f5")

        # Centrar el contenedor principal
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- CONTENEDOR PRINCIPAL AZUL ---
        self.main_frame = ctk.CTkFrame(self, fg_color="#186ccf", corner_radius=0)
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

        # 1. Imagen del científico (Al fondo de los adornos)
        img_path_scientist = os.path.join(base_dir, "assets", "img", "innovative-scientist-explores-virtual-reality-in-cartoon-laboratory-engaging-educational-concepts-in-a-colorful-environment-free-png.png")
        try:
            scientist_img = ctk.CTkImage(light_image=Image.open(img_path_scientist), size=(500, 500))
            self.label_welcome = ctk.CTkLabel(self.main_frame, image=scientist_img, text="")
        except Exception:
            self.label_welcome = ctk.CTkLabel(self.main_frame, text="*Imagen de científico*", font=("Arial", 20), text_color="white")
        self.label_welcome.place(relx=0.35, rely=0.5, anchor="center")

        # 2. Círculos de adorno (Encima de la imagen)
        self.circle1 = ctk.CTkFrame(self.main_frame, fg_color="#2b7ae0", corner_radius=200, width=300, height=300)
        self.circle1.place(x=-100, y=300)
        self.circle2 = ctk.CTkFrame(self.main_frame, fg_color="#145cb3", corner_radius=200, width=385, height=385)
        self.circle2.place(x=-100, y=-200)

        # --- LADO DERECHO: TARJETA BLANCA ---
        self.login_card = ctk.CTkFrame(self.main_frame, fg_color="white", corner_radius=15, width=400, height=550)
        self.login_card.place(relx=1.5, rely=0.5, anchor="center")
        self.login_card.pack_propagate(False)

        self.label_signin = ctk.CTkLabel(self.login_card, text="Iniciar Sesión", font=("Arial", 32, "bold"), text_color="#113e75")
        self.label_signin.pack(pady=(30, 5))

        img_path_aoe = os.path.join(base_dir, "assets", "img", "AOE_img.jpeg")
        try:
            aoe_img = ctk.CTkImage(light_image=Image.open(img_path_aoe), size=(110, 110))
            self.label_aoe = ctk.CTkLabel(self.login_card, image=aoe_img, text="")
        except Exception:
            self.label_aoe = ctk.CTkLabel(self.login_card, text="*AOE*")
        self.label_aoe.pack(pady=(5, 15))

        self.entry_user = ctk.CTkEntry(self.login_card, placeholder_text="Nombre de Usuario", width=320, height=45, fg_color="white", border_color="#dce4ec", border_width=2, text_color="black", corner_radius=8)
        self.entry_user.pack(pady=10)

        self.entry_password = ctk.CTkEntry(self.login_card, placeholder_text="Contraseña", show="*", width=320, height=45, fg_color="white", border_color="#dce4ec", border_width=2, text_color="black", corner_radius=8)
        self.entry_password.pack(pady=(10, 0))

        # Checkbox para mostrar contraseña (grosor reducido)
        self.check_show_password = ctk.CTkCheckBox(self.login_card, text="Mostrar contraseña", command=self.toggle_password, font=("Arial", 11), text_color="gray", checkbox_width=16, checkbox_height=16, border_width=1)
        self.check_show_password.pack(pady=(5, 10), padx=(41, 0), anchor="w")

        self.btn_login = ctk.CTkButton(self.login_card, text="Ingresar", command=self.handle_login, width=280, height=45, font=("Arial", 14, "bold"), fg_color="#186ccf", hover_color="#145cb3", corner_radius=8)
        self.btn_login.pack(pady=(20, 10))

        self.target_x = 0.75
        self.current_x = 1.5
        self.animate_entry()

    def center_window(self, width, height):
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2) - 40
        self.geometry(f"{width}x{height}+{x}+{y}")

    def animate_entry(self):
        if self.current_x > self.target_x:
            self.current_x -= 0.04
            self.login_card.place(relx=self.current_x, rely=0.5, anchor="center")
            self.after(15, self.animate_entry)
        else:
            self.login_card.place(relx=self.target_x, rely=0.5, anchor="center")

    def toggle_password(self):
        if self.check_show_password.get() == 1:
            self.entry_password.configure(show="")
        else:
            self.entry_password.configure(show="*")

    def handle_login(self):
        user = self.entry_user.get()
        pw = self.entry_password.get()
        if not user or not pw:
            Alerts.show_warning("Campos vacíos", "Por favor completa usuario y contraseña.", master=self)
            return
        usuario_encontrado = AuthService.verificar_credenciales(user, pw)
        if usuario_encontrado:
            Alerts.show_success("Éxito", f"¡Bienvenido, {usuario_encontrado['nombreUsuarios']}!", master=self)
            
            self.entry_user.delete(0, 'end')
            self.entry_password.delete(0, 'end')
            self.check_show_password.deselect()
            self.entry_password.configure(show="*")
            
            self.withdraw() 
            dash = DashboardWindow(master=self, usuario=usuario_encontrado)
        else:
            Alerts.show_error("Error", "Los datos ingresados son incorrectos.", master=self)
