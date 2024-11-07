# -*- coding: utf-8 -*-
from datetime import timedelta, datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SupportCenter(models.Model):
    _name = 'support.center'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Support Task Records'
    _rec_name = 'sl_no'

    @api.depends('customer_contact_id')
    def _get_customer_company(self):
        for support_id in self:
            support_id.customer_id = support_id.customer_contact_id.parent_id

    def _default_date(self):
        return datetime.now()

    assigned_user_id = fields.Many2one(
        'res.users', string='Assigned To', tracking=True,
        default=lambda self: self.env.user)
    attended_user_id = fields.Many2one(
        'res.users', string='Attended By',
        default=lambda self: self.env.user)
    case_type = fields.Many2one('case.type', string='Case Type')
    customer_id = fields.Many2one(
        'res.partner', string='Client', compute='_get_customer_company',
        required=True)
    customer_contact_id = fields.Many2one(
        'res.partner', string='Client Contact', required=True,
        domain="[('parent_id', '!=', False)]")
    location_id = fields.Many2one('stock.location', string='Picking Location')
    invoice_id = fields.Many2one('account.move', string='Invoice')
    name = fields.Char(string='Description', required=True)
    sl_no = fields.Char(
        string='Sl No', required=True, default='New', copy=False)
    date_completed = fields.Datetime(string='Date Completed', copy=False)
    date_delivered = fields.Datetime(string='Date Delivered', copy=False)
    date_received = fields.Datetime(
        string='Case Registered On     ', required=True, copy=False,
        default=lambda self: self._default_date())
    date_rescheduled = fields.Datetime(string='Date Rescheduled', copy=False)
    date_scheduled = fields.Datetime(
        string='Expected Delivery', copy=False)
    internal_notes = fields.Html(string='Internal Notes', copy=False)
    issue_description = fields.Text(string='Description')
    product_line_ids = fields.One2many(
        'support.product.line', 'support_id', string='Products Used')
    priority = fields.Selection(
        [('high', 'Immediate'), ('medium', 'With in 48 Hours '),
         ('low', 'With in 7 Days')],
        string='Priority', default='low', required="True")
    service_type = fields.Selection(
        [('amc', 'AMC'), ('paid', 'Paid'), ('warranty', 'Warranty'),
         ('implementation', 'Implementation')],
        string='Service Type', default='')
    state = fields.Selection(
        [('draft', 'draft'), ('received', 'Received'),
         ('in_progress', 'In-Progress'), ('rescheduled', 'Rescheduled'),
         ('on_hold', 'On-Hold'), ('delivered', 'Delivered'),
         ('completed', 'Completed')], string='State', default='draft',
        tracking=True)
    solution_description = fields.Text(string='Solution Delivered')
    work_started_time = fields.Datetime(
        string='Work Started Time', readonly=True)
    total_working_time = fields.Char(
        string='Total Work Time', compute="time_duration")

    @api.constrains('expected_working_hour')
    def _check_expected_working_hour(self):
        if not self.expected_working_hour > 0:
            raise UserError(_('Expected Work Hour should be greater than 0'))
    expected_working_hour = fields.Float(string='Expected Work Hour', default='')

    @api.onchange('priority', 'date_received')
    def set_date_scheduled(self):
        if self.priority and self.date_received:
            if self.priority == 'low':
                self.date_scheduled = self.date_received + timedelta(days=7)
            elif self.priority == 'medium':
                self.date_scheduled = self.date_received + timedelta(days=2)
            elif self.priority == 'high':
                self.date_scheduled = self.date_received + timedelta(days=1)

    @api.constrains('assigned_user_id')
    def check_user_group(self):
        if not self.env.user.has_group('catalist_support.support_group_manager'):
            if self.assigned_user_id != self.env.user:
                raise UserError(_('Only manager can reassign ticket.'))

    def button_received(self):
        self.sl_no = self.env['ir.sequence'].next_by_code(
            'support.center') or _('New')
        if self.service_type != 'implementation':
            template = self.env.ref(
                'catalist_support.support_ticket_initiated_template',
                raise_if_not_found=False)
            print('template2', template)
            if template:
                email_values = {
                    'email_to': self.customer_contact_id.email,
                    'email_cc': self.customer_id.email,
                }
                template.send_mail(
                    self.id, email_values=email_values,
                    notif_layout='mail.mail_notification_light', force_send=True)
        self.state = 'received'

    def button_in_progress(self):
        self.state = 'in_progress'
        if not self.work_started_time:
            self.work_started_time = datetime.now()

    def button_delivered(self):
        self.date_delivered = datetime.now()
        if self.service_type != 'implementation':
            template = self.env.ref(
                'catalist_support.support_ticket_delivered_template',
                raise_if_not_found=False)
            print('template1', template)
            if template:
                email_values = {
                    'email_to': self.customer_contact_id.email,
                    'email_cc': self.customer_id.email,
                }
                template.send_mail(
                    self.id, email_values=email_values,
                    notif_layout='mail.mail_notification_light', force_send=True)

        picking_type_id = self.env['stock.picking.type'].search([
            ('code', '=', 'outgoing')], limit=1)
        location_dest_id = self.env['stock.location'].search([
            ('usage', '=', 'customer')], limit=1)

        if len(self.product_line_ids.ids):
            if not self.location_id.id:
                raise UserError(_('Please enter picking location.'))
            picking_id = self.env['stock.picking'].create({
                'partner_id': self.customer_id.id,
                'picking_type_id': picking_type_id.id,
                'location_id': self.location_id.id,
                'location_dest_id': location_dest_id.id,
            })
            for line_id in self.product_line_ids:
                picking_id.write({
                    'move_ids_without_package': [(0, 0, {
                        'name': line_id.product_id.partner_ref,
                        'date': picking_id.scheduled_date,
                        'date_deadline': picking_id.date_deadline,
                        'picking_type_id': picking_id.picking_type_id.id,
                        'location_id': picking_id.location_id.id,
                        'location_dest_id': picking_id.location_dest_id.id,
                        'company_id': self.env.company.id,
                        'product_id': line_id.product_id.id,
                        'product_uom_qty': line_id.quantity,
                        'product_uom': line_id.product_uom_id.id,
                    })]
                })
        self.state = 'delivered'

    def create_invoice(self):
        if self.customer_id.l10n_in_gst_treatment:
            l10n_in_gst_treatment = self.customer_id.l10n_in_gst_treatment
        else:
            l10n_in_gst_treatment = 'unregistered'
        journal_id = self.env['account.journal'].search([
            ('company_id', '=', self.env.company.id), ('type', '=', 'sale')],
            limit=1)

        move_id = self.env['account.move'].create({
            'partner_id': self.customer_id.id,
            'l10n_in_gst_treatment': l10n_in_gst_treatment,
            'invoice_user_id': self.env.user.id,
            'move_type': 'out_invoice',
            'journal_id': journal_id.id,
        })

        for line_id in self.product_line_ids:
            move_id.write({
                'invoice_line_ids': [(0, 0,  {
                    'product_id': line_id.product_id.id,
                    'quantity': line_id.quantity,
                    'name': line_id.name,
                    'price_unit': line_id.product_id.lst_price,
                    'product_uom_id': line_id.product_uom_id.id,
                    'tax_ids': [(6, 0, line_id.product_id.taxes_id.ids)],
                })]
            })
        self.invoice_id = move_id

    @api.depends('date_delivered', 'work_started_time')
    def time_duration(self):
        for rec in self:
            if rec.date_delivered and rec.work_started_time:
                total_time = rec.date_delivered - rec.work_started_time
                total_time = (
                        total_time -
                        timedelta(microseconds=total_time.microseconds))
                rec.total_working_time = total_time
            else:
                rec.total_working_time = False

    def button_reschedule(self):
        return {
            'name': _('Reschedule Wizard'),
            'res_model': 'ticket.reschedule.wizard',
            'view_mode': 'form',
            'context': {
                'default_ticket_id': self.id,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def button_on_hold(self):
        self.state = 'on_hold'

    def button_completed(self):
        self.date_completed = datetime.now()
        self.state = 'completed'
        if self.service_type != 'implementation':
            template = self.env.ref(
                'catalist_support.support_ticket_closed_template',
                raise_if_not_found=False)
            print('template', template)
            if template:
                email_values = {
                    'email_to': self.customer_contact_id.email,
                    'email_cc': self.customer_id.email,
                }
                template.send_mail(
                    self.id, email_values=email_values,
                    notif_layout='mail.mail_notification_light', force_send=True)

    def unlink(self):
        for records in self:
            if records.state != 'draft':
                raise UserError(_('You cannot delete completed Tickets.'))
        return super(SupportCenter, self).unlink()


class CaseType(models.Model):
    _name = 'case.type'
    _description = 'Case types for support ticket'

    name = fields.Char(string='Name', required=True)


class SupportProductLine(models.Model):
    _name = 'support.product.line'
    _description = 'Support Product Line'

    support_id = fields.Many2one('support.center', string='Support Ref')
    product_id = fields.Many2one(
        'product.product', string='Product', required=True)
    product_uom_category_id = fields.Many2one(
        related='product_id.uom_id.category_id', string='UoM Category')
    product_uom_id = fields.Many2one(
        'uom.uom', 'Unit of Measure', required=True,
        domain="[('category_id', '=', product_uom_category_id)]")
    name = fields.Char(string='Description', required=True)
    quantity = fields.Float(string='Quantity', default=1)

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id.id:
            self.product_uom_id = self.product_id.uom_id
            self.name = self.product_id.partner_ref
