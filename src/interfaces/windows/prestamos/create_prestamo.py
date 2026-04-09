import customtkinter as ctk
from PIL import Image
import os
from datetime import datetime, timedelta
from interfaces.components.mensajes import Alerts
from services.prestamos.prestamos import PrestamoService
from services.usuarios.usuarios import UsuarioService
from models.prestamos.prestamos import Prestamo
from utils.paths import get_resource_path

# Iconos
_ICONS_DIR = os.path.join("assets", "icons", "buttons")

class CreatePrestamoModal(ctk.CTkToplevel):
    def __init__(self, master, instrumento, usuario_actual, on_success=None, **kwargs):
        super().__init__(master, **kwargs)
        self.withdraw()
        self.instrumento = instrumento
        self.usuario_actual = usuario_actual
        self.on_success = on_success
        
        # --- CAPA DE OPACIDAD (OVERLAY) ---
        self.overlay = ctk.CTkToplevel(self.master)
        self.overlay.withdraw()
        self.overlay.geometry(f"{self.overlay.winfo_screenwidth()}x{self.overlay.winfo_screenheight()}+0+0")
        self.overlay.overrideredirect(True)
        self.overlay.configure(fg_color="black")
        self.overlay.attributes("-alpha", 0.0)

        # --- CONFIGURACIÓN MODAL ---
        self.overrideredirect(True)
        self.width = 750
        self.height = 580

        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.target_x = (screen_width // 2) - (self.width // 2) + 80
        self.target_y = (screen_height // 2) - (self.height // 2)

        self.current_y = self.target_y - 80
        self.geometry(f"{self.width}x{self.height}+{self.target_x}+{int(self.current_y)}")
        self.configure(fg_color="white")
        self.attributes("-alpha", 0.0)

        self.overlay.deiconify()
        self.deiconify()

        # Contenedor con borde suave
        self.container = ctk.CTkFrame(self, fg_color="white", corner_radius=20, border_width=1, border_color="#ecf0f1")
        self.container.pack(fill="both", expand=True)

        self._build_ui()
        self.animate_entry()
        self.attributes("-topmost", True)
        self.grab_set()

    def _build_ui(self):
        # 1. HEADER
        header = ctk.CTkFrame(self.container, fg_color="#186ccf", height=60, corner_radius=20)
        header.pack(fill="x", side="top", padx=2, pady=2)
        header.pack_propagate(False)

        try:
            icon_path = get_resource_path(os.path.join(_ICONS_DIR, "add_6902311.png"))
            header_img = ctk.CTkImage(Image.open(icon_path), size=(22, 22))
            ctk.CTkLabel(header, text="", image=header_img).pack(side="left", padx=(25, 12))
        except: pass

        ctk.CTkLabel(header, text="Nueva Solicitud de Préstamo", font=("Arial", 20, "bold"), text_color="white").pack(side="left")

        ctk.CTkButton(
            header, text="✕", width=35, height=35,
            fg_color="transparent", text_color="white",
            hover_color="#e74c3c", font=("Arial", 18), corner_radius=18,
            command=self.close_modal
        ).pack(side="right", padx=15)

        # 2. BODY
        body = ctk.CTkFrame(self.container, fg_color="white")
        body.pack(fill="both", expand=True, padx=40, pady=25)
        
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)

        # Instrumento
        icon_box = ctk.CTkImage(Image.open(get_resource_path(os.path.join("assets", "icons", "unidad_img", "package_1274687.png"))), size=(20, 20))
        self._label(body, " Instrumento Seleccionado", icon=icon_box).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))
        self.txt_inst = ctk.CTkEntry(body, height=45, corner_radius=10, border_width=2, fg_color="#f1f2f6", font=("Arial", 14, "bold"))
        self.txt_inst.insert(0, f" {self.instrumento.descripcionInstrumento}")
        self.txt_inst.configure(state="disabled")
        self.txt_inst.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 20))

        # Solicitante
        icon_user = ctk.CTkImage(Image.open(get_resource_path(os.path.join("assets", "icons", "dashboard", "7816987_usuario.png"))), size=(20, 20))
        self._label(body, " Usuario Solicitante", icon=icon_user).grid(row=2, column=0, sticky="w", pady=(0, 5))
        self.users_data = UsuarioService.get_all_usuarios()
        user_names = [f"{u.nombreUsuarios} ({u.nombreRol})" for u in self.users_data]
        self.combo_solicitante = ctk.CTkComboBox(body, values=user_names, height=45, corner_radius=10, border_width=2, state="readonly", font=("Arial", 13))
        self.combo_solicitante.grid(row=3, column=0, sticky="ew", padx=(0, 10), pady=(0, 20))
        self.combo_solicitante.set("Seleccionar de la lista...")

        # Cantidad
        icon_num = ctk.CTkImage(Image.open(get_resource_path(os.path.join("assets", "icons", "unidad_img", "meter_3348866.png"))), size=(20, 20))
        self._label(body, f" Cantidad (Stock: {self.instrumento.cantidadInstrumento:g})", icon=icon_num).grid(row=2, column=1, sticky="w", pady=(0, 5))
        self.ent_cantidad = ctk.CTkEntry(body, placeholder_text="Ej: 1", height=45, corner_radius=10, border_width=2)
        self.ent_cantidad.insert(0, "1")
        self.ent_cantidad.grid(row=3, column=1, sticky="ew", padx=(10, 0), pady=(0, 20))

        # Fecha y Hora Límite
        icon_date = ctk.CTkImage(Image.open(get_resource_path(os.path.join("assets", "icons", "buttons", "other_12283713.png"))), size=(20, 20))
        self._label(body, " Fecha y Hora Límite", icon=icon_date).grid(row=4, column=0, sticky="w", pady=(0, 5))
        self.ent_fecha = ctk.CTkEntry(body, height=45, corner_radius=10, border_width=2)
        # Formato con Hora para mayor precisión
        default_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d %H:%M")
        self.ent_fecha.insert(0, default_date)
        self.ent_fecha.grid(row=5, column=0, sticky="ew", padx=(0, 10), pady=(0, 20))

        # Motivo
        icon_msg = ctk.CTkImage(Image.open(get_resource_path(os.path.join("assets", "icons", "buttons", "show_8358982.png"))), size=(20, 20))
        self._label(body, " Motivo del Préstamo", icon=icon_msg).grid(row=4, column=1, sticky="w", pady=(0, 5))
        self.txt_motivo = ctk.CTkTextbox(body, height=90, corner_radius=10, border_width=2, border_color="#dcdde1", font=("Arial", 12))
        self.txt_motivo.insert("1.0", "Uso académico en laboratorio.")
        self.txt_motivo.grid(row=5, column=1, rowspan=2, sticky="nsew", padx=(10, 0))

        # 3. FOOTER
        footer = ctk.CTkFrame(self.container, fg_color="#fdfdfd", height=80, corner_radius=20)
        footer.pack(fill="x", side="bottom", padx=2, pady=2)
        footer.pack_propagate(False)

        ctk.CTkFrame(footer, fg_color="#f1f2f6", height=1).pack(fill="x", side="top")

        ctk.CTkButton(
            footer, text="Confirmar Préstamo",
            fg_color="#27ae60", hover_color="#219150",
            width=200, height=45, corner_radius=10,
            font=("Arial", 14, "bold"),
            command=self._save_loan
        ).pack(side="right", padx=(0, 40), pady=15)

        ctk.CTkButton(
            footer, text="Cancelar",
            fg_color="#f5334d", hover_color="#d62c42",
            width=120, height=45, corner_radius=10,
            font=("Arial", 14, "bold"),
            command=self.close_modal
        ).pack(side="right", padx=15, pady=15)

    def _label(self, master, text, icon=None):
        return ctk.CTkLabel(master, text=text, image=icon, compound="left", font=("Arial", 12, "bold"), text_color="#34495e")

    def _save_loan(self):
        solicitante_str = self.combo_solicitante.get()
        motivo = self.txt_motivo.get("1.0", "end-1c").strip()
        fecha_limite = self.ent_fecha.get().strip()
        
        try:
            cant = float(self.ent_cantidad.get())
        except:
            Alerts.show_error("Error", "La cantidad debe ser un número numérico.", master=self)
            return

        if solicitante_str == "Seleccionar de la lista...":
            Alerts.show_error("Campo Requerido", "Por favor seleccione un usuario solicitante.", master=self)
            return

        if cant > self.instrumento.cantidadInstrumento:
            Alerts.show_error("Stock Insuficiente", f"Solo hay {self.instrumento.cantidadInstrumento:g} disponibles.", master=self)
            return

        # Encontrar el usuario seleccionado
        user_idx = self.combo_solicitante.cget("values").index(solicitante_str)
        user_selected = self.users_data[user_idx]

        nuevo_p = Prestamo(
            usuarioId=user_selected.idUsuarios,
            fechaLimitePrestamo=fecha_limite,
            motivoPrestamo=motivo or "Sin motivo especificado",
            estadoPrestamo="activo"
        )
        
        detalles = [{'instrumentoId': self.instrumento.idInstrumento, 'cantidadSolicitada': cant}]
        
        res = PrestamoService.create_prestamo(nuevo_p, detalles)
        if res:
            Alerts.show_success("Éxito", "El préstamo ha sido registrado correctamente.", master=self)
            if self.on_success: self.on_success()
            self.close_modal()
        else:
            Alerts.show_error("Error", "No se pudo registrar en la base de datos.", master=self)

    def close_modal(self):
        self.grab_release()
        self.animate_exit()

    def animate_entry(self):
        try:
            alpha = float(self.attributes("-alpha"))
            overlay_alpha = float(self.overlay.attributes("-alpha"))
            if alpha < 1.0: self.attributes("-alpha", min(1.0, alpha + 0.12))
            if overlay_alpha < 0.5: self.overlay.attributes("-alpha", min(0.5, overlay_alpha + 0.05))

            if self.current_y < self.target_y:
                self.current_y += (self.target_y - self.current_y) * 0.15 + 0.5
                self.geometry(f"+{self.target_x}+{int(self.current_y)}")
                self.after(8, self.animate_entry)
            elif alpha < 1.0 or overlay_alpha < 0.5:
                self.after(8, self.animate_entry)
        except: pass

    def animate_exit(self):
        try:
            alpha = float(self.attributes("-alpha"))
            if alpha > 0:
                self.current_y += 18
                self.attributes("-alpha", max(0, alpha - 0.15))
                self.overlay.attributes("-alpha", max(0, float(self.overlay.attributes("-alpha")) - 0.08))
                self.geometry(f"+{self.target_x}+{int(self.current_y)}")
                self.after(8, self.animate_exit)
            else:
                self.overlay.destroy()
                self.destroy()
        except: pass
