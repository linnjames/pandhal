# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    registration_number = fields.Char(string='Registration Number')
    company_size = fields.Selection(
        [('l_5', '<5'), ('5_20', '5 to 20'), ('20_50', '20 to 50'),
         ('50_250', '50 to 250'), ('g_250', '>250')], string='Company Size',
        default='20_50')

    @api.model
    def create(self, vals_list):
        vals_list['registration_number'] = self.env['ir.sequence'].next_by_code(
            'res.partner') or _('New')
        return super(ResPartner, self).create(vals_list)
