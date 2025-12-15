from PyQt6 import QtWidgets
from PyQt6 import uic

from frontend.app.api_client import get_history
from frontend.app.utils.resource_path import get_resource_path
from asyncio import run


class HistoryDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi(get_resource_path('frontend/ui/history_dialog.ui'), self)
        self.sales = self.get_history_data()

    def get_history_data(self):
        result = run(get_history())
        if result['status'] == 200:
            sales = result['data']
            return sales
        else:
            QtWidgets.QMessageBox.warning(
                self, "Error", result['msg'])

    def fill_sales_table(self):
        total_amount = 0
        total_sales = 0
        self.historyTableWidget.setRowCount(len(self.sales))

        for i, table_row in enumerate(self.sales):
            item_date = QtWidgets.QTableWidgetItem(
                table_row['date'].split('T')[0])
            item_first_date = QtWidgets.QTableWidgetItem(
                table_row['first_sale_date'].split('T')[1].split('.')[0])
            item_last_date = QtWidgets.QTableWidgetItem(
                table_row['last_sale_date'].split('T')[1].split('.')[0])
            item_total_sales = QtWidgets.QTableWidgetItem(
                f"{table_row['total_sales']}")
            item_total_amount = QtWidgets.QTableWidgetItem(
                f"{table_row['total_amount']}")
            item_last_rate_used = QtWidgets.QTableWidgetItem(
                f"{table_row['last_rate_used']}")

            self.historyTableWidget.setItem(i, 0, item_date)
            self.historyTableWidget.setItem(i, 1, item_first_date)
            self.historyTableWidget.setItem(i, 2, item_last_date)
            self.historyTableWidget.setItem(i, 3, item_total_sales)
            self.historyTableWidget.setItem(i, 4, item_total_amount)
            self.historyTableWidget.setItem(i, 5, item_last_rate_used)

            total_sales += table_row['total_sales']
            total_amount += table_row['total_amount']

        self.totalAmountLabel.setText(f"Monto Total: ${total_amount}")
        self.totalSalesLabel.setText(f"Ventas Totales: {total_sales}")
