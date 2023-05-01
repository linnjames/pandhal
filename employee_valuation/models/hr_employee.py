from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    criteria_ids = fields.Many2many('performance.criteria', string='Performance Criteria')
