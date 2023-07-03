from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    company_ids = fields.Many2many('res.company', string='Company')
