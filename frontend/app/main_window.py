from frontend.app.api_client import get_today_rate, get_report
from frontend.app.utils.locale_date import set_date
from frontend.app.utils.resource_path import get_resource_path
from frontend.app.payment_dialog import PaymentDialog
from frontend.app.report_dialog import ReportDialog
from frontend.app.rate_dialog import RateDialog
from frontend.app.history_dialog import HistoryDialog

from PyQt6.QtGui import QCursor
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
from asyncio import run
from PyQt6 import uic


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(get_resource_path('frontend/ui/main_window.ui'), self)
        self.rate = 0
        self.init()
        self.set_rate()
        self.showMaximized()

    def init(self):
        self.configButton.clicked.connect(self.config)
        self.closeBoxButton.clicked.connect(self.report)
        self.btn_charge.clicked.connect(self.payments)
        self.historyButton.clicked.connect(self.history)

        self.displayLineEdit.setText("$0.00")
        self.enable_btn_charge(self.displayLineEdit.text())

        set_date(self, self.dateLabel, "Ventas de Hoy")
        self.init_rate()
        self.set_dashboard()
        self.set_key_pad()

    def set_rate(self):
        rate_dialog = RateDialog()
        if rate_dialog.rate:
            self.rate = rate_dialog.rate
        else:
            self.config()

    def config(self):
        rate_dialog = RateDialog()
        result = rate_dialog.exec()
        if result == QtWidgets.QDialog.DialogCode.Accepted:
            self.init_rate()
            self.set_dashboard()

    def set_dashboard(self):
        result = run(get_report())
        if result['status'] == 200:
            report = result['data']
            self.totalSalesLabel.setText(f"$ {report['total_sale_usd']}")
            self.zelleLabel.setText(f"$ {report['total_zelle']}")
            self.binanceLabel.setText(f"$ {report['total_binance_pay']}")
            self.cashLabel.setText(f"$ {report['total_usd']}")
            self.bsCashLabel.setText(f"Bs. {report['total_bs']}")
            self.totalMobilePaymentLabel.setText(
                f"Bs. {report['total_mobile_payment_bs']}")
            self.totalPointSaleLabel.setText(
                f"Bs. {report['total_point_of_sale_bs']}")

    def history(self):
        history_dialog = HistoryDialog()
        if history_dialog.sales is not None:
            history_dialog.fill_sales_table()
            history_dialog.exec()

    def payments(self):
        if self.rate == 0:
            QtWidgets.QMessageBox.warning(
                self, 'Error', 'No se puede realizar un cobro sin una tasa de cambio.')
            return
        payment_dialg = PaymentDialog(self.sale, self.rate)
        payment_dialg.exec()
        self.set_dashboard()

    def report(self):
        result = run(get_report())
        if result['status'] == 200:
            report = result['data']
            report_dialog = ReportDialog()
            report_dialog.set_data(report)
            report_dialog.exec()
        else:
            QtWidgets.QMessageBox.warning(
                self, "Error", result['msg'])

    def init_rate(self):
        result = run(get_today_rate())
        if result['status'] == 200 and result['data']['rate']:
            self.rate = result['data']['rate']
            print(f"Tasa de cambio: {self.rate}")
        else:
            QtWidgets.QMessageBox.warning(
                self, "Error", result['msg'])

    def set_display(self, key: str, clear_key: bool = False):
        current_display = self.displayLineEdit.text().replace("0.00", "")

        if key == '.' and key in current_display:
            return

        if current_display.startswith('$.'):
            current_display = current_display.replace('$.', '$0.')

        if clear_key:
            current_display = current_display[:len(current_display)-1]
            self.displayLineEdit.setText(current_display)
            if current_display == "":
                self.displayLineEdit.setText("$0.00")
                self.enable_btn_charge(self.displayLineEdit.text())
            return

        else:
            current_display += key
            self.displayLineEdit.setText(current_display)

        if current_display != '$.':
            self.enable_btn_charge(current_display)

    def set_key_pad(self):

        self.btn_0.clicked.connect(lambda _: self.set_display("0"))
        self.btn_1.clicked.connect(lambda _: self.set_display("1"))
        self.btn_2.clicked.connect(lambda _: self.set_display("2"))
        self.btn_3.clicked.connect(lambda _: self.set_display("3"))
        self.btn_4.clicked.connect(lambda _: self.set_display("4"))
        self.btn_5.clicked.connect(lambda _: self.set_display("5"))
        self.btn_6.clicked.connect(lambda _: self.set_display("6"))
        self.btn_7.clicked.connect(lambda _: self.set_display("7"))
        self.btn_8.clicked.connect(lambda _: self.set_display("8"))
        self.btn_9.clicked.connect(lambda _: self.set_display("9"))
        self.btn_dot.clicked.connect(lambda _: self.set_display("."))
        self.btn_c.clicked.connect(lambda _: self.set_display("", True))

    def enable_btn_charge(self, sale: str):
        sale = sale[1:]
        try:
            self.sale = float(sale)
            if self.sale != 0:
                self.btn_charge.setEnabled(True)
                self.btn_charge.setCursor(
                    QCursor(Qt.CursorShape.PointingHandCursor))
            else:
                self.btn_charge.setEnabled(False)
        except ValueError:
            QtWidgets.QMessageBox.warning(
                self, "Error", "No se pudo realizar el cobro. Ingrese un monto válido.")
            self.btn_charge.setEnabled(False)
