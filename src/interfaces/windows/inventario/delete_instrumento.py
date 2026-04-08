import customtkinter as ctk
from PIL import Image
import os
from utils.paths import get_resource_path
from services.instrumentos.instrumentos import InstrumentoService
from interfaces.components.mensajes import Alerts

class DeleteInstrumentoModal(ctk.CTkToplevel):
    def __init__(self, master, instrumento, parent_view=None, **kwargs):
        super().__init__(master, **kwargs)
        self.withdraw()
        self.instrumento = instrumento
        self.parent_view = parent_view
        
        # --- Configuración Visual ---
        self.title("Eliminar Instrumento")
        self.width = 450
        self.height = 320
        self.overrideredirect(True)
        
        # Centrado
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (self.width // 2)
        y = (screen_height // 2) - (self.height // 2)
        self.geometry(f"{self.width}x{self.height}+{x}+{y}")
        self.configure(fg_color="white")
        
        # Overlay
        self.overlay = ctk.CTkToplevel(self.master)
        self.overlay.withdraw()
        self.overlay.geometry(f"{screen_width}x{screen_height}+0+0")
        self.overlay.overrideredirect(True)
        self.overlay.configure(fg_color="black")
        self.overlay.attributes("-alpha", 0.4)
        self.overlay.deiconify()
        self.deiconify()

        # Contenedor con borde
        self.container = ctk.CTkFrame(self, fg_color="white", corner_radius=20, border_width=2, border_color="#f5d6d6")
        self.container.pack(fill="both", expand=True, padx=2, pady=2)

        # Icono de advertencia
        try:
            icons_dir = os.path.join("assets", "icons", "buttons")
            delete_path = get_resource_path(os.path.join(icons_dir, "delete_2550318.png"))
            delete_img = ctk.CTkImage(Image.open(delete_path), size=(60, 60))
            self.lbl_icon = ctk.CTkLabel(self.container, image=delete_img, text="")
        except:
            self.lbl_icon = ctk.CTkLabel(self.container, text="⚠️", font=("Arial", 48))
        self.lbl_icon.pack(pady=(30, 10))

        # Título
        ctk.CTkLabel(
            self.container, text="¿Confirmar Eliminación?", 
            font=("Arial", 22, "bold"), text_color="#c0392b"
        ).pack(pady=5)

        # Mensaje
        msg = f"¿Está seguro de que desea eliminar el instrumento:\n'{instrumento.descripcionInstrumento}'?"
        ctk.CTkLabel(
            self.container, text=msg, 
            font=("Arial", 14), text_color="#7f8c8d", wraplength=380
        ).pack(pady=(5, 30), padx=20)

        # Botones
        self.actions = ctk.CTkFrame(self.container, fg_color="transparent")
        self.actions.pack(fill="x", side="bottom", pady=25)

        self.btn_cancel = ctk.CTkButton(
            self.actions, text="Cancelar", fg_color="#d33", hover_color="#b22",
            text_color="white", font=("Arial", 14, "bold"), height=45, corner_radius=10,
            command=self.close_modal
        )
        self.btn_cancel.pack(side="left", fill="x", expand=True, padx=(25, 10))

        self.btn_confirm = ctk.CTkButton(
            self.actions, text="Eliminar Registro", fg_color="#3085d6", hover_color="#2b77c0",
            text_color="white", font=("Arial", 14, "bold"), height=45, corner_radius=10,
            command=self.handle_delete
        )
        self.btn_confirm.pack(side="left", fill="x", expand=True, padx=(10, 25))

        self.attributes("-topmost", True)
        self.grab_set()

    def handle_delete(self):
        self.btn_confirm.configure(state="disabled", text="Eliminando...")
        self.update()
        
        success = InstrumentoService.delete_instrumento(self.instrumento.idInstrumento)
        
        if success:
            Alerts.show_success("Registro Eliminado", "El instrumento y su imagen han sido borrados.", master=self.master)
            if self.parent_view:
                self.parent_view.all_data = []
                self.parent_view.load_data()
            self.close_modal()
        else:
            Alerts.show_error("Error", "No se pudo eliminar el instrumento de la base de datos.", master=self.master)
            self.btn_confirm.configure(state="normal", text="Eliminar Registro")

    def close_modal(self):
        self.grab_release()
        self.overlay.destroy()
        self.destroy()
