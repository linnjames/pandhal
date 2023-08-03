from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime


class ActionSaleReportWizard(models.TransientModel):
    _name = 'sales.indent.report'

    from_date = fields.Date(string="From Date", required=True)
    to_date = fields.Date(string="TO Date", required=True)
    order_type = fields.Selection([('bakery', 'Bakery'),
                                   ('store', 'Store'),
                                   ('customer order', 'Customer Order')], required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)



    def action_print(self):
        if self.from_date > self.to_date:
            raise UserError(_("From Date is Greater Than To Date"))

        filter_cdtn = '''WHERE so.state = 'sale' AND so.validity_date BETWEEN %s AND %s '''
        params = (self.from_date.strftime("%Y-%m-%d 00:00:00"), self.to_date.strftime("%Y-%m-%d 23:59:59"))

        cdtn = filter_cdtn
        cdtn_params = params

        if self.order_type:
            cdtn += '''AND so.indent_type = %s '''
            cdtn_params += (self.order_type,)

        if self.company_id:
            filter_cdtn += '''AND so.company_id = %s '''
            params += (self.company_id.id,)
            cdtn += '''AND so.company_id = %s '''
            cdtn_params += (self.company_id.id,)

        query = """
            SELECT rp.id AS rp_id, rp.name AS rp_name, rp.phone AS phone,
            so.id AS si_id, so.name AS si_name, so.purchase_id,
            so.client_order_ref AS purchase_name,
            pt.name AS pt_name, pt.list_price AS pt_list_price,
            pt.standard_price AS pt_standard_price,
            sol.message AS pt_message,
            sol.product_id AS product,
            uom.id AS uom_name,
            sol.product_uom_qty AS total_qty
            FROM sale_order_line sol
            LEFT JOIN sale_order so ON sol.order_id = so.id
            LEFT JOIN purchase_order po ON so.purchase_id = po.id
            LEFT JOIN uom_uom uom ON sol.product_uom = uom.id
            LEFT JOIN res_partner rp ON so.partner_id = rp.id
            LEFT JOIN product_product pp ON sol.product_id = pp.id
            LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
            {}
        """.format(filter_cdtn)

        self._cr.execute(query, params)
        move_ids = self.env.cr.dictfetchall()

        if not move_ids:
            raise UserError(_("Nothing to print."))

        for move_id in move_ids:
            product_name = move_id['pt_name']
            if isinstance(product_name, dict):
                # If the product name is a dictionary, retrieve the value for the current language
                product_name = product_name.get(self.env.lang, '')
            move_id['pt_name'] = product_name.strip() if product_name else ''

            # Ensure 'purchase_id' is present in the dictionary and has a 'name' attribute
            # if 'purchase_id' in move_id and move_id['purchase_id']:
            #     purchase_order = self.env['purchase.order'].browse(move_id['purchase_id'])
            #     move_id['purchase_name'] = purchase_order.name
            # else:
            #     # If 'purchase_id' is not present or empty, set 'purchase_name' to an empty string
            #     move_id['purchase_name'] = ''

        lens = []
        for i in move_ids:
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

        data = {
            'model': self._name,
            'ids': self.ids,
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

