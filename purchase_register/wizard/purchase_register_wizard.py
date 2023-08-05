from io import BytesIO
from base64 import encodebytes
from datetime import datetime

import xlsxwriter
from odoo import models, fields


class PurchaseRegisterReportWizard(models.TransientModel):
    _name = "purchase.register.report.wizard"
    _description = "Purchase Register Report"

    MONTH_SELECTION = [
        ('01', 'January'),
        ('02', 'February'),
        ('03', 'March'),
        ('04', 'April'),
        ('05', 'May'),
        ('06', 'June'),
        ('07', 'July'),
        ('08', 'August'),
        ('09', 'September'),
        ('10', 'October'),
        ('11', 'November'),
        ('12', 'December')
    ]

    fileout = fields.Binary('File', readonly=True)
    fileout_filename = fields.Char('Filename', readonly=True)

    year_selection = [(str(year), str(year)) for year in range(2000, 2051)]

    month_selection = fields.Selection(selection=MONTH_SELECTION, string='Month')
    year = fields.Selection(selection=year_selection, string='Year')
    company_name = fields.Many2many('res.company', string="Company")

    def excel_action(self):
        month = self.month_selection
        year = str(self.year)  # Convert year to string
        company_ids = self.company_name.ids if self.company_name else []
        if not company_ids:
            all_companies = self.env['res.company'].search([])  # Fetch all companies
            company_ids = all_companies.ids

        # month_start_date = datetime.strptime(f"{year}-{month}-01", "%Y-%m-%d")
        # month_end_date = month_start_date.replace(day=31)

        records = self.env['purchase.order'].search([
            ('date_approve', '>=', f'{year}-{month}-01'),
            ('date_approve', '<=', f'{year}-{month}-31'),
            ('company_id', 'in', company_ids)

        ])

        for company_id in self.company_name.ids:
            company_name = self.env['res.company'].browse(company_id).name
        # self.generate_xlsx_report(workbook, month, year, records)
        print(records, 'records')
        file_io = BytesIO()
        workbook = xlsxwriter.Workbook(file_io)

        self.generate_xlsx_report(workbook, month, year, records, company_ids)

        workbook.close()
        fout = encodebytes(file_io.getvalue())

        datetime_string = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_name = 'Purchase Register Report'
        filename = '%s_%s' % (report_name, datetime_string)
        self.write({'fileout': fout, 'fileout_filename': filename})
        file_io.close()
        filename += '%2Exlsx'

        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': 'web/content/?model=' + self._name + '&id=' + str(
                self.id) + '&field=fileout&download=true&filename=' + filename,
        }

    def generate_xlsx_report(self, workbook, month, year, records, company_ids):
        print("hiiii", )
        center_head = workbook.add_format({'font_size': 14, 'align': 'center', 'font_color': 'black',
                                           'valign': 'vcenter', 'border': 1, 'bold': True})
        center_head.set_font_name('Times New Roman')
        center_head_1 = workbook.add_format({'font_size': 12, 'align': 'center', 'font_color': 'black',
                                             'valign': 'vcenter', 'border': 0, 'bold': False})
        center_head_2 = workbook.add_format({'font_size': 12, 'align': 'center', 'font_color': 'black',
                                             'valign': 'vcenter', 'border': 0, 'bold': True})
        center_head.set_font_name('Times New Roman')

        # id = records.filtered(lambda r: r.company_id.name == company_name)

        docs_sheet = workbook.add_worksheet('DOCS ' + str(month) + ' - ' + str(year))
        # docs_sheet = workbook.add_worksheet(f'DOCS {str(month)} - {str(year)} - {id}')
        row = 0
        col = 0
        docs_sheet.set_row(row - 1, 25)
        docs_sheet.set_row(row - 2, 25)
        docs_sheet.set_row(row - 3, 25)
        docs_sheet.set_row(row - 4, 25)
        docs_sheet.set_row(row - 5, 25)

        # docs_sheet.set_column(col - 1, col - 1, 20)
        docs_sheet.set_column(col, col, 25)
        docs_sheet.set_column(col + 1, col + 1, 20)
        docs_sheet.set_column(col + 2, col + 2, 25)
        docs_sheet.set_column(col + 3, col + 3, 18)
        docs_sheet.set_column(col + 4, col + 4, 18)
        docs_sheet.set_column(col + 5, col + 5, 20)
        docs_sheet.set_column(col + 6, col + 6, 18)
        docs_sheet.set_column(col + 7, col + 7, 18)
        docs_sheet.set_column(col + 8, col + 8, 18)
        docs_sheet.set_column(col + 9, col + 9, 20)
        docs_sheet.set_column(col + 10, col + 10, 42)
        docs_sheet.set_column(col + 11, col + 11, 18)
        docs_sheet.set_column(col + 12, col + 12, 18)
        docs_sheet.set_column(col + 13, col + 13, 25)
        docs_sheet.set_column(col + 14, col + 14, 15)
        docs_sheet.set_column(col + 15, col + 15, 14)
        docs_sheet.set_column(col + 16, col + 16, 40)
        docs_sheet.set_column(col + 17, col + 17, 40)
        docs_sheet.set_column(col + 18, col + 18, 14)
        # docs_sheet.set_column(col + 19, col + 19, 25)
        docs_sheet.set_column(col + 20, col + 20, 14)
        docs_sheet.set_column(col + 21, col + 21, 14)
        docs_sheet.set_column(col + 22, col + 22, 20)
        docs_sheet.set_column(col + 23, col + 23, 20)
        docs_sheet.set_column(col + 24, col + 24, 18)
        docs_sheet.set_column(col + 25, col + 25, 18)
        docs_sheet.set_column(col + 26, col + 26, 18)
        docs_sheet.set_column(col + 27, col + 27, 16)
        docs_sheet.set_column(col + 28, col + 28, 16)
        docs_sheet.set_column(col + 29, col + 29, 25)

        docs_sheet.write(row, col, 'Location', center_head)
        docs_sheet.write(row, col + 1, 'Warehouse Code', center_head)
        docs_sheet.write(row, col + 2, 'Warehouse Name', center_head)
        docs_sheet.write(row, col + 3, 'PO No.', center_head)
        docs_sheet.write(row, col + 4, 'PO Date', center_head)
        docs_sheet.write(row, col + 5, 'GRN No.', center_head)
        docs_sheet.write(row, col + 6, 'GRN Date.', center_head)
        docs_sheet.write(row, col + 7, 'Invoice Date', center_head)
        docs_sheet.write(row, col + 8, 'Invoice No.', center_head)
        docs_sheet.write(row, col + 9, 'Vendor Code', center_head)
        docs_sheet.write(row, col + 10, 'Vendor Name', center_head)
        docs_sheet.write(row, col + 11, 'GST No', center_head)
        docs_sheet.write(row, col + 12, 'State Code', center_head)
        docs_sheet.write(row, col + 13, 'Place of Supply', center_head)
        docs_sheet.write(row, col + 14, 'Item Code', center_head)
        docs_sheet.write(row, col + 15, 'Item Group', center_head)
        docs_sheet.write(row, col + 16, 'Product Category', center_head)
        docs_sheet.write(row, col + 17, 'Item Description', center_head)
        docs_sheet.write(row, col + 18, 'HSN', center_head)
        docs_sheet.write(row, col + 19, 'UOM', center_head)
        docs_sheet.write(row, col + 20, 'Item Quantity', center_head)
        docs_sheet.write(row, col + 21, 'Item Price', center_head)
        docs_sheet.write(row, col + 22, 'Item_Taxable_Value', center_head)
        docs_sheet.write(row, col + 23, 'CGST_RATE', center_head)
        docs_sheet.write(row, col + 24, 'CGST_AMOUNT', center_head)
        docs_sheet.write(row, col + 25, 'SGST_RATE', center_head)
        docs_sheet.write(row, col + 26, 'SGST_AMOUNT', center_head)
        docs_sheet.write(row, col + 27, 'IGST_RATE', center_head)
        docs_sheet.write(row, col + 28, 'IGST_AMOUNT', center_head)
        docs_sheet.write(row, col + 29, 'Item_Total_Including_GST', center_head)
        # docs_sheet.write(row, col + 30, 'Product Tags', center_head)


        self._cr.execute("""SELECT po.name AS sequence_number, sw.name AS warehouse, sw.code AS warehouse_code,
rc.name AS company_name, po.date_approve, sp.name AS grn_no, sp.date_done,pp.id AS pp,
rp.name AS vendor_name, rp.vat,rp.registration_number, pt.default_code, pc.complete_name, pt.l10n_in_hsn_code,
uu.name, pol.product_qty, pol.name AS product_description, pol.price_unit, pol.price_subtotal, pol.id AS pol_id,
s.code,am.invoice_date,am.name AS invoice_name
FROM purchase_order_line AS pol
LEFT JOIN purchase_order AS po ON po.id = pol.order_id
LEFT JOIN res_partner AS rp ON po.partner_id = rp.id
LEFT JOIN product_product AS pp ON pol.product_id = pp.id
LEFT JOIN product_template AS pt ON pp.product_tmpl_id = pt.id
LEFT JOIN res_country_state AS s ON rp.state_id = s.id
LEFT JOIN res_company AS rc ON po.company_id = rc.id
LEFT JOIN uom_uom AS uu ON pt.uom_id = uu.id
LEFT JOIN product_category AS pc ON pt.categ_id = pc.id
LEFT JOIN stock_warehouse AS sw ON rc.name = sw.name
LEFT JOIN purchase_order_stock_picking_rel AS por ON po.id = por.purchase_order_id
left join stock_picking as sp on por.stock_picking_id = sp.id
LEFT JOIN stock_picking_type  AS spt ON po.picking_type_id = spt.id
left join account_move_purchase_order_rel as ampor on ampor.purchase_order_id = po.id
LEFT JOIN account_move AS am ON ampor.account_move_id = am.id
            WHERE rc.id IN %s""", (tuple(company_ids),))
        fetched_data = self._cr.dictfetchall()
        print(fetched_data)

        price_total = 0
        total_sum = 0.00

        for i in fetched_data:
            dat = datetime.strftime(i['date_approve'], '%d-%m-%Y') if i.get('date_approve') else ''
            company_name = i['company_name']
            sequence_number = i['sequence_number']
            vendor_name = i['vendor_name']
            product_description = i['product_description']
            name = i['name']['en_US'] if i.get('name') and i['name'].get('en_US') else ''
            warehouse = i['warehouse']
            warehouse_code = i['warehouse_code']
            grn_no = i['grn_no']
            invoice_name = i.get('invoice_name')
            if i and i.get('date_done'):
                date_done = datetime.strftime(i['date_done'], '%d-%m-%Y')
            else:
                date_done = ''
            invoice_date = datetime.strftime(i['invoice_date'], '%Y-%d-%m') if i.get('invoice_date') else ''
            # if i['price_subtotal'] is not None:
            #     price_subtotal = float(i['price_subtotal'])
            # else:
            #     price_subtotal = 0.0
            print(i['pol_id'])
            var = self.env['purchase.order.line'].sudo().browse([i['pol_id']])
            res = var.taxes_id._origin.compute_all(var.price_subtotal, product=var.product_id,
                                                   partner=var.partner_id)
            # sum = i['total_amount']
            # total_igst_amount_per += i['amount_total]
            product_tags = self.env['product.product'].browse(i['pp']).product_tag_ids.mapped('name')
            print('Product Tags:', product_tags)


            print('/////////////////dddddddd')
            total_cess_amount = 0
            total_sgst_amount = 0
            total_cgst_amount = 0
            total_igst_amount = 0
            total_cess_amount_per = 0
            total_sgst_amount_per = 0
            total_cgst_amount_per = 0
            total_igst_amount_per = 0

            for tax in res['taxes']:
                print(tax)
                if tax['amount'] > 0:
                    amount_tax = self.env['account.tax'].search([('id', '=', tax['id'])])
                    print(amount_tax, '///')
                    tax_name_upper = tax['name'].upper()

                    # Calculate the respective amounts and add them to the totals
                    if 'CESS' in tax_name_upper:
                        total_cess_amount += tax['amount']
                        total_cess_amount_per += amount_tax.amount
                    elif 'SGST' in tax_name_upper:
                        total_sgst_amount += tax['amount']
                        total_sgst_amount_per += amount_tax.amount
                    elif 'CGST' in tax_name_upper:
                        total_cgst_amount += tax['amount']
                        total_cgst_amount_per += amount_tax.amount
                    elif 'IGST' in tax_name_upper:
                        total_igst_amount += tax['amount']

            consolidated_output = {
                'cess': total_cess_amount_per,
                'cess_amount': total_cess_amount,
                'sgst': total_sgst_amount_per,
                'sgst_amount': total_sgst_amount,
                'cgst': total_cgst_amount_per,
                'cgst_amount': total_cgst_amount,
                'igst': total_igst_amount_per,
                'igst_amount': total_igst_amount,
            }
            price_total = i['price_subtotal'] + consolidated_output['cgst_amount'] + consolidated_output[
                'sgst_amount'] + consolidated_output['igst_amount']
            total_sum += price_total

            print(consolidated_output, '//////////////////')
            # product_tags = ', '.join(i.product_id.product_tag_ids.mapped('name'))
            # igst_perc = i.get('igst_perc', '') if i else ''
            # cgst_perc = i.get('cgst_perc', '') if i else ''
            # sgst_perc = i.get('sgst_perc', '') if i else ''

            docs_sheet.write(row + 1, col, company_name, center_head_1)
            docs_sheet.write(row + 1, col + 1, warehouse_code, center_head_1)
            docs_sheet.write(row + 1, col + 2, warehouse, center_head_1)
            docs_sheet.write(row + 1, col + 3, sequence_number, center_head_1)
            docs_sheet.write(row + 1, col + 4, dat, center_head_1)
            docs_sheet.write(row + 1, col + 5, grn_no, center_head_1)
            docs_sheet.write(row + 1, col + 6, date_done, center_head_1)
            docs_sheet.write(row + 1, col + 7, invoice_date, center_head_1)
            docs_sheet.write(row + 1, col + 8, invoice_name, center_head_1)
            docs_sheet.write(row + 1, col + 9, i['registration_number'], center_head_1)
            docs_sheet.write(row + 1, col + 10, vendor_name, center_head_1)
            docs_sheet.write(row + 1, col + 11, i['vat'], center_head_1)
            docs_sheet.write(row + 1, col + 12, i['code'], center_head_1)
            docs_sheet.write(row + 1, col + 13, company_name, center_head_1)
            docs_sheet.write(row + 1, col + 14, i['default_code'], center_head_1)
            docs_sheet.write(row + 1, col + 15, i['complete_name'], center_head_1)
            tags_str = ', '.join(product_tags)
            docs_sheet.write(row + 1, col + 16, tags_str, center_head_1)
            docs_sheet.write(row + 1, col + 17, product_description)
            docs_sheet.write(row + 1, col + 18, i['l10n_in_hsn_code'], center_head_1)
            docs_sheet.write(row + 1, col + 19, name, center_head_1)
            docs_sheet.write(row + 1, col + 20, i['product_qty'], center_head_1)
            docs_sheet.write(row + 1, col + 21, i['price_unit'], center_head_1)
            docs_sheet.write(row + 1, col + 22, i['price_subtotal'], center_head_1)

            docs_sheet.write(row + 1, col + 23, consolidated_output['cgst'], center_head_1)
            docs_sheet.write(row + 1, col + 24, consolidated_output['cgst_amount'], center_head_1)
            # else:
            #     docs_sheet.write(row + 1, col + 23, '', center_head_1)
            #     docs_sheet.write(row + 1, col + 24, '', center_head_1)
            # if i['sgst_perc']:
            docs_sheet.write(row + 1, col + 25, consolidated_output['sgst'], center_head_1)
            docs_sheet.write(row + 1, col + 26, consolidated_output['sgst_amount'], center_head_1)
            # else:
            #     # SGST is not applicable, so leave the columns blank
            #     docs_sheet.write(row + 1, col + 25, '', center_head_1)
            #     docs_sheet.write(row + 1, col + 26, '', center_head_1)
            # if i['igst_perc']:
            docs_sheet.write(row + 1, col + 27, consolidated_output['igst'], center_head_1)
            docs_sheet.write(row + 1, col + 28, consolidated_output['igst_amount'], center_head_1)
            # else:
            #     # IGST is not applicable, so leave the columns blank
            #     docs_sheet.write(row + 1, col + 27, '', center_head_1)
            #     docs_sheet.write(row + 1, col + 28, '', center_head_1)
            # docs_sheet.write(row + 1, col + 29, i['amount_total'], center_head_1)
            docs_sheet.write(row + 1, col + 29, price_total, center_head_1)


            # docs_sheet.write(row + 1, col + 30, tags_str, center_head_1)

            # docs_sheet.write(row + 1, col + 30, total_amount_sum, center_head_1)
            row += 1
            # docs_sheet.write(row + 1, col + 29, price_total, center_head_1)
        docs_sheet.write(row + 1, col + 29, total_sum, center_head_2)
