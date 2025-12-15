from frontend.app.utils.locale_date import set_date
from frontend.app.utils.resource_path import get_resource_path

from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from PyQt6 import QtWidgets
from PyQt6 import uic
import os
import sys


class ReportDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi(get_resource_path('frontend/ui/report_dialog.ui'), self)
        self.reportTextEdit.setReadOnly(True)
        self.company_name = None
        set_date(self, self.reportTitleLabel, "Cierre de Caja de Hoy")
        self.printButton.clicked.connect(self.print_ticket)
        self.last_report_data = None
        self.last_company_name = None

    def print_ticket(self):
        if not self.last_company_name and not self.last_report_data:
            QtWidgets.QMessageBox.warning(
                self, "Error", "No hay datos para mostrar.")
            return

        data = self.last_report_data

        try:
            title_font = ImageFont.truetype('arialbd.ttf', 24)
            font = ImageFont.truetype('arial.ttf', 18)
            small_font = ImageFont.truetype('arial.ttf', 14)
        except Exception:
            title_font = ImageFont.load_default()
            font = ImageFont.load_default()
            small_font = ImageFont.load_default()

        width = 384
        padding_x = 12
        padding_y = 12
        line_spacing = 8

        center_lines = [f"{self.last_company_name}",
                        f"{datetime.now().date()}"]

        items = [
            ("Total Ventas:", f"{data.get('sale_count', 0)}"),
            ("Total Ventas (USD):", f"$ {data.get('total_sale_usd', 0)}"),
            ("Total Efectivo (USD):", f"$ {data.get('total_usd', 0)}"),
            ("Total Pagos Binance:", f"$ {data.get('total_binance_pay', 0)}"),
            ("Total Zelle:", f"$ {data.get('total_zelle', 0)}"),
            ("Total Ventas (Bs):", f"Bs. {data.get('total_bs', 0)}"),
            ("Efectivo (Bs):", f"Bs. {data.get('total_bs_efectivo', 0)}"),
            ("Pago Móvil (Bs):",
             f"Bs. {data.get('total_mobile_payment_bs', 0)}"),
            ("Punto de Venta (Bs):",
             f"Bs. {data.get('total_point_of_sale_bs', 0)}"),
        ]

        total_height = padding_y

        for line in center_lines:
            bbox = title_font.getbbox(line) if hasattr(
                title_font, 'getbbox') else title_font.getsize(line)
            h = bbox[3] - bbox[1] if isinstance(bbox, tuple) and len(
                bbox) >= 4 else (bbox[1] if isinstance(bbox, tuple) else bbox[1])
            total_height += h + line_spacing

        total_height += 8

        for label, value in items:
            bbox_label = font.getbbox(label) if hasattr(
                font, 'getbbox') else font.getsize(label)
            bbox_value = font.getbbox(value) if hasattr(
                font, 'getbbox') else font.getsize(value)
            h_label = bbox_label[3] - bbox_label[1] if isinstance(
                bbox_label, tuple) and len(bbox_label) >= 4 else bbox_label[1]
            h_value = bbox_value[3] - bbox_value[1] if isinstance(
                bbox_value, tuple) and len(bbox_value) >= 4 else bbox_value[1]
            total_height += max(h_label, h_value) + line_spacing

        total_height += padding_y

        try:
            img = Image.new(
                'RGB', (width, max(200, total_height)), color='white')
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Error", f"Error al crear la imagen del ticket: {e}")
            return

        draw = ImageDraw.Draw(img)

        y = padding_y

        for line in center_lines:
            font_to_use = title_font
            bbox = font_to_use.getbbox(line) if hasattr(
                font_to_use, 'getbbox') else font_to_use.getsize(line)
            text_w = bbox[2] - \
                bbox[0] if isinstance(bbox, tuple) and len(
                    bbox) >= 4 else bbox[0]
            x = (width - text_w) // 2
            draw.text((x, y), line, fill=(0, 0, 0), font=font_to_use)
            h = bbox[3] - bbox[1] if isinstance(bbox, tuple) and len(
                bbox) >= 4 else (bbox[1] if isinstance(bbox, tuple) else bbox[1])
            y += h + line_spacing

        draw.line([(padding_x, y), (width - padding_x, y)], fill=(0, 0, 0))
        y += line_spacing + 2

        for label, value in items:
            # label
            bbox_label = font.getbbox(label) if hasattr(
                font, 'getbbox') else font.getsize(label)
            label_w = bbox_label[2] - bbox_label[0] if isinstance(
                bbox_label, tuple) and len(bbox_label) >= 4 else bbox_label[0]
            bbox_value = font.getbbox(value) if hasattr(
                font, 'getbbox') else font.getsize(value)
            value_w = bbox_value[2] - bbox_value[0] if isinstance(
                bbox_value, tuple) and len(bbox_value) >= 4 else bbox_value[0]

            x_label = padding_x
            x_value = width - padding_x - value_w

            draw.text((x_label, y), label, fill=(0, 0, 0), font=font)
            draw.text((x_value, y), value, fill=(0, 0, 0), font=font)

            h = max((bbox_label[3] - bbox_label[1]) if isinstance(bbox_label, tuple) and len(bbox_label) >= 4 else bbox_label[1],
                    (bbox_value[3] - bbox_value[1]) if isinstance(bbox_value, tuple) and len(bbox_value) >= 4 else bbox_value[1])
            y += h + line_spacing

        # Guardar imagen en AppData/CajaMaestra/tickets
        try:
            # Usar AppData para persistencia
            if sys.platform == "win32":
                base = os.environ.get("APPDATA", os.path.expanduser("~"))
            else:
                base = os.path.expanduser("~/.local/share")
            app_data = os.path.join(base, "CajaMaestra")
            tickets_dir = os.path.join(app_data, 'tickets')
            os.makedirs(tickets_dir, exist_ok=True)
            filename = f"ticket_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"
            save_path = os.path.join(tickets_dir, filename)
            img.save(save_path)
            QtWidgets.QMessageBox.information(
                self, "Éxito", f"Ticket generado: {save_path}")
        except Exception as e:
            QtWidgets.QMessageBox.warning(
                self, "Error", f"Error al generar el ticket: {e}")

    def set_data(self, data: dict, company_name: str = "Caja Maestra"):
        if len(data) == 0:
            self.reportTextEdit.setText("No hay datos para mostrar.")
            return
        self.last_report_data = data
        self.last_company_name = company_name

        self.reportTextEdit.setText(f"""
        ----------------------------------------------
        Empresa: {company_name}\n
        Fecha: {datetime.now().date()}\n
        Total Ventas Realizadas: {data['sale_count']}
        _______________________________________________

        Total Ventas (USD): $ {data['total_sale_usd']}
        _______________________________________________\n
        Total Efectivo (USD): $ {data['total_usd']}\n
        Total Pagos con Binance: $ {data['total_binance_pay']}\n
        Total Zelle: $ {data['total_zelle']}
        _______________________________________________

        Total Ventas (Bs): Bs. {data['total_bs']}
        _______________________________________________\n
        Total Efectivo (Bs): Bs. {data['total_bs_efectivo']}\n
        Total Pago Móvil: Bs. {data['total_mobile_payment_bs']}\n
        Total Punto de Venta: Bs. {data['total_point_of_sale_bs']}
        ---------------------------------------------
    """)
