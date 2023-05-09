from datetime import datetime, date

from odoo import models, fields, _, api


class InvoicePosReportWizard(models.TransientModel):
    _name = "invoice.pos.report.wizard"

    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    # product_category_type_ids = fields.Many2many('product.category.type', string='Category Type')
    company_ids = fields.Many2many('res.company', string='Company')
    product_ids = fields.Many2many('product.product', string='Product')
    product_category_ids = fields.Many2many('product.category', string='Category')
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user.id)
    typ = fields.Selection([('franchise', 'Franchise'), ('own', 'Own')], string="Type")

    @api.onchange('date_from', 'date_to', 'company_ids', 'user_id')
    def _onchange_company_ids(self):
        comp_list = []
        if self.user_id:
            if self.user_id.has_group('base.group_erp_manager') or self.user_id.has_group('base.group_system'):
                for i in self.user_id.company_ids:
                    comp_list.append(i.id)
            else:
                comp_list = self.env.context['allowed_company_ids']
        return {'domain': {'company_ids': [('id', 'in', tuple(comp_list))]}}

    def action_print_report(self):
        user = self.env.user.id
        self.env.cr.execute(("""DELETE FROM invoice_pos_report WHERE current_user_id = %s""") % user)

        condition = ''
        conditions = ''

        if self.date_from and self.date_to:
            x = self.date_from.strftime('%Y-%m-%d 00:00:00')
            y = self.date_to.strftime('%Y-%m-%d 23:59:59')
            condition += """ and am.invoice_date between '%s' and '%s'""" % (x, y)
            conditions += """ and po.date_order at time zone 'utc' at time zone 'ist' between '%s' and '%s'""" % (x, y)

        # if self.product_category_type_ids:
        #     if len(self.product_category_type_ids) == 1:
        #         condition += """ and pt.product_category_type_id = %s""" % self.product_category_type_ids.id
        #         conditions += """ and pt.product_category_type_id = %s""" % self.product_category_type_ids.id
        #     else:
        #         condition += """ and pt.product_category_type_id in {}""".format(
        #             tuple(self.product_category_type_ids.ids))
        #         conditions += """ and pt.product_category_type_id in {}""".format(
        #             tuple(self.product_category_type_ids.ids))

        if self.product_ids:
            if len(self.product_ids) == 1:
                condition += """ and aml.product_id = %s""" % self.product_ids.id
                conditions += """ and pol.product_id = %s""" % self.product_ids.id
            else:
                condition += """ and aml.product_id in {}""".format(tuple(self.product_ids.ids))
                conditions += """ and pol.product_id in {}""".format(tuple(self.product_ids.ids))

        if self.product_category_ids:
            if len(self.product_category_ids) == 1:
                condition += """ and pt.categ_id = %s""" % self.product_category_ids.id
                conditions += """ and pt.categ_id = %s""" % self.product_category_ids.id
            else:
                condition += """ and pt.categ_id in {}""".format(tuple(self.product_category_ids.ids))
                conditions += """ and pt.categ_id in {}""".format(tuple(self.product_category_ids.ids))

        if self.typ:
            condition += """ and rp.typ = '%s'""" % self.typ

        if self.company_ids:
            if len(self.company_ids) == 1:
                condition += """ and aml.company_id = %s""" % self.company_ids.id
                conditions += """ and pol.company_id = %s""" % self.company_ids.id
            else:
                condition += """ and aml.company_id in {}""".format(tuple(self.company_ids.ids))
                conditions += """ and pol.company_id in {}""".format(tuple(self.company_ids.ids))
        else:
            comp = self.user_id.company_ids
            if len(comp) == 1:
                condition += """ and aml.company_id = %s""" % comp.id
                conditions += """ and pol.company_id = %s""" % comp.id
            else:
                condition += """ and aml.company_id in {}""".format(tuple(comp.ids))
                conditions += """ and pol.company_id in {}""".format(tuple(comp.ids))



        self.env.cr.execute(("""INSERT INTO invoice_pos_report (product_id, company_id, product_category_id,
                    invoice_date, partner_id, quantity, untaxed_amount, taxed_amount, user_id, current_user_id)
        	                            SELECT aml.product_id as product, aml.company_id as company, pt.categ_id as category, am.invoice_date as invoice_date, am.partner_id as partner,
                                        aml.quantity as qty, aml.price_subtotal, aml.price_total, am.invoice_user_id as user_id, %s as current_user_id
                                        FROM account_move_line as aml
                                        left join account_move as am on aml.move_id = am.id
                                        left join product_product as pp on aml.product_id = pp.id
                                        left join product_template as pt on pp.product_tmpl_id = pt.id
                                        left join res_partner as rp on am.partner_id = rp.id
                                        where am.state = 'posted' and am.move_type = 'out_invoice' and aml.product_id is not null
                                %s
		 union all
								SELECT aml.product_id as product, aml.company_id as company, pt.categ_id as category, am.invoice_date as invoice_date, am.partner_id as partner,
                                        aml.quantity as qty, aml.price_subtotal as price_subtotal, aml.price_total as price_total, am.invoice_user_id as user_id, %s as current_user_id
                                        FROM account_move_line as aml
                                        left join account_move as am on aml.move_id = am.id
                                        left join product_product as pp on aml.product_id = pp.id
                                        left join product_template as pt on pp.product_tmpl_id = pt.id
                                        left join res_partner as rp on am.partner_id = rp.id
                                        where am.state = 'posted' and am.move_type = 'out_refund' and aml.product_id is not null
                                %s
		union all
								SELECT pol.product_id as product,pol.company_id as company,pt.categ_id as category,pos.date_order as invoice_date,pos.partner_id as partner,
                                        pol.qty as qty, pol.price_subtotal  as price_subtotal, pol.price_subtotal_incl as price_total, am.invoice_user_id as user_id, %s as current_user_id
                                        FROM pos_order as pos
                                        left join pos_order_line as pol on pol.order_id = pos.id
                                         left join product_product as pp on pol.product_id = pp.id
                                         left join product_template as pt on pp.product_tmpl_id = pt.id
                                         left join res_partner as rp on pos.partner_id = rp.id
                                         where pos.state in ('paid', 'done', 'invoiced');
                                %s""")
                            % (user, condition, user, condition, user, conditions))


        pivot_view_ref = self.env.ref('invoice_pos_report.view_invoice_pos_report_pivot', False)
        tree_view_ref = self.env.ref('invoice_pos_report.invoice_pos_report_tree', False)
        graph_view_ref = self.env.ref('invoice_pos_report.view_invoice_pos_report_graph', False)
        return {
            'name': "Invoice Pos Report",
            'view_mode': 'tree, pivot, graph',
            'view_id': False,
            'res_model': 'invoice.pos.report',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'views': [(pivot_view_ref and pivot_view_ref.id or False, 'pivot'),
                      (tree_view_ref and tree_view_ref.id or False, 'tree'),
                      (graph_view_ref and graph_view_ref.id or False, 'graph')],
        }
