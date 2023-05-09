from odoo import fields, models, api
from datetime import  date


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    applicable_tcs = fields.Boolean(string="TCS Applicable", default=False)
    tcs_section = fields.Many2one('tcs.management', string="TCS Section")
    tcs_type = fields.Selection([('with_pan', 'With PAN'), ('without_pan', 'Without PAN')], string="TCS Type")
    tcs_percentage = fields.Float(string="TCS %")
    tcs_account = fields.Many2one('account.account', string="TCS Account")
    tcs_limit = fields.Monetary(string="TCS Limit")
    applicable_tds = fields.Boolean(string="TDS Applicable", default=False)
    tds_section = fields.Many2one('tds.management', string="TDS Section")
    tds_type = fields.Selection([('with_pan', 'With PAN'), ('without_pan', 'Without PAN')], string="TDS Type")
    tds_percentage = fields.Float(string="TDS %")
    tds_account = fields.Many2one('account.account', string="TDS Account")
    tds_limit = fields.Monetary(string="TDS Limit")
    limit_date = fields.Date(string="Date Limit")
    pan_no = fields.Char(string='Pan No')

    @api.onchange('tcs_section')
    def onchange_tcs_section(self):
        if self.tcs_section:
            if self.tcs_section.tcs_type:
                self.tcs_type = self.tcs_section.tcs_type
            if self.tcs_section.tcs_percentage:
                self.tcs_percentage = self.tcs_section.tcs_percentage
            if self.tcs_section.tcs_account:
                self.tcs_account = self.tcs_section.tcs_account

    @api.onchange('tds_section')
    def onchange_tds_section(self):
        if self.tds_section:
            if self.tds_section.tds_type:
                self.tds_type = self.tds_section.tds_type
            if self.tds_section.tds_percentage:
                self.tds_percentage = self.tds_section.tds_percentage
            if self.tds_section.tds_account:
                self.tds_account = self.tds_section.tds_account

    @api.model
    def action_test_cron(self):
        partner = self.env['res.partner'].search([])
        x = date.today().strftime('%m-%d')
        if x == '04-01':
            for i in partner:
                i.limit_date = date.today()
