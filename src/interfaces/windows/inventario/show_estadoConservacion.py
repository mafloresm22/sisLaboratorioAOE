import customtkinter as ctk
import os

class LegendConservacionModal(ctk.CTkToplevel):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.withdraw()
        
        # --- CAPA DE OPACIDAD (OVERLAY) ---
        self.overlay = ctk.CTkToplevel(self.master)
        self.overlay.withdraw()
        self.overlay.geometry(f"{self.overlay.winfo_screenwidth()}x{self.overlay.winfo_screenheight()}+0+0")
        self.overlay.overrideredirect(True)
        self.overlay.configure(fg_color="black")
        self.overlay.attributes("-alpha", 0.5)
        
        # --- MODAL ---
        self.overrideredirect(True)
        self.width = 400
        self.height = 360
        
        # Centrar el modal en pantalla
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.target_x = ((screen_width // 2) - (self.width // 2)) + 150
        self.target_y = (screen_height // 2) - (self.height // 2)
        
        self.current_y = self.target_y - 60 
        self.geometry(f"{self.width}x{self.height}+{self.target_x}+{int(self.current_y)}")
        self.configure(fg_color="white")
        
        self.overlay.deiconify()
        self.deiconify()
        
        # --- CONTENEDOR PRINCIPAL ---
        self.container = ctk.CTkFrame(self, fg_color="white", corner_radius=15, border_width=2, border_color="#3498db")
        self.container.pack(fill="both", expand=True)
        
        # HEADER SENCILLO
        self.lbl_header = ctk.CTkLabel(
            self.container, text="Leyenda de Conservación", 
            font=("Arial", 20, "bold"), text_color="#2c3e50"
        )
        self.lbl_header.pack(pady=(25, 20))
        
        # BODY DISCRETO
        self.body = ctk.CTkFrame(self.container, fg_color="transparent")
        self.body.pack(fill="both", expand=True, padx=40)
        
        estados = [
            ("5 - NUEVO",      "#27ae60"),
            ("4 - BUENO",      "#186ccf"),
            ("3 - REGULAR",    "#d68910"),
            ("2 - MALO",       "#c0392b"),
        ]
        
        for texto, color in estados:
            lbl = ctk.CTkLabel(
                self.body, text=texto, 
                font=("Arial", 16, "bold"), text_color="white",
                fg_color=color, corner_radius=8, height=40
            )
            lbl.pack(fill="x", pady=5)

        # FOOTER
        self.btn_entendido = ctk.CTkButton(
            self.container, text="Cerrar", 
            fg_color="#f7607a", hover_color="#e63e5a",
            width=140, height=40, corner_radius=10,
            font=("Arial", 13, "bold"),
            command=self.close_modal
        )
        self.btn_entendido.pack(pady=25)

        self.animate_entry()
        self.attributes("-topmost", True)
        self.grab_set()

    def animate_entry(self):
        if self.current_y < self.target_y:
            distancia = self.target_y - self.current_y
            self.current_y += (distancia * 0.2) + 1
            if self.current_y > self.target_y: self.current_y = self.target_y
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
