from odoo import api, fields, models, _
from datetime import date
from odoo.exceptions import Warning, ValidationError


class EmployeeValuation(models.Model):
    _name = 'employee.valuation'
    _description = 'Employee Valuation'
    _rec_name = 'reference'

    reference = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                            default=lambda self: _('New'))

    date = fields.Date(string='Date', default=lambda self: date.today())
    emp_id = fields.Many2one('hr.employee', string='Employee')
    department_id = fields.Many2one('hr.department', string='Department')
    exp_date = fields.Date(string='Expected Date')
    emp_line_ids = fields.One2many('employee.valuation.lines', 'valuation_id', string="Performance Evaluation")
    state = fields.Selection(
        [('draft', 'Draft'), ('confirm', 'Confirm'), ('valuation', 'Valuation'), ('approve', 'Approve')],
        default='draft', string='Status', readonly=True)

    result = fields.Selection(
        [('pass', 'Pass'), ('fail', 'Fail')],
        string='Result', compute='_compute_employee_result', readonly=True, store=True)

    @api.depends('emp_line_ids.result')
    def _compute_employee_result(self):
        for i in self:
            re = i.emp_line_ids.mapped('result')
            if any(r == 'fail' for r in re):
                i.result = 'fail'
            # elif all(r == 'pass' for r in re):
            #     i.result = 'pass'
            else:
                i.result = 'pass'

    @api.model
    def create(self, vals):
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('employee.valuation.code') or _('New')
        res = super(EmployeeValuation, self).create(vals)
        return res

    def action_request(self):
        if self.emp_line_ids:
            for i in self.emp_line_ids:
                per = self.env['performance.assessment'].sudo().create({
                    'valuation_id': self.id,
                    'employee_id': self.emp_id.id,
                    'department_id': self.department_id.id,
                    'criteria_id': i.performance_id.id,
                    'user_id': i.performance_id.team_lead_id.id,
                    'max_mark': i.performance_id.max_mark,
                    'min_mark': i.performance_id.min_mark
                })
                for j in i.performance_id.case_mark_ids:
                    per.write({
                        'assess_line_ids': [(0, 0, {
                            'case': j.case,
                            'case_mark': j.mark
                        })]
                    })
            self.state = 'valuation'
        else:
            raise Warning(_("There Is No Lines"))

    def action_confirm(self):
        self.state = 'confirm'

    def action_draft(self):
        self.state = 'draft'

    def action_approve(self):
        perform = self.env['performance.assessment'].sudo().search(
            [('valuation_id', '=', self.id), ('employee_id', '=', self.emp_id.id)])
        for i in perform:
            if i.state != 'approve':
                raise ValidationError(_("Performance Assessment Not Approved"))
        self.state = 'approve'
        return {
            'effect': {
                'fadeout': 'fast',
                'message': 'Employee Valuation Approved',
                'type': 'rainbow_man',
            }
        }

    def action_performance_assessment_records(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Performance Assessment',
            'res_model': 'performance.assessment',
            'view_mode': 'tree,form',
            'domain': [('valuation_id', '=', self.id), ('employee_id', '=', self.emp_id.id)],
            'context': {'create': False, 'delete': False},
        }

    @api.onchange('emp_id')
    def _onchange_valuation_employee(self):
        self.emp_line_ids = False
        self.department_id = False
        if self.emp_id:
            for i in self.emp_id.criteria_ids:
                self.write({
                    'emp_line_ids': [(0, 0, {
                        'performance_id': i.id,
                        'max_mark': i.max_mark,
                        'min_mark': i.min_mark,
                    })]
                })
            self.department_id = self.emp_id.department_id.id


class EmployeeValuationLines(models.Model):
    _name = 'employee.valuation.lines'
    _description = 'Valuation Lines'

    valuation_id = fields.Many2one('employee.valuation', readonly=True)
    performance_id = fields.Many2one('performance.criteria', string='Performance Criteria')
    max_mark = fields.Float(string='Maximum Mark')
    min_mark = fields.Float(string='Minimum Mark')
    obtained_mark = fields.Float(string='Obtained Mark')
    result = fields.Selection(
        [('pass', 'Pass'), ('fail', 'Fail')],
        string='Result', compute='_compute_line_result', readonly=True, store=True)

    @api.depends('obtained_mark', 'max_mark', 'min_mark')
    def _compute_line_result(self):
        for i in self:
            if i.obtained_mark < i.min_mark:
                i.result = 'fail'
            elif i.obtained_mark >= i.min_mark:
                i.result = 'pass'
