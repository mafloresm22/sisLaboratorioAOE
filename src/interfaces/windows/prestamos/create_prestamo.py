import customtkinter as ctk
from datetime import datetime, timedelta
from interfaces.components.mensajes import Alerts
from services.prestamos.prestamos import PrestamoService
from models.prestamos.prestamos import Prestamo

class CreatePrestamoModal(ctk.CTkToplevel):
    def __init__(self, master, instrumento, usuario_actual, on_success=None):
        super().__init__(master)
        self.instrumento = instrumento
        self.usuario_actual = usuario_actual
        self.on_success = on_success
        
        self.title("Nuevo Préstamo")
        self.geometry("500x650")
        self.configure(fg_color="#f0f2f5")
        self.transient(master)
        self.grab_set()
        
        # Centrar Ventana
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.winfo_screenheight() // 2) - (650 // 2)
        self.geometry(f"+{x}+{y}")

        self._build_ui()

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="#186ccf", height=80, corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(header, text="📝 FORMULARIO DE PRÉSTAMO", font=("Arial", 18, "bold"), text_color="white").pack(pady=25)

        container = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Instrumento Info (Read Only)
        ctk.CTkLabel(container, text="Instrumento Seleccionado:", font=("Arial", 12, "bold"), text_color="#7f8c8d").pack(anchor="w", padx=25, pady=(20, 0))
        self.txt_inst = ctk.CTkEntry(container, width=400, height=40, corner_radius=10, border_width=0, fg_color="#f1f2f6")
        self.txt_inst.insert(0, self.instrumento.descripcionInstrumento)
        self.txt_inst.configure(state="disabled")
        self.txt_inst.pack(padx=25, pady=(5, 15))

        # Solicitante
        ctk.CTkLabel(container, text="Nombre del Solicitante:", font=("Arial", 12, "bold"), text_color="#2c3e50").pack(anchor="w", padx=25)
        self.ent_nombre = ctk.CTkEntry(container, placeholder_text="Ej. Juan Pérez", width=400, height=45, corner_radius=10)
        self.ent_nombre.pack(padx=25, pady=(5, 15))

        # Carrera / Rol
        ctk.CTkLabel(container, text="Carrera o Rol:", font=("Arial", 12, "bold"), text_color="#2c3e50").pack(anchor="w", padx=25)
        self.ent_carrera = ctk.CTkEntry(container, placeholder_text="Ej. Ing. De Sistemas", width=400, height=45, corner_radius=10)
        self.ent_carrera.pack(padx=25, pady=(5, 15))

        # Cantidad
        ctk.CTkLabel(container, text=f"Cantidad (Disponible: {self.instrumento.cantidadInstrumento:g}):", font=("Arial", 12, "bold"), text_color="#2c3e50").pack(anchor="w", padx=25)
        self.ent_cantidad = ctk.CTkEntry(container, width=400, height=45, corner_radius=10)
        self.ent_cantidad.insert(0, "1")
        self.ent_cantidad.pack(padx=25, pady=(5, 15))

        # Fecha de Devolución (Default +3 días)
        ctk.CTkLabel(container, text="Fecha Límite de Devolución:", font=("Arial", 12, "bold"), text_color="#2c3e50").pack(anchor="w", padx=25)
        self.ent_fecha = ctk.CTkEntry(container, width=400, height=45, corner_radius=10)
        default_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
        self.ent_fecha.insert(0, default_date)
        self.ent_fecha.pack(padx=25, pady=(5, 15))

        # Botones
        btn_save = ctk.CTkButton(
            container, text="Confirmar Préstamo", height=50, width=400, corner_radius=12,
            fg_color="#27ae60", hover_color="#219150", font=("Arial", 15, "bold"),
            command=self._save_loan
        )
        btn_save.pack(pady=(20, 10))

    def _save_loan(self):
        nombre = self.ent_nombre.get().strip()
        carrera = self.ent_carrera.get().strip()
        try:
            cant = float(self.ent_cantidad.get())
        except:
            Alerts.show_error("Error", "La cantidad debe ser un número.")
            return

        if not nombre or not carrera:
            Alerts.show_error("Error", "Por favor complete el nombre y la carrera.")
            return

        if cant > self.instrumento.cantidadInstrumento:
            Alerts.show_error("Stock Insuficiente", "No hay suficiente stock para este préstamo.")
            return

        # Preparar Modelo
        # Nota: Usamos motivoPrestamo para guardar el nombre y carrera ya que son datos externos a la tabla Usuarios
        motivo = f"SOLICITANTE: {nombre} | CARRERA: {carrera} | ORIGEN: Préstamo Externo"
        
        nuevo_p = Prestamo(
            usuarioId=self.usuario_actual.get('idUsuarios', 1),
            fechaLimitePrestamo=self.ent_fecha.get(),
            motivoPrestamo=motivo,
            estadoPrestamo="Activo"
        )
        
        detalles = [{'instrumentoId': self.instrumento.idInstrumento, 'cantidadSolicitada': cant}]
        
        res = PrestamoService.create_prestamo(nuevo_p, detalles)
        if res:
            Alerts.show_success("Éxito", "El préstamo se ha registrado correctamente.")
            if self.on_success: self.on_success()
            self.destroy()
        else:
            Alerts.show_error("Error", "No se pudo registrar el préstamo en el servidor.")
