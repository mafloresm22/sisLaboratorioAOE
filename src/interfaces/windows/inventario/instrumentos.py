import customtkinter as ctk
from PIL import Image, ImageTk
import os
from models.instrumentos.instrumentos import Instrumento

class InstrumentosFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="white", corner_radius=15)
        
        # --- Layout Principal ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ==========================================
        # 1. CABECERA: TÍTULO, BUSCADOR Y BOTÓN
        # ==========================================
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.grid(row=0, column=0, sticky="ew", padx=25, pady=(25, 15))
        
        # Título del Módulo
        self.lbl_title = ctk.CTkLabel(
            self.header, text="Gestión de Inventario", 
            font=("Arial", 28, "bold"), text_color="#2c3e50"
        )
        self.lbl_title.pack(side="left")

        # Contenedor para Buscador y Botón (Derecha)
        self.actions_container = ctk.CTkFrame(self.header, fg_color="transparent")
        self.actions_container.pack(side="right")

        # Buscador estilizado
        self.search_entry = ctk.CTkEntry(
            self.actions_container, placeholder_text="🔍 Buscar instrumento...",
            width=300, height=40, font=("Arial", 13),
            border_color="#d1d8e0", corner_radius=10
        )
        self.search_entry.pack(side="left", padx=(0, 15))
        self.search_entry.bind("<KeyRelease>", self.filter_data)

        # Botón para Ver Leyenda de Estados
        self.btn_legend = ctk.CTkButton(
            self.actions_container, text="ℹ️ Ver Leyenda",
            width=140, height=45, corner_radius=10,
            fg_color="#3498db", hover_color="#2980b9", text_color="white",
            font=("Arial", 13, "bold"),
            command=self.on_show_legend
        )
        self.btn_legend.pack(side="left", padx=(0, 10))

        # Botón de Agregar
        self.btn_add = ctk.CTkButton(
            self.actions_container, text="➕ Agregar Instrumento", 
            width=190, height=45, corner_radius=10,
            fg_color="#27ae60", hover_color="#219150", text_color="white",
            font=("Arial", 14, "bold"),
            command=self.on_add_instrumento
        )
        self.btn_add.pack(side="left")

        # ==========================================
        # 2. TABLA DE DATOS
        # ==========================================
        self.table_container = ctk.CTkFrame(self, fg_color="transparent")
        self.table_container.grid(row=1, column=0, sticky="nsew", padx=25, pady=(0, 25))
        
        # CABECERA DE LA TABLA
        self.table_header = ctk.CTkFrame(self.table_container, fg_color="#59a4f0", height=45, corner_radius=10)
        self.table_header.pack(fill="x", pady=(0, 10))
        self.table_header.pack_propagate(False)

        self.col_map = {
            "N°": 0.02, "IMAGEN": 0.06, "DESCRIPCIÓN": 0.11, "CANT.": 0.30, 
            "MARCA": 0.36, "MODELO": 0.43, "SERIE": 0.50, "COLOR": 0.57, 
            "TAMAÑO": 0.64, "CONSERV.": 0.71, "UBICACIÓN": 0.78,
            "PISO": 0.87, "ACCIONES": 0.95
        }

        for text, rel_x in self.col_map.items():
            lbl = ctk.CTkLabel(self.table_header, text=text, font=("Arial", 11, "bold"), text_color="white")
            anchor = "center" if text in ["ACCIONES", "IMAGEN", "CONSERV."] else "w"
            lbl.place(relx=rel_x, rely=0.5, anchor=anchor)

        # CUERPO DE LA TABLA (Scrollable)
        self.scroll_table = ctk.CTkScrollableFrame(self.table_container, fg_color="transparent")
        self.scroll_table.pack(fill="both", expand=True)

        # ==========================================
        # 3. PAGINACIÓN Y METADATOS
        # ==========================================
        self.pagination_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.pagination_frame.grid(row=2, column=0, sticky="ew", padx=25, pady=(0, 20))
        
        # Botones y etiquetas
        self.btn_prev = ctk.CTkButton(self.pagination_frame, text="◀ Anterior", width=110, height=35, corner_radius=8, font=("Arial", 12, "bold"), fg_color="#34495e", hover_color="#2c3e50")
        self.btn_prev.pack(side="left", padx=5)
        
        self.lbl_pageinfo = ctk.CTkLabel(self.pagination_frame, text="Página 1 de 1", font=("Arial", 12, "bold"), text_color="#7f8c8d")
        self.lbl_pageinfo.pack(side="left", padx=15)
        
        self.btn_next = ctk.CTkButton(self.pagination_frame, text="Siguiente ▶", width=110, height=35, corner_radius=8, font=("Arial", 12, "bold"), fg_color="#34495e", hover_color="#2c3e50")
        self.btn_next.pack(side="left", padx=5)
        
        self.lbl_total_records = ctk.CTkLabel(self.pagination_frame, text="Total: 0 instrumentos registrados", font=("Arial", 12, "bold"), text_color="#95a5a6")
        self.lbl_total_records.pack(side="right", padx=10)

        self.load_data() # Cargar la vista de tabla

    def load_data(self):
        """Lógica para renderizar los datos o estado vacío de la tabla"""
        # Limpiar tabla
        for child in self.scroll_table.winfo_children():
            child.destroy()

        # --- DATOS DE EJEMPLO ---
        inst1 = Instrumento(
            idInstrumento=1, nombreInstrumento="Microscopio Binocular", 
            cantidadInstrumento=5, marcaInstrumento="Olympus", 
            modeloInstrumento="CX23", serieInstrumento="SN-00123", 
            colorInstrumento="Blanco", tamanoInstrumento="Mediano", 
            idEstadoCons=5, usuarioId=1, laboratorioId=1, pisoInstrumento="2do Piso"
        )
        inst1.nombre_laboratorio = "Lab. Biología"

        inst2 = Instrumento(
            idInstrumento=2, nombreInstrumento="Balanza Analítica", 
            cantidadInstrumento=2, marcaInstrumento="Ohaus", 
            modeloInstrumento="Pioneer", serieInstrumento="SN-99881", 
            colorInstrumento="Gris", tamanoInstrumento="Compacto", 
            idEstadoCons=4, usuarioId=2, laboratorioId=3, pisoInstrumento="1er Piso"
        )
        inst2.nombre_laboratorio = "Lab. Química"

        datos_en_tabla = [inst1, inst2] 
        
        # Validar Empty State (Sin Registros)
        if not datos_en_tabla:
            msg_frame = ctk.CTkFrame(self.scroll_table, fg_color="transparent")
            msg_frame.pack(fill="both", expand=True, pady=80)
            
            ctk.CTkLabel(msg_frame, text="📭", font=("Arial", 70)).pack(pady=(0, 15))
            ctk.CTkLabel(msg_frame, text="No se encontraron registros de instrumentos.", 
                         font=("Arial", 18, "bold"), text_color="#2c3e50").pack()
            ctk.CTkLabel(msg_frame, text="Intenta agregando un nuevo instrumento haciendo clic en el botón superior.", 
                         font=("Arial", 13), text_color="#7f8c8d").pack(pady=5)
            
            # Reset de etiquetas a 0
            self.lbl_pageinfo.configure(text="Página 0 de 0")
            self.lbl_total_records.configure(text="Total: 0 instrumentos registrados")
            self.btn_prev.configure(state="disabled", fg_color="#95a5a6")
            self.btn_next.configure(state="disabled", fg_color="#95a5a6")
            return

        # Actualizar info de paginación
        self.lbl_pageinfo.configure(text="Página 1 de 1")
        self.lbl_total_records.configure(text=f"Total: {len(datos_en_tabla)} instrumentos registrados")
        self.btn_prev.configure(state="normal", fg_color="#34495e")
        self.btn_next.configure(state="normal", fg_color="#34495e")

        for i, item in enumerate(datos_en_tabla):
            # Determinamos el color base de la fila
            row_color = "#ffffff" if i % 2 == 0 else "#fcfcfc"
            
            # --- Fila interactiva ---
            row = ctk.CTkFrame(self.scroll_table, fg_color=row_color, height=80, corner_radius=12)
            row.pack(fill="x", pady=4, padx=2) 
            row.pack_propagate(False)

            # Efecto Hover robusto contra Parpadeo usando Bounding Box
            def on_enter(e, r=row): 
                r.configure(fg_color="#eaf3fb") # Azul muy profesional
            
            def on_leave(e, r=row, c=row_color): 
                # Solo restaura el color si el cursor realmente salió del área de la fila
                mx, my = r.winfo_pointerxy()
                rx, ry = r.winfo_rootx(), r.winfo_rooty()
                rw, rh = r.winfo_width(), r.winfo_height()
                if not (rx <= mx <= rx + rw and ry <= my <= ry + rh):
                    r.configure(fg_color=c)
            
            row.bind("<Enter>", on_enter)
            row.bind("<Leave>", on_leave)

            # --- Columnas dinámicas usando col_map ---
            # 1. N° (Decorado con 0s y color corporativo)
            lbl_no = ctk.CTkLabel(row, text=str(i+1).zfill(2), font=("Arial", 14, "bold"), text_color="#186ccf")
            lbl_no.place(relx=self.col_map["N°"], rely=0.5, anchor="w")

            # 2. IMAGEN (Con borde moderno y fondo blanco)
            img_frame = ctk.CTkFrame(row, width=54, height=54, fg_color="#ffffff", border_width=1, border_color="#e0e0e0", corner_radius=12)
            img_frame.place(relx=self.col_map["IMAGEN"], rely=0.5, anchor="center")
            ctk_box = ctk.CTkLabel(img_frame, text="📦", font=("Arial", 26))
            ctk_box.place(relx=0.5, rely=0.5, anchor="center")

            # 3. DESCRIPCIÓN (Letra más grande y negrita)
            lbl_desc = ctk.CTkLabel(row, text=item.nombreInstrumento, font=("Arial", 13, "bold"), text_color="#2c3e50")
            lbl_desc.place(relx=self.col_map["DESCRIPCIÓN"], rely=0.5, anchor="w")

            # 4. CANTIDAD (Decorado con indicador visual)
            ctk.CTkLabel(row, text=f"{item.cantidadInstrumento} und.", font=("Arial", 12, "bold"), text_color="#16a085").place(relx=self.col_map["CANT."], rely=0.5, anchor="w")

            # 5. MARCA
            ctk.CTkLabel(row, text=item.marcaInstrumento or "-", font=("Arial", 11)).place(relx=self.col_map["MARCA"], rely=0.5, anchor="w")

            # 6. MODELO
            ctk.CTkLabel(row, text=item.modeloInstrumento or "-", font=("Arial", 11)).place(relx=self.col_map["MODELO"], rely=0.5, anchor="w")

            # 7. SERIE
            ctk.CTkLabel(row, text=item.serieInstrumento or "-", font=("Arial", 10), text_color="#7f8c8d").place(relx=self.col_map["SERIE"], rely=0.5, anchor="w")

            # 8. COLOR
            ctk.CTkLabel(row, text=item.colorInstrumento or "-", font=("Arial", 11)).place(relx=self.col_map["COLOR"], rely=0.5, anchor="w")

            # 9. TAMAÑO
            ctk.CTkLabel(row, text=item.tamanoInstrumento or "-", font=("Arial", 11)).place(relx=self.col_map["TAMAÑO"], rely=0.5, anchor="w")

            # 10. ESTADO DE CONSERVACIÓN
            color_map = { 5: ("#2ecc71", "#dff9fb"), 4: ("#186ccf", "#e3f2fd"), 3: ("#f39c12", "#fef5e7"), 2: ("#e74c3c", "#fadbd8") }
            txt_c, bg_c = color_map.get(item.idEstadoCons, ("#7f8c8d", "#f5f6fa"))
            badge = ctk.CTkFrame(row, fg_color=bg_c, corner_radius=10, height=26)
            badge.place(relx=self.col_map["CONSERV."], rely=0.5, anchor="center")
            ctk.CTkLabel(badge, text=str(item.idEstadoCons), font=("Arial", 13, "bold"), text_color=txt_c).pack(padx=12, pady=1)

            # 11. UBICACIÓN
            ctk.CTkLabel(row, text=getattr(item, 'nombre_laboratorio', '-'), font=("Arial", 11)).place(relx=self.col_map["UBICACIÓN"], rely=0.5, anchor="w")

            # 12. PISO
            ctk.CTkLabel(row, text=item.pisoInstrumento or "-", font=("Arial", 10), text_color="#7f8c8d").place(relx=self.col_map["PISO"], rely=0.5, anchor="w")

            # 13. ACCIONES (Diseño Botón Premium Unificado)
            acts_btn = ctk.CTkOptionMenu(
                row, values=["✏️ Editar", "🗑️ Eliminar"],
                width=110, height=32, corner_radius=16, # Bordes totalmente redondeados estilo píldora
                font=("Arial", 12, "bold"), text_color="#ffffff",
                fg_color="#8abef2", button_color="#8abef2", button_hover_color="#2c3e50",
                dropdown_fg_color="#ffffff", dropdown_text_color="#2c3e50", dropdown_hover_color="#f1f7ff",
                dropdown_font=("Arial", 12, "bold")
            )
            acts_btn.configure(command=lambda val, inst=item, btn=acts_btn: self.handle_action(val, inst, btn))
            acts_btn.set("⚙️ Acción")
            acts_btn.place(relx=self.col_map["ACCIONES"], rely=0.5, anchor="center")

            widgets_para_hover = [row] + list(row.winfo_children())
            
            # También capturamos nietos (como lo que hay dentro de los frames de imagen y badges)
            for child in list(row.winfo_children()):
                if isinstance(child, (ctk.CTkFrame, ctk.CTkLabel)):
                    widgets_para_hover.extend(list(child.winfo_children()))
            
            # Aplicamos los eventos a todos los widgets recolectados
            for w in widgets_para_hover:
                w.bind("<Enter>", on_enter, add="+")
                w.bind("<Leave>", on_leave, add="+")

    def handle_action(self, choice, item, option_menu):
        """Maneja las acciones del Dropdown, y resetea el texto a '⚙️ Acción'"""
        option_menu.set("⚙️ Acción")
        if "Editar" in choice:
            print(f"Editando el ID {item.idInstrumento}")
        elif "Eliminar" in choice:
            print(f"Eliminar el ID {item.idInstrumento}")

    def filter_data(self, event=None):
        """Lógica para filtrar la tabla según el buscador"""
        query = self.search_entry.get().lower()
        print(f"Buscando: {query}")

    def on_show_legend(self):
        """Muestra una alerta/modal con la leyenda de estados de conservación"""
        from interfaces.components.mensajes import Alerts
        mensaje = (
            "5 = Nuevo\n"
            "4 = Bueno\n"
            "3 = Regular\n"
            "2 = Malo"
        )
        Alerts.show_info("Leyenda de Estados de Conservación", mensaje, master=self)

    def on_add_instrumento(self):
        """Abre el modal para agregar instrumento"""
        print("Abriendo modal para agregar instrumento...")

if __name__ == "__main__":
    app = ctk.CTk()
    app.geometry("1400x800")
    frame = InstrumentosFrame(app)
    frame.pack(fill="both", expand=True, padx=20, pady=20)
    app.mainloop()
