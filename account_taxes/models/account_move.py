import logging
import math

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    total_tcs_amount = fields.Monetary(string='Total TCS Amount',
                                       store=True, readonly=True, default=0, compute='_compute_amount')
    tcs_amount = fields.Monetary(string='TCS Amount', store=True,
                                 readonly=True, default=0, compute='_compute_tcs_amount', tracking=True)
    tcs_percentage = fields.Float(string='TCS Percentage', store=True, tracking=True)
    apply_tcs = fields.Boolean(string="Apply TCS")

    total_tds_amount = fields.Monetary(string='Total TDS Amount',
                                       store=True, readonly=True, default=0, compute='_compute_amount')
    tds_amount = fields.Monetary(string='TDS Amount', store=True,
                                 readonly=True, default=0, compute='_compute_tds_amount', tracking=True)
    tds_percentage = fields.Float(string='TDS Percentage', store=True, tracking=True)
    apply_tds = fields.Boolean(string="Apply TDS")

    tds_section = fields.Many2one('tds.management', string="TDS Section")
    tcs_section = fields.Many2one('tcs.management', string="TCS Section")

    tds_voucher = fields.Boolean(string='TDS Voucher')
    tcs_voucher = fields.Boolean(string='TCS Voucher')
    account_move_id = fields.Many2one('account.move', string='Bill/Invoice No')
    account_move_tcs_id = fields.Many2one('account.move', string='Bill/Invoice No')
    tds_section_id = fields.Many2one('tds.management', string='TDS Section')
    tcs_section_id = fields.Many2one('tcs.management', string='TCS Section')
    untaxed_bill_amount = fields.Float(string='Untaxed Bill Amount')
    untaxed_bill_tcs_amount = fields.Float(string='Untaxed Bill Amount')
    taxed_bill_amount = fields.Float(string='Taxed Bill Amount')
    taxed_bill_tcs_amount = fields.Float(string='Taxed Bill Amount')

    def action_post(self):
        res = super(AccountMove, self).action_post()
        if self.partner_id:
            if self.apply_tds:
                comp = self.env.company
                misce = self.env['account.journal'].search([('code', '=', 'TDS'), ('company_id', '=', comp.id)])
                if misce:
                    if self.move_type == 'out_invoice':
                        journal_entry = self.env['account.move'].create({
                            'ref': self.name,
                            'move_type': 'entry',
                            'journal_id': misce.id,
                            'apply_tds': self.apply_tds,
                            'company_id': comp.id,
                            'currency_id': comp.currency_id.id,
                            'partner_id': self.partner_id.id,
                            'commercial_partner_id': self.partner_id.id,
                            'payment_reference': self.name,
                            'invoice_partner_display_name': self.partner_id.name,
                            'l10n_in_gst_treatment': self.l10n_in_gst_treatment,
                            'date': self.invoice_date,
                            'account_move_id': self.id,
                            'tds_section_id': self.tds_section.id,
                            'tds_voucher': True,
                            'untaxed_bill_amount': self.amount_untaxed,
                            'taxed_bill_amount': self.amount_total,
                            'line_ids': [
                                (0, 0, {
                                    'account_id': self.partner_id.property_account_receivable_id.id,
                                    'currency_id': comp.currency_id.id,
                                    'debit': 0.0,
                                    'credit': math.ceil(self.tds_amount),
                                    'partner_id': self.partner_id.id,
                                }),
                                (0, 0, {
                                    'account_id': self.partner_id.tds_account.id,
                                    'currency_id': comp.currency_id.id,
                                    'debit': math.ceil(self.tds_amount),
                                    'credit': 0.0,
                                    # 'partner_id': self.partner_id.id,
                                }),
                            ],
                        })
                        journal_entry.action_post()
                    if self.move_type == 'in_invoice':
                        journal_entry = self.env['account.move'].create({
                            'ref': self.name,
                            'move_type': 'entry',
                            'journal_id': misce.id,
                            'apply_tds': self.apply_tds,
                            'company_id': comp.id,
                            'currency_id': comp.currency_id.id,
                            'partner_id': self.partner_id.id,
                            'commercial_partner_id': self.partner_id.id,
                            'payment_reference': self.name,
                            'date': self.invoice_date,
                            'invoice_partner_display_name': self.partner_id.name,
                            'l10n_in_gst_treatment': self.l10n_in_gst_treatment,
                            'account_move_id': self.id,
                            'tds_section_id': self.tds_section.id,
                            'tds_voucher': True,
                            'untaxed_bill_amount': self.amount_untaxed,
                            'taxed_bill_amount': self.amount_total,
                            'line_ids': [
                                (0, 0, {
                                    'account_id': self.partner_id.property_account_payable_id.id,
                                    'currency_id': comp.currency_id.id,
                                    'debit': math.ceil(self.tds_amount),
                                    'credit': 0.0,
                                    'partner_id': self.partner_id.id,
                                }),
                                (0, 0, {
                                    'account_id': self.partner_id.tds_account.id,
                                    'currency_id': comp.currency_id.id,
                                    'debit': 0.0,
                                    'credit': math.ceil(self.tds_amount),
                                    # 'partner_id': self.partner_id.id,
                                }),
                            ],
                        })
                        journal_entry.action_post()
                else:
                    raise ValidationError('No Journal for TDS in this company.')
            if self.apply_tcs:
                comp = self.env.company
                misce = self.env['account.journal'].search([('code', '=', 'TCS'), ('company_id', '=', comp.id)])
                if misce:
                    if self.move_type == 'in_invoice':
                        journal_entry = self.env['account.move'].create({
                            'ref': self.name,
                            'move_type': 'entry',
                            'journal_id': misce.id,
                            'apply_tcs': self.apply_tcs,
                            'company_id': comp.id,
                            'currency_id': comp.currency_id.id,
                            'partner_id': self.partner_id.id,
                            'commercial_partner_id': self.partner_id.id,
                            'payment_reference': self.name,
                            'invoice_partner_display_name': self.partner_id.name,
                            'l10n_in_gst_treatment': self.l10n_in_gst_treatment,
                            'account_move_tcs_id': self.id,
                            'tcs_section_id': self.tcs_section.id,
                            'tcs_voucher': True,
                            'date': self.invoice_date,
                            'untaxed_bill_tcs_amount': self.amount_untaxed,
                            'taxed_bill_tcs_amount': self.amount_total,
                            'line_ids': [
                                (0, 0, {
                                    'account_id': self.partner_id.property_account_payable_id.id,
                                    'currency_id': comp.currency_id.id,
                                    'debit': 0.0,
                                    'credit': math.ceil(self.tcs_amount),
                                    'partner_id': self.partner_id.id,
                                }),
                                (0, 0, {
                                    'account_id': self.partner_id.tcs_account.id,
                                    'currency_id': comp.currency_id.id,
                                    'debit': math.ceil(self.tcs_amount),
                                    'credit': 0.0,
                                    # 'partner_id': self.partner_id.id,
                                })
                            ]
                        })
                        journal_entry.action_post()
                else:
                    raise ValidationError('No Journal for TCS in this company.')
        return res

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        res = super(AccountMove, self)._onchange_partner_id()
        if self.partner_id:
            if self.move_type in ['out_invoice', 'in_invoice']:
                if self.partner_id.applicable_tds:
                    self.apply_tds = True
                    self.tds_section = self.partner_id.tds_section
                    self.tds_percentage = self.partner_id.tds_percentage
                    self._onchange_apply_tds()
                else:
                    self.apply_tds = False
                    self.tds_section = False
                    self.tds_percentage = False
                    self.tds_amount = 0
                if self.partner_id.applicable_tcs:
                    self.apply_tcs = True
                    self.tcs_section = self.partner_id.tcs_section
                    self.tcs_percentage = self.partner_id.tcs_percentage
                    self._onchange_apply_tcs()
                else:
                    self.apply_tcs = False
                    self.tcs_section = False
                    self.tcs_percentage = False
                    self.tcs_amount = 0
        return res

    @api.onchange('apply_tds')
    def _onchange_apply_tds(self):
        if self.apply_tds:
            if self.partner_id.tds_percentage:
                self.tds_percentage = self.partner_id.tds_percentage
                self.tds_section = self.partner_id.tds_section
            self.invoice_line_ids.tds = True
        else:
            self.tds_percentage = 0
            self.tds_section = 0
            self.invoice_line_ids.tds = False
            self.tds_amount = 0

    @api.onchange('apply_tcs')
    def _onchange_apply_tcs(self):
        if self.apply_tcs:
            if self.partner_id.tcs_percentage:
                self.tcs_percentage = self.partner_id.tcs_percentage
                self.tcs_section = self.partner_id.tcs_section
            self.invoice_line_ids.tcs = True
        else:
            self.tcs_percentage = 0
            self.tcs_section = 0
            self.invoice_line_ids.tcs = False
            self.tcs_amount = 0

    @api.depends('tds_percentage', 'apply_tds', 'invoice_line_ids.tds', 'invoice_line_ids.price_subtotal')
    def _compute_tds_amount(self):
        for move in self:
            if move.apply_tds and move.tds_percentage:
                tds_amt = 0
                for move_line in move.invoice_line_ids:
                    if move_line.tds:
                        tds_amt += (move.tds_percentage * move_line.price_subtotal) / 100
                    else:
                        pass
                move.tds_amount = math.ceil(tds_amt)
            else:
                move.tds_amount = 0

    @api.depends('tcs_percentage', 'apply_tcs', 'invoice_line_ids.tcs', 'invoice_line_ids.price_subtotal')
    def _compute_tcs_amount(self):
        for move in self:
            if move.apply_tcs and move.tcs_percentage:
                tcs_amt = 0
                for move_line in move.invoice_line_ids:
                    if move_line.tcs:
                        tcs_amt += (move.tcs_percentage * move_line.price_subtotal) / 100
                    else:
                        pass
                move.tcs_amount = math.ceil(tcs_amt)
            else:
                move.tcs_amount = 0

                
class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    is_global_line = fields.Boolean(string='TCS Amount Line',
                                    help="This field is used to separate global discount line.")
    tcs = fields.Boolean(string='TCS')
    tds = fields.Boolean(string='TDS', store=True)
