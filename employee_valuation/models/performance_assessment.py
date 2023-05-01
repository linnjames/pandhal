from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class PerformanceAssessment(models.Model):
    _name = 'performance.assessment'
    _description = 'Performance Assessment'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string='Employee')
    department_id = fields.Many2one('hr.department', string='Department')
    criteria_id = fields.Many2one('performance.criteria', string='Performance Criteria')
    user_id = fields.Many2one('res.users', string='Valuation User')
    max_mark = fields.Float(string='Maximum Mark')
    min_mark = fields.Float(string='Minimum Mark')

    valuation_id = fields.Many2one('employee.valuation', string='Employee Valuation')

    state = fields.Selection(
        [('draft', 'Draft'), ('approve', 'Approve')],
        default='draft', string='Status', readonly=True)

    assess_line_ids = fields.One2many('performance.assessment.lines', 'per_id', string="Performance Assessment")

    total = fields.Float(string="Total", compute='_compute_total_line_mark_assessment', store=True)

    @api.depends('assess_line_ids.mark')
    def _compute_total_line_mark_assessment(self):
        for i in self:
            to = 0
            for j in i.assess_line_ids:
                to += j.mark
            i.total = to

    @api.model
    def create(self, vals):
        res = super(PerformanceAssessment, self).create(vals)
        if res.total > res.max_mark:
            raise ValidationError('Total Mark Greater Than Maximum Mark ! ')
        return res

    def write(self, vals):
        wr = super(PerformanceAssessment, self).write(vals)
        if self.total > self.max_mark:
            raise ValidationError('Total Mark Greater Than Maximum Mark !')
        return wr

    def action_approve_assessment(self):
        if self.assess_line_ids:
            for i in self.assess_line_ids:
                if i.mark > i.case_mark:
                    raise ValidationError(_("Employee Mark Greater Than Case Mark For Case: %s", i.case))
            if self.valuation_id:
                for j in self.valuation_id.emp_line_ids:
                    if j.performance_id.id == self.criteria_id.id:
                        j.obtained_mark = self.total
                self.state = 'approve'
            return {
                'effect': {
                    'fadeout': 'fast',
                    'message': 'Performance Assessment Approved',
                    'type': 'rainbow_man',
                }
            }
        else:
            raise ValidationError("There Is No Lines")


class PerformanceAssessmentLines(models.Model):
    _name = 'performance.assessment.lines'
    _description = 'Performance Assessment Lines'

    case = fields.Char(string='Case')
    case_mark = fields.Float(string="Case Mark")
    mark = fields.Float(string='Employee Mark')

    per_id = fields.Many2one('performance.assessment')
