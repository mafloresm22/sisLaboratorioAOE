import customtkinter as ctk
from PIL import Image
import os
from services.unidad.unidad import UnidadService
from interfaces.windows.unidad.create_unidad import CreateUnidadModal
from interfaces.windows.unidad.edit_unidad import EditUnidadModal
from interfaces.windows.unidad.delete_unidad import DeleteUnidadModal

# Directorio de iconos de botones
_BUTTON_ICONS_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "..", "assets", "icons", "buttons"
))

class UnidadItem(ctk.CTkFrame):
    """Componente que representa un Círculo con Icono y Nombre debajo."""
    def __init__(self, master, title, icon_path, bg_color, hover_color, on_edit=None, on_delete=None):
        # Frame contenedor invisible
        super().__init__(master, fg_color="transparent")
        self.bg_color = bg_color
        self.hover_color = hover_color
        
        # 1. Forma de la Unidad
        self.circle_btn = ctk.CTkFrame(
            self, width=140, height=140, corner_radius=70, 
            fg_color=bg_color, border_width=0
        )
        self.circle_btn.pack(pady=(0, 15))
        self.circle_btn.pack_propagate(False) 
        
        # 2. El Icono dentro del círculo (Usando CTkImage)
        try:
            pil_img = Image.open(icon_path)
            ctk_img = ctk.CTkImage(light_image=pil_img, size=(65, 65))
            self.lbl_icon = ctk.CTkLabel(self.circle_btn, image=ctk_img, text="")
        except Exception:
            # Fallback en caso de que no se encuentre el icono
            self.lbl_icon = ctk.CTkLabel(self.circle_btn, text="📦", font=("Arial", 60))
            
        self.lbl_icon.place(relx=0.5, rely=0.5, anchor="center")
        
        # 3. El Nombre debajo del círculo
        self.lbl_name = ctk.CTkLabel(
            self, text=title, font=("Arial", 16, "bold"), 
            text_color="#2c3e50", wraplength=170, justify="center"
        )
        self.lbl_name.pack()

        # 4. Botones de Acción
        # Icono Editar
        edit_img = ctk.CTkImage(
            Image.open(os.path.join(_BUTTON_ICONS_DIR, "edit_3808637.png")), size=(22, 22)
        )
        self.btn_edit = ctk.CTkButton(
            self.circle_btn, text="", image=edit_img, width=40, height=40, corner_radius=12,
            fg_color="#f39c12", hover_color="#e67e22", 
            command=on_edit, border_width=2, border_color="white"
        )
        self.btn_edit.place(relx=0.15, rely=0.18, anchor="center")

        # Icono Eliminar
        delete_img = ctk.CTkImage(
            Image.open(os.path.join(_BUTTON_ICONS_DIR, "delete_2550318.png")), size=(22, 22)
        )
        self.btn_delete = ctk.CTkButton(
            self.circle_btn, text="", image=delete_img, width=40, height=40, corner_radius=12,
            fg_color="#e74c3c", hover_color="#c0392b",
            command=on_delete, border_width=2, border_color="white"
        )
        self.btn_delete.place(relx=0.85, rely=0.18, anchor="center")

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
        self.header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 20))
        
        self.lbl_title = ctk.CTkLabel(
            self.header, text="Unidades de Medida", 
            font=("Arial", 32, "bold"), text_color="#2c3e50"
        )
        self.lbl_title.pack(side="left")

        add_img = ctk.CTkImage(
            Image.open(os.path.join(_BUTTON_ICONS_DIR, "add_6902311.png")), size=(20, 20)
        )
        self.btn_add = ctk.CTkButton(
            self.header, text=" Agregar Unidad", image=add_img, width=180, height=45,
            fg_color="#186ccf", hover_color="#145cb3",
            font=("Arial", 15, "bold"), corner_radius=10,
            command=self.on_add_unit
        )
        self.btn_add.pack(side="right")

        # 2. CONTENEDOR DE CÍRCULOS (Scrollable)
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
        
        # Paleta de colores variada y mapeo de iconos profesionales
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
        icons_dir = os.path.join(base_path, "assets", "icons", "unidad_img")
        
        colors = [
            ("#3498db", "#2980b9", os.path.join(icons_dir, "ruler_7927154.png")),
            ("#2ecc71", "#27ae60", os.path.join(icons_dir, "5672649.png")),
            ("#e67e22", "#d35400", os.path.join(icons_dir, "package_1274687.png")),
            ("#9b59b6", "#8e44ad", os.path.join(icons_dir, "8892765.png")),
            ("#34495e", "#2c3e50", os.path.join(icons_dir, "meter_3348866.png")),
            ("#1abc9c", "#16a085", os.path.join(icons_dir, "3016800.png")),
        ]

        if not unidades:
            # Estado vacío
            empty_frame = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
            empty_frame.grid(row=0, column=0, columnspan=5, pady=100)
            
            show_img = ctk.CTkImage(
                Image.open(os.path.join(_BUTTON_ICONS_DIR, "show_8358982.png")), size=(80, 80)
            )
            ctk.CTkLabel(empty_frame, text="", image=show_img).pack()
            ctk.CTkLabel(
                empty_frame, text="No hay unidades registradas", 
                font=("Arial", 20, "bold"), text_color="#bdc3c7"
            ).pack(pady=20)
        else:
            for i, unit in enumerate(unidades):
                col = i % 5
                row = i // 5
                
                color_conf = colors[i % len(colors)]
                
                item = UnidadItem(
                    self.scroll_container,
                    title=unit.nombreUnidad,
                    icon_path=color_conf[2],
                    bg_color=color_conf[0],
                    hover_color=color_conf[1],
                    on_edit=lambda u=unit: self.on_edit_unit(u),
                    on_delete=lambda u=unit: self.on_delete_unit(u)
                )
                item.grid(row=row, column=col, padx=20, pady=30, sticky="n")

    def on_add_unit(self):
        modal = CreateUnidadModal(self.winfo_toplevel(), parent_view=self)

    def on_edit_unit(self, unit):
        modal = EditUnidadModal(self.winfo_toplevel(), unit_data=unit, parent_view=self)

    def on_delete_unit(self, unit):
        modal = DeleteUnidadModal(self.winfo_toplevel(), unit_data=unit, parent_view=self)
