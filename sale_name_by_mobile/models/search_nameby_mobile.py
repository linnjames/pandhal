from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.onchange('phone')
    def _onchange_name_phone(self):
        if self.phone:
            self.name = '%s - %s' % (self.name.split(' - ')[0], self.phone)

    _sql_constraints = [
        ('unique_phone', 'UNIQUE(phone)', 'Phone number must be unique!'),
    ]

    @api.constrains('phone')
    def _check_unique_phone(self):
        for partner in self:
            if partner.phone:
                duplicate_partners = self.env['res.partner'].search([
                    ('phone', '=', partner.phone),
                    ('id', '!=', partner.id)
                ])
                if duplicate_partners:
                    raise ValidationError('Phone number must be unique!')
