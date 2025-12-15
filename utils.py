import sys
import os


def get_resource_path(relative_path):
    """
    Obtiene la ruta absoluta de un recurso, funciona tanto en desarrollo como en PyInstaller.
    
    PyInstaller crea una carpeta temporal y almacena la ruta en _MEIPASS
    """
    try:
        # PyInstaller crea una carpeta temporal y almacena la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Si no está empaquetado, usa la ruta del directorio actual
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def get_app_data_path():
    """
    Obtiene la ruta del directorio de datos de la aplicación en AppData.
    Para bases de datos y archivos que necesitan persistir.
    """
    app_name = "CajaMaestra"
    
    if sys.platform == "win32":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
    else:
        base = os.path.expanduser("~/.local/share")
    
    app_data = os.path.join(base, app_name)
    
    # Crear directorio si no existe
    os.makedirs(app_data, exist_ok=True)
    
    return app_data
