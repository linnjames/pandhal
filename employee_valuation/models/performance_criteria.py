from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PerformanceCriteria(models.Model):
    _name = "performance.criteria"
    _description = "Performance Criteria"
    _rec_name = 'name'

    name = fields.Text(string='Name')
    department_id = fields.Many2one('hr.department', string='Department')
    team_lead_id = fields.Many2one('res.users', string="Team Lead")
    max_mark = fields.Float(string="Maximum Mark")
    min_mark = fields.Float(string='Minimum Mark')

    case_mark_ids = fields.One2many('criteria.mark', 'criteria_id', string="Add Mark")
    total = fields.Float(string='Total', compute='_compute_mark_total')

    state = fields.Selection(
        [('draft', 'Draft'), ('approve', 'Approve')],
        default='draft', string='Status', readonly=True)

    @api.model
    def create(self, vals):
        res = super(PerformanceCriteria, self).create(vals)
        if res.min_mark > res.max_mark:
            raise ValidationError('Minimum Mark Greater Than Maximum Mark !')
        if res.total > res.max_mark:
            raise ValidationError('Total Mark Greater Than Maximum Mark ! ')
        return res

    def write(self, vals):
        wr = super(PerformanceCriteria, self).write(vals)
        if self.min_mark > self.max_mark:
            raise ValidationError('Minimum Mark Greater Than Maximum Mark !')
        if self.total > self.max_mark:
            raise ValidationError('Total Mark Greater Than Maximum Mark !')
        return wr

    @api.onchange('department_id')
    def _onchange_performance_department(self):
        self.case_mark_ids = False
        if self.department_id:
            for i in self.department_id.criteria_line_ids:
                self.write({
                    'case_mark_ids': [(0, 0, {
                        'case': i.case,
                    })]
                })

    @api.depends('case_mark_ids.mark')
    def _compute_mark_total(self):
        for i in self:
            t = 0
            for j in i.case_mark_ids:
                t += j.mark
            i.total = t

    def action_approve_criteria(self):
        if self.case_mark_ids:
            for i in self.case_mark_ids:
                if i.mark <= 0:
                    raise ValidationError("Case Mark Should Be GreaterThan Zero")
            self.state = 'approve'
        else:
            raise ValidationError("There Is No Lines")


class CriteriaMark(models.Model):
    _name = 'criteria.mark'
    _description = 'Add Mark'

    case = fields.Char(string='Case')
    mark = fields.Float(string="Mark")
    criteria_id = fields.Many2one('performance.criteria')
