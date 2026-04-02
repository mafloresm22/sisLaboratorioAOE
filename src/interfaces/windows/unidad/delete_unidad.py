import customtkinter as ctk
from services.unidad.unidad import UnidadService
from interfaces.components.mensajes import Alerts

class DeleteUnidadModal(ctk.CTkToplevel):
    def __init__(self, master, unit_data, parent_view=None, **kwargs):
        super().__init__(master, **kwargs)
        self.withdraw() # Ocultar mientras se configura
        self.parent_view = parent_view
        self.id_unidad = unit_data.get('idUnidad')
        self.nombre_unidad = unit_data.get('nombreUnidad')
        
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
        
        # Centrar + Offset derecha
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
        
        # 1. ICONO WARNING
        self.icon_circle_frame = ctk.CTkFrame(
            self.container, width=100, height=100,
            corner_radius=50, border_width=4, border_color="#f8bb86",
            fg_color="transparent"
        )
        self.icon_circle_frame.pack(pady=(35, 10))
        self.icon_circle_frame.pack_propagate(False)
        self.lbl_icon_symbol = ctk.CTkLabel(self.icon_circle_frame, text="!", font=("Arial", 60, "bold"), text_color="#f8bb86")
        self.lbl_icon_symbol.place(relx=0.5, rely=0.5, anchor="center")
        
        # 2. TÍTULO
        self.lbl_title = ctk.CTkLabel(self.container, text="¿Estás seguro?", font=("Arial", 28, "bold"), text_color="#595959")
        self.lbl_title.pack(pady=(10, 0))
        
        # 3. TEXTO
        self.lbl_text = ctk.CTkLabel(
            self.container, 
            text=f"No podrás revertir la eliminación de la unidad:\n'{self.nombre_unidad}'", 
            font=("Arial", 16), text_color="#545454", justify="center"
        )
        self.lbl_text.pack(pady=(15, 25), padx=20)
        
        # 4. BOTONES
        self.btns_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.btns_frame.pack(pady=10)
        
        self.btn_confirm = ctk.CTkButton(
            self.btns_frame, text="¡Sí, eliminar!", 
            fg_color="#3085d6", hover_color="#2b77c0",
            font=("Arial", 15, "bold"), width=150, height=45, corner_radius=8,
            command=self.confirm_delete
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

    def confirm_delete(self):
        resultado = UnidadService.delete_unidad(self.id_unidad)
        
        if resultado == "in_use":
            Alerts.show_error(
                "No se puede eliminar", 
                "Esta unidad está siendo utilizada por uno o más instrumentos en el inventario.", 
                master=self.master
            )
            self.close_modal()
        elif resultado:
            self.close_modal()
            Alerts.show_success("¡Eliminado!", f"La unidad '{self.nombre_unidad}' ha sido borrada.", master=self.master)
            if self.parent_view:
                self.parent_view.load_unidades()
        else:
            Alerts.show_error("Error", "Ocurrió un fallo al intentar eliminar la unidad.", master=self.master)
            self.close_modal()
