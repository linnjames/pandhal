from odoo import api, fields, models, _
from odoo.exceptions import Warning
import requests
from io import BytesIO
import base64
import tempfile
import pytz
from datetime import datetime
from reportlab.pdfgen import canvas

class PrintOrder(models.Model):
    _name = 'pos.printer'


    printer_name = fields.Char(string="Printer Name")
    ip_address = fields.Char(string="IP")
    category_ids = fields.Many2many('product.category', string="Category")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)

    @staticmethod
    def create_pdf(receipt_number, floor, table, employee_name, employee_role, category_name, products):
        # Create a new PDF file
        pdf_file = tempfile.NamedTemporaryFile(delete=False)
        pdf_path = pdf_file.name
        india_timezone = pytz.timezone('Asia/Kolkata')
        current_date_time = datetime.now(india_timezone)
        current_time = current_date_time.strftime('%d-%m-%Y %H:%M:%S')

        # Generate the receipt using ReportLab
        c = canvas.Canvas(pdf_path)
        c.setFont("Helvetica", 25)
        c.drawString(100, 800, "Receipt Number: {}".format(receipt_number))
        c.drawString(100, 750, "Time: {}".format(current_time))
        c.drawString(100, 700, "Table: {}".format(table))
        c.drawString(100, 650, "Floor: {}".format(floor))
        c.drawString(100, 600, "Employee Name: {}".format(employee_name))
        c.drawString(100, 550, "Employee Role: {}".format(employee_role))
        c.drawString(100, 500, "Order Lines:{}".format(category_name))
        y = 450
        for product, quantity, note in products:
            c.drawString(150, y, "- {}: {}".format(product, quantity))
            c.drawString(150, y - 25, "{}".format(note))
            y -= 50  # Move down to the next line
            # if y < 100:  # If we reach the bottom of the page, start a new one
            #     c.showPage()
            #     c.setFont("Helvetica", 25)
            #     c.drawString(100, 800, "Receipt Number: {}".format(receipt_number))
            #     c.drawString(100, 750, "Table: {}".format(table))
            #     c.drawString(100, 700, "Floor: {}".format(floor))
            #     c.drawString(100, 650, "Employee Name: {}".format(employee_name))
            #     c.drawString(100, 600, "Employee Role: {}".format(employee_role))
            #     c.drawString(100, 550, "Order Lines:{}".format(category_name))
            #     y = 500

        c.save()

        # Return the path to the new PDF file
        return pdf_path

    @api.model
    def current_kot_print(self, data):
        # Get the receipt information
        receipt_number = data['receipt_number']
        floor = data['floor']
        table = data['table']
        session = data['session']
        employee_name = data['employee_name']
        employee_role = data['employee_role']
        orderlines = data['orderlines']
        category_dict = {}
        printer_dict = {}
        printer_name = 0
        for item in orderlines:
            product = item[0]
            quantity = item[1]
            pos_category_name = item[2]
            note = item[3]
            category_id = item[4]
            pdt_categ_id = self.env['product.category'].search([('id', '=', category_id)])
            items = self.env['pos.printer'].search([('category_ids', 'in', category_id)])
            printerIP = items.ip_address
            category_name = pdt_categ_id.name
            for item in items:
                printer_dict[category_name] = item.printer_name

            if category_name in category_dict:
                category_dict[category_name].append((product, quantity, note))
            else:
                category_dict[category_name] = [(product, quantity, note)]

        for category_name, products in category_dict.items():
            if category_name in printer_dict:
                printer_name = printer_dict[category_name]
            else:
                printer_name = 0

            if (printer_name != 0):
                for count in range(2):
                    # print("pdf details",receipt_number, floor, table, employee_name, employee_role,category_name, products)
                    pdf_path = self.create_pdf(receipt_number, floor, table, employee_name, employee_role, category_name, products)
                    # pos_session = self.env['pos.session'].browse(session)
                    # url = "http://%s/print/from-pdf", % pos_config.ip_address
                    url = "http://{}/print/from-pdf".format(printerIP)
                    files = [('PdfFile', ('Odoo1111.pdf', open(pdf_path, 'rb'), 'application/pdf'))]
                    payload = {'PrinterPath': printer_name, 'Copies': '1'}
                    headers = {}

                    response = requests.request("POST", url, headers=headers, data=payload, files=files)

        return {'result': 'success'}