from odoo import models, fields


class CaseSystem(models.Model):
    _name = 'case.system'
    _description = 'Case System'

    case = fields.Char(string='Case')
    case1_id = fields.Many2one('hr.department')


class EmployeeDepartment(models.Model):
    _inherit = 'hr.department'

    criteria_line_ids = fields.One2many('case.system', 'case1_id', srtring='Cases')
