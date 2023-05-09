import io

from odoo import models, fields
from odoo.http import request
from odoo.tools import date_utils
from odoo.tools.safe_eval import json

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class TdsReport(models.TransientModel):
    _name = 'tds.report'
    _description = 'TDS Report'

    from_date = fields.Date(string='From Date')
    to_date = fields.Date(string='To Date')
    type_selection = fields.Selection([('sale', 'Sales'), ('purchase', 'Purchase')], string='Type Selection',
                                      default='purchase')
    date_selection = fields.Selection([('account_date', 'Accounting Date'), ('bill_date', 'Bill Date')],
                                      string='Date Selection', default='bill_date')

    def print_tds_report(self):
        date_from = self.from_date.strftime('%Y-%m-%d 00:00:00')
        date_to = self.to_date.strftime('%Y-%m-%d 23:59:59')
        from_date = self.from_date.strftime('%d-%m-%Y')
        to_date = self.to_date.strftime('%d-%m-%Y')
        data = {
            'from_date': date_from,
            'to_date': date_to,
            'date_from': from_date,
            'date_to': to_date,
            'type_selection': self.type_selection,
            'date_selection': self.date_selection,
        }
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'tds.report',
                     'options': json.dumps(data, default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'TDS Report',
                     },
            'report_type': 'xlsx',
        }
        # return self.env.ref('account_taxes.tds_report_excel').report_action(self, data=data)

    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        row = 4
        col = 0
        sheet = workbook.add_worksheet('TDS Ageing')
        bold1 = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#919191', 'border': 1})
        bold2 = workbook.add_format({'bold': True, 'align': 'center'})
        bold3 = workbook.add_format({'bold': True, 'align': 'left'})
        bold4 = workbook.add_format({'bold': True, 'bg_color': '#bfbbbd', 'align': 'left'})
        size = workbook.add_format({'font_size': 20, 'bg_color': '#c7c5c6', 'align': 'center', 'border': 1})
        rowss = sheet.set_default_row(20)
        align = workbook.add_format({'align': 'left'})

        sheet.write(row - 2, col + 0, ' From Date :', bold2)
        sheet.write(row - 2, col + 1, data['date_from'])
        sheet.write(row - 1, col + 0, 'To Date :', bold2)
        sheet.write(row - 1, col + 1, data['date_to'])

        sheet.merge_range('C1:E1', 'TDS Report', size)
        sheet.write(row, col + 0, 'Date', bold1)
        sheet.write(row, col + 1, 'Particulars', bold1)
        sheet.write(row, col + 2, 'Pan No.', bold1)
        sheet.write(row, col + 3, 'Amount', bold1)
        sheet.write(row, col + 4, 'TDS Amount', bold1)
        sheet.write(row, col + 5, 'TDS %', bold1)
        sheet.set_row(1, rowss)

        sheet.set_column('A:A', 15)
        sheet.set_column('B:B', 30)
        sheet.set_column('C:C', 35)
        sheet.set_column('D:D', 20)
        sheet.set_column('E:E', 20)
        sheet.set_column('F:F', 15)
        sheet.set_column('G:G', 15)

        sheet.set_row(0, 35)

        condition = ""
        if data['date_selection'] == 'bill_date':
            condition += "and am.invoice_date between '%s' and '%s'" % (data['from_date'], data['to_date'])
        if data['date_selection'] == 'account_date':
            condition += "and am.date between '%s' and '%s'" % (data['from_date'], data['to_date'])
        if data['type_selection'] == 'sale':
            condition += "and am.move_type = 'in_invoice'"
        if data['type_selection'] == 'purchase':
            condition += "and am.move_type = 'out_invoice'"

        self.env.cr.execute(("""
                                        SELECT am.invoice_date as invoice_dates, am.date as account_dates, am.name, rp.name as partner_id, rp.pan_no , am.amount_untaxed,
                                         tm.name as tds_section, am.tds_amount, am.tds_percentage, tm.id as tds_id
                                            FROM account_move am
                                            left join res_partner rp on am.partner_id = rp.id
                                            left join tds_management tm on am.tds_section = tm.id
                                            where tm.name is not Null %s
                                        """) % (condition))
        move_ids = self.env.cr.dictfetchall()
        tds = self.env['tds.management'].search([])
        tds_sec = {}
        for i in tds:
            list1 = []
            for inv in move_ids:
                if i.id == inv['tds_id']:
                    x = inv['tds_section']
                    list1.append(inv)
                    tds_sec[x] = list1
        if data['date_selection'] == 'account_date':
            for inv in tds_sec.keys():
                row += 1
                sheet.write(row, 0, row, 5, 'TDS Section: ' + inv, bold4)
                tds_sum = 0
                amount = 0
                for i in tds_sec[inv]:
                    sheet.write(row + 1, col, i['account_dates'].strftime('%d-%m-%Y'), align)
                    sheet.write(row + 1, col + 1, i['partner_id'], align)
                    sheet.write(row + 1, col + 2, i['pan_no'], align)
                    sheet.write(row + 1, col + 3, i['amount_untaxed'], align)
                    sheet.write(row + 1, col + 4, i['tds_amount'], align)
                    sheet.write(row + 1, col + 5, i['tds_percentage'], align)
                    tds_sum += i['tds_amount']
                    amount += i['amount_untaxed']
                    row += 1
                row += 1
                sheet.write(row, col + 4, tds_sum, bold3)
                sheet.write(row, col + 3, amount, bold3)

        if data['date_selection'] == 'bill_date':
            for inv in tds_sec.keys():
                row += 1
                sheet.merge_range(row, 0, row, 5, 'TDS Section: ' + inv, bold4)
                tds_sum = 0
                amount = 0
                for i in tds_sec[inv]:
                    sheet.write(row + 1, col, i['invoice_dates'].strftime('%d-%m-%Y'), align)
                    sheet.write(row + 1, col + 1, i['partner_id'], align)
                    sheet.write(row + 1, col + 2, i['pan_no'], align)
                    sheet.write(row + 1, col + 3, i['amount_untaxed'], align)
                    sheet.write(row + 1, col + 4, i['tds_amount'], align)
                    sheet.write(row + 1, col + 5, i['tds_percentage'], align)
                    tds_sum += i['tds_amount']
                    amount += i['amount_untaxed']
                    row += 1
                row += 1
                sheet.write(row, col + 4, tds_sum, bold3)
                sheet.write(row, col + 3, amount, bold3)

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
