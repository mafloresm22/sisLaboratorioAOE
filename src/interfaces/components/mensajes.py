import customtkinter as ctk

class Swal:
    @staticmethod
    def fire(master, title, text, icon="success"):
        if not master:
            return

        modal = ctk.CTkToplevel(master)

        modal.overrideredirect(True)
        modal.geometry("390x380")
        modal.resizable(False, False)

        # Fondo transparente o gris sutil para el contorno
        modal.configure(fg_color="#cccccc")
        
        # Contenedor principal para simular el panel blanco curvado
        main_frame = ctk.CTkFrame(modal, fg_color="white", corner_radius=10, border_color="#d1d1d1", border_width=1)
        main_frame.pack(fill="both", expand=True)  

        # Comportamiento Modal estricto: bloquea la ventana de fondo
        modal.transient(master) 
        modal.grab_set() 
        
        # Centrado perfecto sobre el programa principal
        modal.update_idletasks()
        master.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() // 2) - (450 // 2)
        y = master.winfo_y() + (master.winfo_height() // 2) - (380 // 2)
        modal.geometry(f"+{x}+{y}")
        
        # Paleta de colores
        icons = {
            "success": ("#a5dc86", "✓"),
            "error": ("#f27474", "✗"),
            "warning": ("#f8bb86", "!"),
            "info": ("#3fc3ee", "i")
        }
        color, symbol = icons.get(icon, icons["info"])
        
        # Lienzo para el Icono
        canvas = ctk.CTkCanvas(main_frame, width=90, height=90, bg="white", highlightthickness=0)
        canvas.pack(pady=(45, 20))
        canvas.create_oval(6, 6, 84, 84, outline=color, width=5)
        
        font_size = 45 if icon != "warning" else 60
        canvas.create_text(45, 45, text=symbol, fill=color, font=("Arial", font_size, "bold"))
        
        # Título
        lbl_title = ctk.CTkLabel(main_frame, text=title, font=("Arial", 28, "bold"), text_color="#545454")
        lbl_title.pack(pady=(0, 10))
        
        # Texto secundario
        lbl_msg = ctk.CTkLabel(main_frame, text=text, font=("Arial", 15), text_color="#545454", wraplength=400, justify="center")
        lbl_msg.pack(pady=(0, 30))
        
        # Botón OK característico de SweetAlert (Azul púrpura #7066e0)
        btn_ok = ctk.CTkButton(
            main_frame, text="OK", width=120, height=45, font=("Arial", 16, "bold"),
            fg_color="#7066e0", hover_color="#5a52b3", corner_radius=5,
            command=lambda: modal.destroy()
        )
        btn_ok.pack(pady=(0, 10))
        
        modal.after(3000, modal.destroy)
        
        if modal.winfo_exists():
            master.wait_window(modal)


class Alerts:
    """Clase puente para que el resto del sistema siga funcionando igual"""
    @staticmethod
    def show_success(titulo, mensaje, master=None):
        Swal.fire(master, titulo, mensaje, "success")

    @staticmethod
    def show_warning(titulo, mensaje, master=None):
        Swal.fire(master, titulo, mensaje, "warning")

    @staticmethod
    def show_error(titulo, mensaje, master=None):
        Swal.fire(master, titulo, mensaje, "error")

    @staticmethod
    def show_info(titulo, mensaje, master=None):
        Swal.fire(master, titulo, mensaje, "info")
