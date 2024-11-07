from odoo import api, fields, models, _


class MrpReportWizard(models.TransientModel):
    _name = "mrp.report.wizard"
    _description = "MRP Report"

    prod_ids = fields.Many2many('product.product', string="Products")
    categ_ids = fields.Many2many('product.category', string='Category')
    date_from = fields.Datetime(string='Date From')
    date_to = fields.Datetime(string='Date To')

    def action_print_report(self):
        x = self.date_from.strftime('%Y-%m-%d 00:00:00')
        y = self.date_to.strftime('%Y-%m-%d 23:59:59')
        print(self.prod_ids)
        temp = self.prod_ids.product_tmpl_id
        # print(temp, 'temp')

        # Date comparison
        if self.date_from > self.date_to:
            raise Warning(_("From Date is greater than To Date!"))

        condition = '''WHERE mdl.mrp_updated_date BETWEEN '%s' AND '%s'
                         ''' % (x, y)
        # print(condition, '888888888888888888888888888888')

        # if self.categ_ids:
        #     if len(self.categ_ids) == 1:
        #         condition = """WHERE pt.categ_id = '%s'""" % (self.categ_ids[0])
        #     else:
        #         condition = """WHERE pt.categ_id IN %s
        #                                          """ % str(tuple(self.categ_ids))

        if self.prod_ids:
            if len(temp) == 1:
                condition = """WHERE mdl.product_id = '%s'""" % (temp.ids[0])
            else:
                condition = """WHERE mdl.product_id IN %s
                                                 """ % str(tuple(temp.ids))

        # print(condition, '10000000000000000000000000000000000000000000000000000')

        query = """
                SELECT mdl.id mdl, mdl.mrp_updated_date updated_date, mdl.mrp_updated_value updated_value, pt.id pt,(pt.name->>'en_US')::text product, pt.l10n_in_hsn_code vat,
                    pt.categ_id category, pt.default_code code, u.login user_name
                FROM mrp_details_line AS mdl
                LEFT JOIN product_template AS pt ON mdl.product_id = pt.id
                LEFT JOIN res_users AS u ON mdl.user_name = u.id
                %s
            """ % condition

        self._cr.execute(query)
        mrp_details_lines = self._cr.dictfetchall()
        # print(mrp_details_lines)
        # print(id)


        values = []
        dup = []
        unique_product_ids = set()

        for i in mrp_details_lines:
            product_id = i['pt']
            product_name = i['product']

            if product_id not in [item['product_id'] for item in values]:
                unique_product_ids.add(product_id)
                values.append({
                    'product_id': product_id,
                    'product_name': product_name,
                    'mdl': i['mdl'],
                    'hsn': i['vat'],
                    'reference':i['code']
                })
            else:
                dup.append({
                    'product_id': product_id,
                    'mdl': i['mdl'],
                    'product_name': product_name,
                    'hsn': i['vat'],
                })

        print('values =', values)
        print('dup =', dup)

        data = {
                    'ids': self.ids,
                    'model': self._name,
                    'dup': values,
                    'vals': mrp_details_lines,
                    'x': x,
                    'y': y,
        }
        print('data=',data)

        # unique_products = set()
        # values = []
        # for line in mrp_details_lines:
        #     prod_id = line.get('id')
        #     if prod_id not in unique_products:
        #         values.append(line)
        #         unique_products.add(prod_id)
        #         print(line['name'])
        #         print(values)

        return self.env.ref('sales_price_calculation_mrp.record_mrp_updation_print').report_action(self, data=data)


        # action = self.env.ref('sales_price_calculation_mrp.record_mrp_updation_print').report_action(self, data={
        #     'values': values, 'date_from': x, 'date_to': y})
        # print('11111111111111111111',data)

        # return action



