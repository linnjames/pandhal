from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    company_ids = fields.Many2many('res.company', string='Company')





class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Add a Many2one field to link with the purchase order
    purchase_id = fields.Many2one('purchase.order', string='Purchase')

    # Add a Char field to store the purchase order name
    purchase_name = fields.Char(related='purchase_id.name', readonly=True)