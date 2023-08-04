# -*- coding: utf-8 -*-
from odoo import models, fields, _
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    sh_sale_order_id = fields.Many2one(
        "sale.order", string="Sale Order", readonly=True)
