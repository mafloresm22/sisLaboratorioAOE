import customtkinter as ctk
from PIL import Image
from services.unidad.unidad import UnidadService

class UnidadItem(ctk.CTkFrame):
    """Componente que representa un Círculo con Icono y Nombre debajo."""
    def __init__(self, master, title, icon_text, bg_color, hover_color, on_edit=None, on_delete=None):
        # Frame contenedor invisible
        super().__init__(master, fg_color="transparent")
        self.bg_color = bg_color
        self.hover_color = hover_color
        
        # 1. El Círculo 
        self.circle_btn = ctk.CTkFrame(
            self, width=160, height=160, corner_radius=80, 
            fg_color=bg_color, border_width=0
        )
        self.circle_btn.pack(pady=(0, 15))
        self.circle_btn.pack_propagate(False) 
        
        # 2. El Icono dentro del círculo
        self.lbl_icon = ctk.CTkLabel(
            self.circle_btn, text=icon_text, font=("Segoe UI Emoji", 65),
            text_color="white"
        )
        self.lbl_icon.place(relx=0.5, rely=0.5, anchor="center")
        
        # 3. El Nombre debajo del círculo
        self.lbl_name = ctk.CTkLabel(
            self, text=title, font=("Arial", 16, "bold"), 
            text_color="#2c3e50", wraplength=170, justify="center"
        )
        self.lbl_name.pack()

        # 4. Botones de Acción
        self.btn_edit = ctk.CTkButton(
            self.circle_btn, text="✏️", width=45, height=45, corner_radius=12,
            fg_color="#f39c12", hover_color="#e67e22", font=("Segoe UI Emoji", 22),
            command=on_edit, border_width=2, border_color="white"
        )
        self.btn_edit.place(relx=0.85, rely=0.18, anchor="center")

        self.btn_delete = ctk.CTkButton(
            self.circle_btn, text="🗑️", width=45, height=45, corner_radius=12,
            fg_color="#e74c3c", hover_color="#c0392b", font=("Segoe UI Emoji", 22),
            command=on_delete, border_width=2, border_color="white"
        )
        self.btn_delete.place(relx=0.15, rely=0.18, anchor="center")

        self.circle_btn.bind("<Enter>", self._on_enter)
        self.circle_btn.bind("<Leave>", self._on_leave)
        self.lbl_icon.bind("<Enter>", self._on_enter)

    def _on_enter(self, event):
        self.circle_btn.configure(fg_color=self.hover_color)
        self.circle_btn.configure(cursor="hand2")

    def _on_leave(self, event):
        x, y = self.circle_btn.winfo_pointerxy()
        widget = self.circle_btn.winfo_containing(x, y)
        if widget not in [self.circle_btn, self.lbl_icon, self.btn_edit, self.btn_delete]:
            self.circle_btn.configure(fg_color=self.bg_color)
            self.circle_btn.configure(cursor="")

class UnidadFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="white", corner_radius=15)
        
        # Layout principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 1. CABECERA
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.grid(row=0, column=0, sticky="ew", padx=30, pady=(30, 20))
        
        self.lbl_title = ctk.CTkLabel(
            self.header, text="Unidades de Medida", 
            font=("Arial", 32, "bold"), text_color="#2c3e50"
        )
        self.lbl_title.pack(side="left")

        self.btn_add = ctk.CTkButton(
            self.header, text="➕ Agregar Unidad", width=160, height=45,
            fg_color="#186ccf", hover_color="#145cb3",
            font=("Arial", 15, "bold"), corner_radius=10,
            command=self.on_add_unit
        )
        self.btn_add.pack(side="right")

        # 2. SEPARADOR
        self.line = ctk.CTkFrame(self, fg_color="#f0f0f0", height=2)
        self.line.grid(row=0, column=0, sticky="ew", padx=30, pady=(100, 0))

        # 3. CONTENEDOR DE CÍRCULOS (Scrollable)
        self.scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        
        # Configurar 5 columnas para la cuadrícula de unidades
        for i in range(5):
            self.scroll_container.grid_columnconfigure(i, weight=1)
        
        self.load_unidades()

    def load_unidades(self):
        # Limpiar
        for child in self.scroll_container.winfo_children():
            child.destroy()
            
        unidades = UnidadService.get_all_unidades()
        
        # Paleta de colores variada
        colors = [
            ("#3498db", "#2980b9", "📏"), # Regla
            ("#2ecc71", "#27ae60", "🧪"), # Tubo
            ("#e67e22", "#d35400", "📦"), # Caja
            ("#9b59b6", "#8e44ad", "📐"), # Escuadra
            ("#34495e", "#2c3e50", "⚖️"), # Balanza
            ("#1abc9c", "#16a085", "🌡️"), # Termómetro
        ]

        if not unidades:
            # Estado vacío
            empty_frame = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
            empty_frame.grid(row=0, column=0, columnspan=5, pady=100)
            
            ctk.CTkLabel(empty_frame, text="🔍", font=("Arial", 80)).pack()
            ctk.CTkLabel(
                empty_frame, text="No hay unidades registradas", 
                font=("Arial", 20, "bold"), text_color="#bdc3c7"
            ).pack(pady=10)
        else:
            for i, unit in enumerate(unidades):
                col = i % 5
                row = i // 5
                
                color_conf = colors[i % len(colors)]
                
                item = UnidadItem(
                    self.scroll_container,
                    title=unit["nombreUnidad"],
                    icon_text=color_conf[2],
                    bg_color=color_conf[0],
                    hover_color=color_conf[1],
                    on_edit=lambda u=unit: print(f"Editar: {u['nombreUnidad']}"),
                    on_delete=lambda u=unit: print(f"Eliminar: {u['nombreUnidad']}")
                )
                item.grid(row=row, column=col, padx=20, pady=30, sticky="n")

    def on_add_unit(self):
        print("Abrir Modal Unidad")
