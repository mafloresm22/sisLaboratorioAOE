import customtkinter as ctk
from services.laboratorios.laboratorios import LaboratorioService
from interfaces.components.mensajes import Alerts

class DeleteLaboratorioModal(ctk.CTkToplevel):
    def __init__(self, master, lab_data, parent_view=None, **kwargs):
        super().__init__(master, **kwargs)
        self.withdraw()
        self.parent_view = parent_view
        self.id_lab = lab_data.idLaboratorios
        self.nombre_lab = lab_data.nombreLaboratorios
        self.estado_lab = lab_data.estadoLaboratorios
        
        # --- CAPA DE OPACIDAD ---
        self.overlay = ctk.CTkToplevel(self.master)
        self.overlay.withdraw()
        self.overlay.geometry(f"{self.overlay.winfo_screenwidth()}x{self.overlay.winfo_screenheight()}+0+0")
        self.overlay.overrideredirect(True)
        self.overlay.configure(fg_color="black")
        self.overlay.attributes("-alpha", 0.5)
        
        # --- MODAL CONFIG ---
        self.overrideredirect(True)
        self.width = 450
        self.height = 380
        
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
        self.container = ctk.CTkFrame(self, fg_color="white", corner_radius=20, border_width=1, border_color="#f0f0f0")
        self.container.pack(fill="both", expand=True, padx=2, pady=2)
        
        # 1. ICONO (Cambia según estado)
        is_active = self.estado_lab.lower() == "disponible"
        icon_color = "#f8bb86" if is_active else "#3085d6"
        icon_symbol = "!" if is_active else "🔓"
        
        self.icon_circle_frame = ctk.CTkFrame(
            self.container, width=100, height=100,
            corner_radius=50, border_width=4, border_color=icon_color,
            fg_color="transparent"
        )
        self.icon_circle_frame.pack(pady=(35, 10))
        self.icon_circle_frame.pack_propagate(False)
        self.lbl_icon_symbol = ctk.CTkLabel(self.icon_circle_frame, text=icon_symbol, font=("Arial", 60, "bold"), text_color=icon_color)
        self.lbl_icon_symbol.place(relx=0.5, rely=0.5, anchor="center")
        
        # 2. TÍTULO
        title_text = "¿Desea desactivar?" if is_active else "¿Desea reactivar?"
        self.lbl_title = ctk.CTkLabel(self.container, text=title_text, font=("Arial", 28, "bold"), text_color="#595959")
        self.lbl_title.pack(pady=(10, 0))
        
        # 3. TEXTO
        action_desc = "marcará este laboratorio como NO DISPONIBLE." if is_active else "activará este laboratorio nuevamente."
        self.lbl_text = ctk.CTkLabel(
            self.container, 
            text=f"Se {action_desc}\nLaboratorio: '{self.nombre_lab}'", 
            font=("Arial", 16), text_color="#545454", justify="center"
        )
        self.lbl_text.pack(pady=(15, 25), padx=20)
        
        # 4. BOTONES
        self.btns_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.btns_frame.pack(pady=10)
        
        btn_confirm_text = "Sí, desactivar" if is_active else "Sí, activar"
        btn_confirm_color = "#3085d6" if is_active else "#27ae60"
        
        self.btn_confirm = ctk.CTkButton(
            self.btns_frame, text=btn_confirm_text, 
            fg_color=btn_confirm_color, hover_color=btn_confirm_color,
            font=("Arial", 15, "bold"), width=150, height=45, corner_radius=8,
            command=self.confirm_toggle
        )
        self.btn_confirm.pack(side="left", padx=10)
        
        self.btn_cancel = ctk.CTkButton(
            self.btns_frame, text="Cancelar", 
            fg_color="#d33", hover_color="#b22",
            font=("Arial", 15, "bold"), width=110, height=45, corner_radius=8,
            command=self.close_modal
        )
        self.btn_cancel.pack(side="left", padx=10)

        self.animate_entry()
        self.attributes("-topmost", True)
        self.grab_set()

    def animate_entry(self):
        if self.current_y < self.target_y:
            distancia = self.target_y - self.current_y
            self.current_y += (distancia * 0.25) + 1
            if self.current_y > self.target_y: self.current_y = self.target_y
            self.geometry(f"{self.width}x{self.height}+{self.target_x}+{int(self.current_y)}")
            self.after(12, self.animate_entry)

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

    def confirm_toggle(self):
        resultado = LaboratorioService.toggle_status(self.id_lab, self.estado_lab)
        
        if resultado:
            self.close_modal()
            new_state = "activado" if self.estado_lab.lower() != "disponible" else "desactivado"
            Alerts.show_success("¡Éxito!", f"El laboratorio ha sido {new_state}.", master=self.master)
            if self.parent_view:
                self.parent_view.load_data()
        else:
            Alerts.show_error("Error", "Ocurrió un fallo al intentar cambiar el estado.", master=self.master)
            self.close_modal()
