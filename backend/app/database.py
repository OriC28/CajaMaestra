from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
import os
import sys
import shutil

# Función para obtener la ruta correcta en PyInstaller
def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Función para obtener la ruta de datos de la aplicación
def get_app_data_path():
    if sys.platform == "win32":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
    else:
        base = os.path.expanduser("~/.local/share")
    app_data = os.path.join(base, "CajaMaestra")
    os.makedirs(app_data, exist_ok=True)
    return app_data

# Ruta de la base de datos en AppData para persistencia
DATABASE_PATH = os.path.join(get_app_data_path(), 'cajamaestra.db')

# Si la base de datos no existe en AppData, copiar la plantilla
if not os.path.exists(DATABASE_PATH):
    template_db = get_resource_path('backend/cajamaestra.db')
    if os.path.exists(template_db):
        shutil.copy(template_db, DATABASE_PATH)

engine = create_engine(
    f"sqlite:///{DATABASE_PATH}")
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


def create_db_and_tables():
    """
    Inicia la base de datos y crea sus respectivas tablas si no existen.

    Nota: Requiere que todos los modelos sean importados.
    """
    Base.metadata.create_all(engine)
