from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    vendor = fields.Many2one('res.partner',string='Vendor')
