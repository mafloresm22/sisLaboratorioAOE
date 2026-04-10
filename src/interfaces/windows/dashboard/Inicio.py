import customtkinter as ctk
from PIL import Image
import os
from services.reportes.reportes import ReporteService
from utils.paths import get_resource_path

class ChartBar(ctk.CTkFrame):
    """Un componente de barra interactiva personalizada."""
    def __init__(self, master, label, value, max_value, color="#186ccf", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.grid_columnconfigure(1, weight=1)
        
        # Etiqueta
        ctk.CTkLabel(self, text=label, font=("Arial", 11), width=160, anchor="w").grid(row=0, column=0, padx=(10, 5))
        
        # Contenedor de la barra
        self.bar_bg = ctk.CTkFrame(self, height=18, fg_color="#f0f0f0", corner_radius=10)
        self.bar_bg.grid(row=0, column=1, sticky="ew", padx=10, pady=10)
        
        # La barra de progreso
        percentage = (value / max_value) if max_value > 0 else 0
        self.bar_fill = ctk.CTkFrame(self.bar_bg, height=18, fg_color=color, corner_radius=10, width=0)
        self.bar_fill.place(relheight=1, relwidth=percentage)
        
        # Valor al final
        ctk.CTkLabel(self, text=str(int(value)), font=("Arial", 12, "bold"), width=50).grid(row=0, column=2, padx=(5, 15))

class InicioFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="#f5f6fa", corner_radius=15)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- HEADER ---
        self.header = ctk.CTkFrame(self, fg_color="white", height=80, corner_radius=15)
        self.header.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        self.header.grid_propagate(False)
        
        ctk.CTkLabel(self.header, text="Inicio", font=("Arial", 26, "bold"), text_color="#2c3e50").pack(side="left", padx=30, pady=20)

        # --- CONTENIDO SCROLLABLE ---
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.scroll.grid_columnconfigure((0, 1), weight=1)

        self.load_reports()

    def create_card(self, title, row, col, rowspan=1):
        card = ctk.CTkFrame(self.scroll, fg_color="white", corner_radius=15, border_width=1, border_color="#dcdde1")
        card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew", rowspan=rowspan)
        
        ctk.CTkLabel(card, text=title, font=("Arial", 16, "bold"), text_color="#353b48").pack(pady=15, padx=20, anchor="w")
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        return content

    def load_reports(self):
        # Limpiar
        for child in self.scroll.winfo_children():
            child.destroy()

        # 2. Resumen General (Tarjetas Individuales en la parte superior)
        resumen = ReporteService.get_resumen_general()
        metrics_container = ctk.CTkFrame(self.scroll, fg_color="transparent")
        metrics_container.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5)
        metrics_container.grid_columnconfigure((0, 1, 2, 3), weight=1)

        metrics = [
            ("Instrumentos", resumen.get("instrumentos", 0), "#186ccf", "assets/icons/dashboard/11458663_inventario.png"),
            ("Usuarios", resumen.get("usuarios", 0), "#f1c40f", "assets/icons/dashboard/7816987_usuario.png"),
            ("Laboratorios", resumen.get("laboratorios", 0), "#e67e22", "assets/icons/dashboard/7918318_laboratorio.png"),
            ("Préstamos Activos", resumen.get("prestamos_activos", 0), "#e74c3c", "assets/icons/dashboard/772938_prestamo.png")
        ]
        
        for i, (name, val, color, icon_path) in enumerate(metrics):
            card = ctk.CTkFrame(metrics_container, fg_color="white", corner_radius=15, border_width=1, border_color="#dcdde1", height=100)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            card.grid_propagate(False)

            # Icono + Valor en fila
            try:
                img = Image.open(get_resource_path(icon_path))
                ctk_icon = ctk.CTkImage(light_image=img, size=(30, 30))
                ctk.CTkLabel(card, image=ctk_icon, text="").pack(side="left", padx=(15, 10))
            except: pass

            val_frame = ctk.CTkFrame(card, fg_color="transparent")
            val_frame.pack(side="left", fill="both", expand=True)
            
            ctk.CTkLabel(val_frame, text=str(val), font=("Arial", 20, "bold"), text_color=color).pack(anchor="w", pady=(20, 0))
            ctk.CTkLabel(val_frame, text=name, font=("Arial", 11), text_color="#7f8c8d").pack(anchor="w")

        # 3. Ranking de Préstamos
        rank_data = ReporteService.get_instrumentos_mas_prestados(limit=8)
        content_rank = self.create_card("Top Instrumentos más Pedidos", 1, 0)
        if rank_data:
            max_val = max([d[1] for d in rank_data]) if rank_data else 1
            for label, val in rank_data:
                ChartBar(content_rank, label[:35], val, max_val, color="#186ccf").pack(fill="x", pady=5)

        # 4. Distribución por Laboratorio
        lab_data = ReporteService.get_instrumentos_por_laboratorio()
        if lab_data:
            content_lab = self.create_card("Distribución por Laboratorio", 1, 1)
            max_lab = max([float(d[1]) for d in lab_data]) if lab_data else 1
            for label, val in lab_data:
                ChartBar(content_lab, label, val, max_lab, color="#9b59b6").pack(fill="x", pady=5)

        # 5. Estado de Conservación
        cons_data = ReporteService.get_estado_conservacion_stats()
        if cons_data:
            content_cons = self.create_card("Resumen de Conservación", 2, 0)
            content_cons.master.grid_configure(columnspan=2)
            
            # Mostrar barras en horizontal/grid para que no se vea vacío
            items_frame = ctk.CTkFrame(content_cons, fg_color="transparent")
            items_frame.pack(fill="both", expand=True)
            items_frame.grid_columnconfigure((0, 1), weight=1)
            
            max_cons = max([int(d[1]) for d in cons_data]) if cons_data else 1
            colors = {"NUEVO": "#2ecc71", "BUENO": "#3498db", "REGULAR": "#f1c40f", "MALO": "#e74c3c"}
            
            for index, (label, val) in enumerate(cons_data):
                r, c = divmod(index, 2)
                color = colors.get(label.upper(), "#95a5a6")
                bar = ChartBar(items_frame, label, val, max_cons, color=color)
                bar.grid(row=r, column=c, sticky="ew", padx=10)


