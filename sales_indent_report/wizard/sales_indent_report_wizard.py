from odoo import models, fields, api, _
import json

from odoo.exceptions import ValidationError
from datetime import datetime


class ActionSaleReportWizard(models.TransientModel):
    _name = 'sales.indent.report'

    from_date = fields.Date(string="From Date", required=True)
    to_date = fields.Date(string="TO Date", required=True)
    order_type = fields.Selection([('bakery', 'Bakery'),
                                   ('store', 'Store'),
                                   ('customer order', 'Customer Order')], required=True)

    def action_print(self):
        company_id = self.env.company.id
        if self.from_date > self.to_date:
            raise Warning(_("From Date is Greater Than To Date"))
        filter_cdtn = ''' and so.expected_date between '%s' AND '%s'
                                                  ''' % (self.from_date.strftime("%Y-%m-%d 00:00:00"), self.to_date.strftime("%Y-%m-%d 23:59:59"))
        print(filter_cdtn, "wwwwwwwwwwwwwwww")

        if self.order_type:
            filter_cdtn += """ and so.indent_type = '%s'""" % self.order_type
        print(filter_cdtn, 'qqqqqqqqqqqqqqqqqqqqqqqqq')

        # query = ("""select rp.id rp_id, rp.name rp_name,rp.phone phone,
        #                         so.id so_id, so.reference so_name,so.no_id so_purchase_ref,
        #                         pt.name pt_name, sil.qty pt_qty,
        #                         sil.message pt_message, so.company_id so_com
        #                         from sales_indent_lines sil
        #                         left join sales_indent so on sil.pur_id = so.id
        #                         left join res_partner rp on so.vendor_id = rp.id
        #                         left join product_product pp on sil.product_id = pp.id
        #                         left join product_template pt on pp.product_tmpl_id = pt.id
        #                         where so.company_id = %s and so.state = 'confirmed' %s
        #                         order by so.reference asc
        #                     """ % (company_id, filter_cdtn))
        # print(query)

        query = ("""select rp.id rp_id, rp.name rp_name,rp.phone phone,
                                        so.id so_id, so.reference so_name,so.no_id so_purchase_ref,
                                        pt.name pt_name, sil.qty pt_qty,pt.list_price pt_list_price,
                                        pt.standard_price pt_standard_price,
                                        sil.message pt_message, so.company_id so_com
                                        from sales_indent_lines sil
                                        left join sales_indent so on sil.pur_id = so.id
                                        left join res_partner rp on so.vendor_id = rp.id
                                        left join product_product pp on sil.product_id = pp.id
                                        left join product_template pt on pp.product_tmpl_id = pt.id
                                        where so.company_id = %s and so.state = 'confirmed' %s
                                        order by so.reference asc
                                    """ % (company_id, filter_cdtn))
        print(query)

        self._cr.execute(query)
        move_ids = self.env.cr.dictfetchall()
        # move_ids = json.loads(move_ids)
        print('eeeeeeeeeeeee', move_ids)

        for move_id in move_ids:
            product_name = move_id['pt_name']
            if isinstance(product_name, dict):
                # If the product name is a dictionary, retrieve the value for the current language
                product_name = product_name.get(self.env.lang, '')
            move_id['pt_name'] = product_name.strip() if product_name else ''

        lens = []
        for i in move_ids:
            x = self.env['sales.indent'].sudo().search([('id', '=', i['so_id'])])
            if x.state == 'confirmed':
                lens.append({
                    'customer_id': i['rp_id'],
                    'customer': i['rp_name'],
                    'phone': i['phone'],
                })

        no_dup = []
        for j in lens:
            if j not in no_dup:
                no_dup.append(j)
        sort_code = sorted(no_dup, key=lambda s: s['customer'])

        # move_ids_json = json.dumps(move_ids)

        data = {
            'model': self._name,
            'ids': self.ids,
            # 'vals': move_ids_json,
            'vals': move_ids,
            'cust_code': sort_code,
            'from_date': self.from_date.strftime("%d-%m-%Y"),
            'to_date': self.to_date.strftime("%d-%m-%Y"),
            'company': self.env.company.name,
        }
        print("lllllllllllllllllll", data)
        return self.env.ref('sales_indent_report.report_sales_indent_report_pdf').report_action(self, data=data)


class CustomProductTemplate(models.Model):
    _inherit = 'product.template'

    standard_price = fields.Float(string='Standard Price', store=True)
