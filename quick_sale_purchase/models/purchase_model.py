# -*- coding: utf-8 -*-
from odoo import models, fields, _
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    sh_sale_order_id = fields.Many2one(
        "sale.order", string="Sale Order", readonly=True)

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()

        sale_orders = self.env['sale.order'].sudo().search([('purchase_id', '=', False)])
        for record in sale_orders:
            record.purchase_id = self.id

        return res
