import os
import sys

def get_base_path():
    """Devuelve la ruta de la carpeta donde vive el .exe o el script."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def get_storage_path(relative_path):
    """Devuelve una ruta absoluta en una carpeta persistente para fotos."""
    base = get_base_path()
    full_path = os.path.join(base, relative_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    return full_path

def get_resource_path(relative_path):
    """Para leer iconos e imágenes que vienen DENTRO del .exe (solo lectura)."""
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    return os.path.join(base, relative_path)
