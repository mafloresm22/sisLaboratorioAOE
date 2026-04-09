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
        modal.attributes("-topmost", True)
        modal.lift()
        modal.grab_set() 
        
        # Centrado sobre el master
        modal.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() // 2) - (390 // 2)
        y = master.winfo_y() + (master.winfo_height() // 2) - (380 // 2)
        modal.geometry(f"+{max(0, x)}+{max(0, y)}")
        
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
        
        # Botón OK
        btn_ok = ctk.CTkButton(
            main_frame, text="OK", width=120, height=45, font=("Arial", 16, "bold"),
            fg_color="#7066e0", hover_color="#5a52b3", corner_radius=5,
            command=lambda: modal.destroy()
        )
        btn_ok.pack(pady=(0, 10))
        
        modal.after(3000, modal.destroy)
        
        if modal.winfo_exists():
            master.wait_window(modal)


    @staticmethod
    def confirm(master, title, text):
        if not master: return False
        
        result = {"value": False}
        modal = ctk.CTkToplevel(master)
        modal.overrideredirect(True)
        modal.geometry("390x380")
        modal.configure(fg_color="#cccccc")
        
        main_frame = ctk.CTkFrame(modal, fg_color="white", corner_radius=10, border_color="#d1d1d1", border_width=1)
        main_frame.pack(fill="both", expand=True)
        
        modal.transient(master)
        modal.attributes("-topmost", True)
        modal.grab_set()

        # Centrado
        modal.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() // 2) - (390 // 2)
        y = master.winfo_y() + (master.winfo_height() // 2) - (380 // 2)
        modal.geometry(f"+{max(0, x)}+{max(0, y)}")

        # Icono Warning para pregunta
        canvas = ctk.CTkCanvas(main_frame, width=90, height=90, bg="white", highlightthickness=0)
        canvas.pack(pady=(45, 20))
        canvas.create_oval(6, 6, 84, 84, outline="#f8bb86", width=5)
        canvas.create_text(45, 45, text="?", fill="#f8bb86", font=("Arial", 60, "bold"))

        ctk.CTkLabel(main_frame, text=title, font=("Arial", 22, "bold"), text_color="#545454").pack(pady=(0, 10))
        ctk.CTkLabel(main_frame, text=text, font=("Arial", 15), text_color="#545454", wraplength=350).pack(pady=(0, 30))

        btn_row = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_row.pack(pady=10)

        def set_res(val):
            result["value"] = val
            modal.destroy()

        ctk.CTkButton(btn_row, text="Sí, confirmar", width=140, height=40, fg_color="#7066e0", command=lambda: set_res(True)).pack(side="left", padx=10)
        ctk.CTkButton(btn_row, text="Cancelar", width=100, height=40, fg_color="#aaa", command=lambda: set_res(False)).pack(side="left", padx=10)

        master.wait_window(modal)
        return result["value"]


class Alerts:
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

    @staticmethod
    def ask_question(titulo, mensaje, master=None):
        return Swal.confirm(master, titulo, mensaje)
