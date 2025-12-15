import sys
import os


def get_resource_path(relative_path):
    """
    Obtiene la ruta absoluta de un recurso para PyInstaller.
    """
    try:
        # PyInstaller crea una carpeta temporal y almacena la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Si no está empaquetado, usa la ruta del directorio actual
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
