from odoo import models, fields, api, _
from odoo.exceptions import Warning
from datetime import datetime, date


class InvoicePosReport(models.Model):
    _name = "invoice.pos.report"

    product_id = fields.Many2one('product.product', string='Product')
    company_id = fields.Many2one('res.company', string='Company')
    product_category_id = fields.Many2one('product.category', string='Category')
    # product_category_type_id = fields.Many2one('product.category.type', string='Category Type')
    invoice_date = fields.Date(string='Invoice Date')
    partner_id = fields.Many2one('res.partner', string='Partner')
    # typ = fields.Selection([('franchise', 'Franchise'), ('own', 'Own')], string="Type")
    # region_id = fields.Many2one('region.master', string='Region')
    quantity = fields.Float(string='Quantity')
    untaxed_amount = fields.Float(string='Untaxed Amount')
    taxed_amount = fields.Float(string='Taxed Amount')
    # shelf_life_int = fields.Char(string='Shelf Life')
    user_id = fields.Many2one('res.users', string='User')
    current_user_id = fields.Many2one('res.users', string='Current User')

    # def init(self):
    #     self._cr.execute("""
    #        CREATE OR REPLACE VIEW invoice_pos_report AS (
    #           SELECT aml.product_id as product, aml.company_id as company, pt.categ_id as category, pt.product_category_type_id  as category_type, am.invoice_date as invoice_date, am.partner_id as partner,
    #                             rp.typ as typ,rp.region_id as region, aml.quantity as qty, aml.price_subtotal, aml.price_total, am.state
    #                             FROM account_move_line as aml
    #                             left join account_move as am on aml.move_id = am.id
    #                             left join product_product as pp on aml.product_id = pp.id
    #                             left join product_template as pt on pp.product_tmpl_id = pt.id
    #                             left join res_partner as rp on am.partner_id = rp.id
    #                             where am.state = 'posted' and am.move_type = 'out_invoice' and aml.exclude_from_invoice_tab = False)""")
