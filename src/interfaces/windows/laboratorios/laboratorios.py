import customtkinter as ctk
from PIL import Image
import os
from services.laboratorios.laboratorios import LaboratorioService

class LaboratorioStatCard(ctk.CTkFrame):
    def __init__(self, master, title, count, color, **kwargs):
        super().__init__(master, fg_color="#f8f9fa", border_width=1, border_color="#e0e0e0", corner_radius=12, **kwargs)
        
        self.grid_columnconfigure(1, weight=1)
        
        # Icono decorativo
        self.icon_lbl = ctk.CTkLabel(self, text="🧪", font=("Arial", 24))
        self.icon_lbl.grid(row=0, column=0, padx=15, pady=15)
        
        # Textos
        self.info_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.info_frame.grid(row=0, column=1, sticky="w")
        
        self.name_lbl = ctk.CTkLabel(self.info_frame, text=title, font=("Arial", 13, "bold"), text_color="#595959")
        self.name_lbl.pack(anchor="w")
        
        self.count_lbl = ctk.CTkLabel(self.info_frame, text=f"{count} Instrumentos", font=("Arial", 12), text_color=color)
        self.count_lbl.pack(anchor="w")

class LaboratoriosFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="white", corner_radius=15)
        
        # --- Layout Principal (2 Columnas: 75% Tabla, 25% Stats) ---
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ==========================================
        # 1. SECCIÓN IZQUIERDA: TABLA
        # ==========================================
        self.left_container = ctk.CTkFrame(self, fg_color="transparent")
        self.left_container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        # CABECERA INTERNA
        self.inner_header = ctk.CTkFrame(self.left_container, fg_color="transparent")
        self.inner_header.pack(fill="x", pady=(0, 20))
        
        self.lbl_title = ctk.CTkLabel(
            self.inner_header, text="Gestión de Laboratorios", 
            font=("Arial", 30, "bold"), text_color="#2c3e50"
        )
        self.lbl_title.pack(side="left")

        self.btn_add = ctk.CTkButton(
            self.inner_header, text="➕ Nuevo Laboratorio", width=170, height=45,
            fg_color="#186ccf", hover_color="#145cb3",
            font=("Arial", 14, "bold"), corner_radius=10,
            command=self.on_add_lab
        )
        self.btn_add.pack(side="right")

        # CONTENEDOR TABLA
        self.table_container = ctk.CTkFrame(self.left_container, fg_color="transparent")
        self.table_container.pack(fill="both", expand=True)
        
        # 1. Cabecera Tabla
        self.table_header = ctk.CTkFrame(self.table_container, fg_color="#f8f9fa", height=50, corner_radius=10)
        self.table_header.pack(fill="x", pady=(0, 10))
        self.table_header.pack_propagate(False)

        # Configuración de columnas (NRO, NOMBRE, ESTADO, ACCIONES)
        headers = [
            ("NRO", 0.05), 
            ("NOMBRE DEL LABORATORIO", 0.15), 
            ("ESTADO", 0.55), 
            ("ACCIONES", 0.85)
        ]
        
        for text, rel_x in headers:
            anchor = "center" if text in ["ESTADO", "ACCIONES"] else "w"
            lbl = ctk.CTkLabel(self.table_header, text=text, font=("Arial", 12, "bold"), text_color="#7f8c8d")
            lbl.place(relx=rel_x, rely=0.5, anchor=anchor)

        # 2. Cuerpo Tabla
        self.scroll_table = ctk.CTkScrollableFrame(self.table_container, fg_color="transparent")
        self.scroll_table.pack(fill="both", expand=True)

        # ==========================================
        # 2. SECCIÓN DERECHA: ESTADÍSTICAS
        # ==========================================
        self.right_container = ctk.CTkFrame(self, fg_color="#fcfcfc", corner_radius=0)
        self.right_container.grid(row=0, column=1, sticky="nsew")
        
        # Border izquierdo simulado
        self.border_left = ctk.CTkFrame(self.right_container, fg_color="#e0e0e0", width=1)
        self.border_left.pack(side="left", fill="y")

        self.stats_inner = ctk.CTkScrollableFrame(self.right_container, fg_color="transparent")
        self.stats_inner.pack(fill="both", expand=True, padx=15, pady=20)

        self.lbl_stats_title = ctk.CTkLabel(
            self.stats_inner, text="📊 Resumen por Laboratorio", 
            font=("Arial", 16, "bold"), text_color="#2c3e50"
        )
        self.lbl_stats_title.pack(pady=(0, 20), anchor="w")

        self.load_data()

    def load_data(self):
        # Limpiar
        for child in self.scroll_table.winfo_children(): child.destroy()
        for child in self.stats_inner.winfo_children(): 
            if isinstance(child, LaboratorioStatCard): child.destroy()

        labs = LaboratorioService.get_all_laboratorios()
        
        if not labs:
            self.show_empty_state()
            return

        colors = ["#186ccf", "#27ae60", "#f39c12", "#8e44ad", "#e74c3c", "#16a085"]
        
        for i, lab in enumerate(labs):
            color = colors[i % len(colors)]
            
            # --- FILA DE TABLA ---
            bg_row = "white" if i % 2 == 0 else "#fdfdfd"
            row = ctk.CTkFrame(self.scroll_table, fg_color=bg_row, height=60, corner_radius=8)
            row.pack(fill="x", pady=2)
            row.pack_propagate(False)

            # NRO
            ctk.CTkLabel(row, text=str(i + 1), font=("Arial", 14), text_color="#7f8c8d").place(relx=0.05, rely=0.5, anchor="w")
            
            # Nombre con Identificador
            id_indicator = ctk.CTkFrame(row, width=4, height=30, fg_color=color, corner_radius=2)
            id_indicator.place(relx=0.12, rely=0.5, anchor="w")
            
            ctk.CTkLabel(row, text=lab.nombreLaboratorios, font=("Arial", 14, "bold"), text_color="#2c3e50").place(relx=0.15, rely=0.5, anchor="w")

            # ESTADO
            estado = lab.estadoLaboratorios.lower()
            is_disponible = "disponible" in estado
            color_text = "#27ae60" if is_disponible else "#e74c3c"
            color_bg = "#e8f5e9" if is_disponible else "#ffebee"
            
            estado_badge = ctk.CTkFrame(row, fg_color=color_bg, corner_radius=12, height=24)
            estado_badge.place(relx=0.55, rely=0.5, anchor="center")
            
            lbl_est = ctk.CTkLabel(estado_badge, text=lab.estadoLaboratorios.upper(), font=("Arial", 10, "bold"), text_color=color_text)
            lbl_est.pack(padx=10)

            # ACCIONES
            acts = ctk.CTkFrame(row, fg_color="transparent")
            acts.place(relx=0.85, rely=0.5, anchor="center")
            
            ctk.CTkButton(acts, text="✏️", width=32, height=32, fg_color="#ffae42", hover_color="#e67e22", 
                         font=("Segoe UI Emoji", 14), corner_radius=6, command=lambda l=lab: self.on_edit_lab(l)).pack(side="left", padx=3)
            ctk.CTkButton(acts, text="🗑️", width=32, height=32, fg_color="#ff5c5c", hover_color="#c0392b", 
                         font=("Segoe UI Emoji", 14), corner_radius=6, command=lambda l=lab: self.on_delete_lab(l)).pack(side="left", padx=3)

            # --- CARD DE ESTADÍSTICA ---
            stat_card = LaboratorioStatCard(self.stats_inner, title=lab.nombreLaboratorios, count=lab.instrument_count, color=color)
            stat_card.pack(fill="x", pady=5)

    def show_empty_state(self):
        empty = ctk.CTkFrame(self.scroll_table, fg_color="transparent")
        empty.pack(pady=80)
        ctk.CTkLabel(empty, text="🔍", font=("Arial", 60)).pack()
        ctk.CTkLabel(empty, text="Sin laboratorios registrados", font=("Arial", 16, "bold"), text_color="#bdc3c7").pack(pady=10)

    def on_add_lab(self): print("Agregar")
    def on_edit_lab(self, lab): print(f"Editar {lab.nombreLaboratorios}")
    def on_delete_lab(self, lab): print(f"Eliminar {lab.nombreLaboratorios}")
