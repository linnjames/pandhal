from odoo import models, fields


class ProductCategory(models.Model):
    _inherit = 'product.category'

    product_fssai = fields.Boolean(string="FSSAI")
