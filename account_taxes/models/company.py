# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = "res.company"

    account_taxes = fields.Many2one(
        string="TCS/TDS Account",
        comodel_name='account.account',
        help="Account for TDS/TCS on invoices.")
