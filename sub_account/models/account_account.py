from odoo import models, fields, api, exceptions


class AccountAccount(models.Model):
    _inherit = 'account.account'

    parent_account_id = fields.Many2one("account.account", string="Parent Account")

    # @api.onchange("parent_account_id")
    # def account_type(self):
    #     print("ooooooooooooooooooooo")
    #     for rec in self:
    #         rec.account_type = rec.parent_account_id.account_type



