from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    terms_and_condition = fields.Text(string="Terms and Conditions")

    # def action_view_sale_order(self):
    #     pass


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.onchange('partner_id')
    def _onchange_purchase_order_partner_id(self):
        self.notes = False
        self.notes = self.partner_id.terms_and_condition
