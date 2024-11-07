# -*- coding: utf-8 -*-
from odoo import models, fields


class TicketRescheduleWizard(models.Model):
    _name = 'ticket.reschedule.wizard'
    _description = 'Ticket Reschedule Wizard'

    ticket_id = fields.Many2one('support.center', string='Ticket')
    date_rescheduled = fields.Datetime(
        string='Date Rescheduled', required=True)

    def action_reschedule_date(self):
        self.ticket_id.date_rescheduled = self.date_rescheduled
        self.ticket_id.state = 'rescheduled'
        if self.ticket_id.service_type != 'implementation':
            template = self.env.ref(
                'catalist_support.support_ticket_reschedule_template',
                raise_if_not_found=False)
            if template:
                email_values = {
                    'email_to': self.ticket_id.customer_contact_id.email,
                    'email_cc': self.ticket_id.customer_id.email,
                }
                template.send_mail(
                    self.ticket_id.id, email_values=email_values,
                    notif_layout='mail.mail_notification_light', force_send=True)
