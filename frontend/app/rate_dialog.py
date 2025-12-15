from frontend.app.api_client import create_rate, get_today_rate
from frontend.app.utils.resource_path import get_resource_path

from PyQt6 import QtWidgets
from PyQt6 import uic
from asyncio import run


class RateDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi(get_resource_path('frontend/ui/rate_dialog.ui'), self)
        self.acceptButton.clicked.connect(self.accept_rate)
        self.rate = self.get_rate()

    def get_rate(self):
        result = run(get_today_rate())
        if result['status'] == 200 and result['data']['rate']:
            return result['data']['rate']

    def accept_rate(self):
        rate = self.rateSpinBox.value()
        if rate <= 0 and rate != "":
            QtWidgets.QMessageBox.warning(
                self, "Error", "La tasa de cambio debe ser mayor a 0.")
            return

        result = run(create_rate(rate))
        if result['status'] == 200:
            QtWidgets.QMessageBox.information(
                self, "Éxito", f"Tasa de cambio actualizada a Bs. {rate}")
            self.accept()
        else:
            QtWidgets.QMessageBox.warning(
                self, "Error", result['msg'])
        self.close()
