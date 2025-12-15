from frontend.app.main_window import MainWindow
from backend.app.main import run_fastapi

import threading
import time
from PyQt6 import QtWidgets


if __name__ == '__main__':
    # Iniciar servidor FastAPI en hilo separado
    api_thread = threading.Thread(target=run_fastapi, daemon=True)
    api_thread.start()

    time.sleep(2)

    app = QtWidgets.QApplication([])
    window = MainWindow()
    app.exec()
