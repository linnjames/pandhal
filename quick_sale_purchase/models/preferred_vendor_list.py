# -*- coding: utf-8 -*-
from odoo import fields, models, api


class PreferredVendorList(models.Model):
    _name = "preferred.vendor"
    _description = "Preferred Vendor List Company wise"
    _rec_name = "product_id"

    product_id = fields.Many2one('product.product', string="Product")
    pref_ven_line = fields.One2many('preferred.vendor.lines', 'ref_id',
                                    string="Preference")
    _sql_constraints = [('unique_product', 'unique (product_id)', 'Product already added!')]

    vendor_name = fields.Many2one('res.partner', string="Vendor")
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm')], default='draft')

    @api.onchange('vendor_name')
    def _onchange_vendor_name(self):
        self.pref_ven_line = False
        self.state = 'draft'

    def add_details(self):
        print("hjk")
        self.pref_ven_line = False
        comp_obj = self.env['res.company'].search([])
        for i in comp_obj:
            print("Vendor:", i.name)
            self.write({'pref_ven_line': [(0, 0, {'company_id': i.id,'partner_id': self.vendor_name.id})]})
        self.state = 'confirm'


class PreferredVendorLines(models.Model):
    _name = "preferred.vendor.lines"
    _description = "Preferred Vendor Lines"

    # Educational Qualifications
    ref_id = fields.Many2one('preferred.vendor', string="Ref ID")
    company_id = fields.Many2one('res.company', string="Company")
    partner_id = fields.Many2one('res.partner', string="Vendor")
