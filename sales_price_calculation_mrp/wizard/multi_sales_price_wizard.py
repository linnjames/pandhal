# -*- coding: utf-8 -*-

import time

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class MultiSalesPriceWizard(models.TransientModel):
    _name = "multi.sales.price.wizard"
    _description = "Multiple Sales Price"

    def _get_default_products(self):
        product_ids = self.env['product.template'].browse(self._context.get('active_ids', [])).ids
        return product_ids

    product_tmpl_ids = fields.Many2many('product.template', string='Products', default=_get_default_products)

    def multi_price(self):
        for product_id in self.product_tmpl_ids:
            product_id.action_mrp()

        return {
            'effect': {
                'fadeout': 'fast',
                'message': 'Successful',
                'img_url': '/web/static/src/img/smile.svg',
                'type': 'rainbow_man',
            }
        }
