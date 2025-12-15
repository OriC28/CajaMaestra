from PyQt6.QtGui import QCursor
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
from asyncio import run
from PyQt6 import uic

from frontend.app.api_client import create_sale
from frontend.app.utils.resource_path import get_resource_path


class PaymentDialog(QtWidgets.QDialog):
    def __init__(self, sale: float, rate: float):
        super().__init__()
        self.sale = sale
        self.rate = rate
        self.missing = self.sale
        self.payments = {'total_usd': self.sale, 'payments': []}
        self.table_row = []
        uic.loadUi(get_resource_path('frontend/ui/payment_dialog.ui'), self)
        self.set_column_width()
        self.addPaymentButton.clicked.connect(self.add_payment)
        self.closeSaleButton.clicked.connect(self.close_sale)
        self.closeSaleButton.setEnabled(False)
        self.set_sale()

    def set_column_width(self):
        self.paymentTableWidget.setColumnWidth(0, 100)
        self.paymentTableWidget.setColumnWidth(1, 200)
        self.paymentTableWidget.setColumnWidth(0, 200)

    def set_sale(self):
        self.totalSaleLabel.setText(f"$ {self.sale}")
        self.missingLabel.setText(f"$ {self.sale}")

    def get_method(self):
        return self.methodComboBox.currentText()

    def get_amount(self):
        amount = float(self.amountSpinBox.value())
        if amount > self.sale:
            QtWidgets.QMessageBox.warning(
                self, "Error", "El monto ingresado es mayor al total de la venta.")
            return

        if amount == 0.0:
            QtWidgets.QMessageBox.warning(
                self, "Error", "El monto ingresado no puede ser 0.")
            return

        return amount

    def recovery_api_method(self, methods: dict, method: str):
        for key, value in methods.items():
            if value == method:
                return key
        return None

    def add_payment(self):
        method = self.get_method()
        amount = self.get_amount()
        amount_dolar = 0

        methods = {
            'zelle': 'Zelle',
            'usd_efectivo': 'USD Efectivo',
            'binance_pay': 'Binance Pay',
            'pago_movil': 'Pago Móvil',
            'punto_venta': 'Punto de Venta',
            'bs_efectivo': 'Bs Efectivo'
        }

        if amount:
            if method in ['Pago Móvil', 'Punto de Venta', 'Bs Efectivo']:
                amount_dolar = amount
                amount = amount_dolar*self.rate
            else:
                amount_dolar = amount

            self.missing -= amount_dolar
            self.missingLabel.setText(f"$ {self.missing}")
            self.payments['payments'].append(
                {'method': self.recovery_api_method(methods, method), 'native_amount': amount})
            self.table_row.append(
                {'method': method, 'amount': amount, 'amount_dolar': amount_dolar})

            self.fill_table(self.table_row)
            if self.missing == 0:
                self.closeSaleButton.setCursor(
                    QCursor(Qt.CursorShape.PointingHandCursor))
                self.closeSaleButton.setEnabled(True)

    def fill_table(self, table_row=[]):
        self.paymentTableWidget.setRowCount(len(table_row))
        for i, table_row in enumerate(table_row):
            item_method = QtWidgets.QTableWidgetItem(table_row['method'])
            item_amount = QtWidgets.QTableWidgetItem(
                f"{table_row['amount']}")
            item_amount_dolar = QtWidgets.QTableWidgetItem(
                f"{table_row['amount_dolar']}")

            self.paymentTableWidget.setItem(i, 0, item_method)
            self.paymentTableWidget.setItem(i, 1, item_amount)
            self.paymentTableWidget.setItem(i, 2, item_amount_dolar)

    def close_sale(self):
        result = run(create_sale(self.payments))
        if result['status'] == 200:
            QtWidgets.QMessageBox.information(
                self, "Éxito", "Venta realizada con éxito.")
        else:
            QtWidgets.QMessageBox.warning(
                self, "Error", result['msg'])
        self.close()
