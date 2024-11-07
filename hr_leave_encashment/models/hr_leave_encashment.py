from calendar import monthrange

from odoo import fields, api, models, _
from odoo.exceptions import ValidationError
from datetime import datetime, date


class HrLeaveEncashment(models.Model):
    _name = 'hr.leave.encashment'
    _inherit = ['mail.thread']
    _order = 'name desc'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    department_id = fields.Many2one('hr.department', string="Department", related="employee_id.department_id",
                                    store=True)
    job_id = fields.Many2one('hr.job', string="Job", related="employee_id.job_id", store=True)
    manager_id = fields.Many2one('res.users', string="Manager", related="employee_id.parent_id.user_id", store=True)
    current_user = fields.Many2one('res.users', string="Current User", related='employee_id.user_id',
                                   default=lambda self: self.env.uid, store=True)
    name = fields.Char('Name', readonly=True, copy=False)
    project_id = fields.Many2one('project.project', string="Project")
    project_manager_id = fields.Many2one('res.users', string="Project Manager")
    contract_id = fields.Many2one('hr.contract', string="Contract")
    note = fields.Text(string='Note')
    state = fields.Selection([('draft', 'Draft'),
                              ('waiting', 'Waiting'),
                              ('approved', 'Approved'),
                              ('posted', 'Posted'),
                              ('refused', 'Refused'), ('cancel', 'Cancelled')], string="Status",
                             default="draft")
    debit_account_id = fields.Many2one('account.account', string='Debit Account', copy=False)
    credit_account_id = fields.Many2one('account.account', string='Credit Account', copy=False)
    journal_id = fields.Many2one('account.journal', string='Journal', copy=False)
    user_id = fields.Many2one('res.users', string='User', readonly=True, default=lambda self: self.env.user.id)
    company_id = fields.Many2one('res.company', string='Company', readonly=True,
                                 default=lambda self: self.env.company.id)
    date = fields.Date(string='Date', readonly=True, default=date.today())
    leave_type_id = fields.Many2one('hr.leave.type', string='Leave type', copy=False)
    no_of_days_left = fields.Float(string='No of days', copy=False)
    no_of_days_encash = fields.Float(string='No of days to Encash', copy=False)
    amount_per_hrs = fields.Float(string='Amount per Hours', copy=False)
    encashment_amount_total = fields.Float(string='Total Encashment Amount', copy=False)
    encashment_amount_balance = fields.Float(string='Balance Amount', copy=False)

    @api.onchange('employee_id', 'no_of_days_encash', 'leave_type_id')
    def _onchange_employee_id(self):
        self.no_of_days_left = False
        self.amount_per_hrs = False
        self.encashment_amount_total = False
        self.project_id = False
        if self.employee_id:
            if self.employee_id.contract_ids:
                for co in self.employee_id.contract_ids:
                    if co.state == 'open':
                        self.contract_id = co.id
                        dates = self.date
                        month_range = monthrange(dates.year, dates.month)[1]
                        amt = (((co.wage / month_range) / 8) * 2)
                        self.amount_per_hrs = amt
            else:
                self.contract_id = False
                self.amount_per_hrs = 0.00
        # else:
        #     self.contract_id = False
        #     self.amount_per_hrs = 0.00
        if self.contract_id and self.no_of_days_encash and self.amount_per_hrs:
            amts = self.amount_per_hrs * self.no_of_days_encash
            self.encashment_amount_total = amts
        # else:
        #     self.encashment_amount_total = 0.00
        if self.leave_type_id and self.employee_id and self.employee_id.contract_ids:
            left_days = self.env['hr.leave.report'].search(
                [('employee_id', '=', self.employee_id.id), ('state', '=', 'validate'),
                 ('holiday_status_id.active', '=', True), ('holiday_status_id', '=', self.leave_type_id.id)])
            left_holiday = 0
            for left in left_days:
                left_holiday += left.number_of_days
            self.no_of_days_left = left_holiday

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.leave.encashment') or _('New')
        res = super(HrLeaveEncashment, self).create(vals)
        return res

    def encashment_submit(self):
        self.state = 'waiting'

    def encashment_approve(self):
        if self.leave_type_id:
            leave = self.env['hr.leave'].create({
                'employee_id': self.employee_id.id,
                'department_id': self.department_id.id,
                # 'category_id': self.department_id.id,
                'mode_company_id': self.company_id.id,
                'holiday_status_id': self.leave_type_id.id,
                'number_of_days': self.no_of_days_encash,
                'name': 'Encashment of %s' % self.name
            })
            leave.action_approve()
            leave.action_validate()
        self.state = 'approved'

    def encashment_post(self):
        if self.employee_id.user_id:
            if self.debit_account_id and self.credit_account_id and self.journal_id:
                journal_entry = self.env['account.move'].create({
                    'ref': self.name,
                    'move_type': 'entry',
                    'journal_id': self.journal_id.id,
                    'company_id': self.company_id.id,
                    'currency_id': self.company_id.currency_id.id,
                    'payment_reference': self.name,
                    'date': self.date,
                    'line_ids': [
                        (0, 0, {
                            'account_id': self.credit_account_id.id,
                            'currency_id': self.company_id.currency_id.id,
                            'debit': 00.0,
                            'credit': round(self.encashment_amount_total),
                            'partner_id': self.employee_id.user_id.partner_id.id,
                        }),
                        (0, 0, {
                            'account_id': self.debit_account_id.id,
                            'currency_id': self.company_id.currency_id.id,
                            'debit': round(self.encashment_amount_total),
                            'credit': 0.0,
                            'partner_id': self.employee_id.user_id.partner_id.id,
                        }),
                    ],
                })
                journal_entry.action_post()
            else:
                raise ValidationError('Debit Account , Credit Account and Journal must be selected')
        else:
            raise ValidationError("Please set a 'Related User' for the employee")
        self.encashment_amount_balance = round(self.encashment_amount_total)
        self.state = 'posted'

    def encashment_refused(self):
        self.state = 'refused'

    def encashment_reset_draft(self):
        self.state = 'draft'

    def encashment_cancel(self):
        self.state = 'cancel'

    @api.onchange('no_of_days_encash')
    def _onchange_days_encash(self):
        if self.no_of_days_encash > self.no_of_days_left:
            raise ValidationError("'No of days to Encash' is greater than 'No of days'")
