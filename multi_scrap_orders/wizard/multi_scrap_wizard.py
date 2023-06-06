import datetime
import base64
import io

from odoo import models, fields, api, _
from datetime import datetime
from odoo.tools import date_utils
from odoo.tools.safe_eval import json

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class MultiScrapWizard(models.TransientModel):
    _name = 'multi.scrap.wizard'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    date = fields.Date(string='Date', default=fields.Date.context_today, readonly=True)

    def action_scrap_report(self):
        print('//////////////////')
        # a = self.env['res.config.settings'].sudo().search([], limit=1, order='id desc')
        # b = datetime.today().strftime('%B %d, %Y')
        # for i in a:
        #     for j in i.mail_ids:
        #         mail_content = "Hello " + str(
        #             "<br/><br/>" + "Multi scrap report have been generated" + " "+str(b) + "<br/><br/<br/><br/>Thank you.")
        #         # mail = self.env['mail.mail'].sudo().create({
        #         #     'subject': 'Multi Scrap Report',
        #         #     'email_from': self.create_uid.email,
        #         #     'email_to': j.partner_id.email,
        #         #     'body_html': mail_content,
        #         #     # 'attachment_ids': self.env.ref('multi_scrap_orders.multi_scrap_report_xlsx'),
        #         #     # template.attachment_ids = [(6, 0, [data_id.id])]
        #         #
        #         # })
        #         data, data_format = self.env.ref('multi_scrap_orders.multi_scrap_report_xlsx')._render(self.id)
        #         att_id = self.env['ir.attachment'].create({
        #             'name': 'Multi Scrap.xlsx',
        #             'type': 'binary',
        #             'datas': base64.encodestring(data),
        #             'res_model': 'multi.scrap.wizard',
        #             'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        #
        #         })
        #         mail = {
        #             'subject': "Multi Scrap",
        #             'body_html': mail_content,
        #             'email_from': self.create_uid.email,
        #             'email_to': j.partner_id.email,
        #             'attachment_ids': [(6, 0, att_id.ids)],
        #         }
        #         self.env['mail.mail'].sudo().create(mail).send()
        date_from = self.date.strftime('%Y-%m-%d 00:00:00')
        date_to = self.date.strftime('%Y-%m-%d 23:59:59')
        data = {
            'date_from': date_from,
            'date_to': date_to,
        }
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'multi.scrap.wizard',
                     'options': json.dumps(data, default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'TDS Report',
                     },
            'report_type': 'xlsx',
        }

    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        format1 = workbook.add_format(
            {'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'bold': True, 'border': 5, })
        sheet = workbook.add_worksheet('MultiScrapXlsx')
        sheet.set_column('A:A', 40)
        sheet.set_column('B:B', 18)
        sheet.set_column('C:C', 18)
        sheet.set_column('D:D', 18)
        sheet.set_column('E:E', 27)
        row = 0
        col = 0
        sheet.write(0, 0, 'Product Name', format1)
        format2 = workbook.add_format(
            {'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'bold': True, 'border': 5, })
        sheet.write(0, 1, 'Today Inward Qty', format2)
        format3 = workbook.add_format(
            {'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'bold': True, 'border': 5, })
        sheet.write(0, 2, 'Scrap Qty', format3)
        format4 = workbook.add_format(
            {'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'bold': True, 'border': 5, })
        sheet.write(0, 3, 'Closing Stock', format4)
        format4 = workbook.add_format(
            {'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'bold': True, 'border': 5, })
        sheet.write(0, 4, 'Reason', format4)

        self._cr.execute(('''SELECT pt.name,sp.scheduled_date, pt.id , sum(sml.qty_done)
                               FROM stock_picking sp
                               left join stock_move sm on sp.id = sm.picking_id
                               left join stock_move_line sml on sp.id = sml.picking_id
                               left join product_product pp on sm.product_id = pp.id
                               left join product_template pt on pp.product_tmpl_id = pt.id
                               left join multi_scrap_line msl on pt.id = msl.product_id
                               left join stock_quant sq on pt.id = sq.product_id
                               where sp.scheduled_date between '%s' and '%s'
                               group by(pt.id,sp.scheduled_date)
                               ''') % (
            data['date_from'], data['date_to']))
        move = self.env.cr.dictfetchall()
        for i in move:
            i['reason'] = ''
            i['quantity'] = 0
            products = self.env['product.template'].search([('id', '=', i['id'])])
            i['qty_avilable'] = products.qty_available
        self._cr.execute(('''SELECT  pt.name, pt.id,ir.res as reason,msl.quantity, ms.expected_date
                                        FROM multi_scrap_line msl
                                        left join product_product pp on msl.product_id = pp.id
                                        left join product_template pt on pp.product_tmpl_id = pt.id
                                        left join inventory_reason ir on msl.reason = ir.id
        								left join multi_scrap ms on msl.multi_scarp_id = ms.id
         							    where ms.expected_date between '%s' and '%s' ''') % (
            data['date_from'], data['date_to']))
        moves = self.env.cr.dictfetchall()
        for j in moves:
            j['sum'] = 0
            j['qty_avilable'] = 0
        mo = move + moves
        for inv in mo:
            row += 1
            sheet.write(row + 1, col, inv['name'])
            sheet.write(row + 1, col + 1, inv['sum'])
            sheet.write(row + 1, col + 2, inv['quantity'])
            sheet.write(row + 1, col + 3, inv['qty_avilable'])
            sheet.write(row + 1, col + 4, inv['reason'])

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
