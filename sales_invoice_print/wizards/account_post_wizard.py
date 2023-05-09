from odoo import models, fields, api, _


class AccountPostWizard(models.TransientModel):
    _name = "account.post.wizard"
    _description = "Account Post"

    move_ids = fields.Many2many('account.move', string='Invoices')

    def default_get(self, fields):
        res = super(AccountPostWizard, self).default_get(fields)
        active_move_ids = self.env['account.move'].browse(self._context.get('active_ids')).ids
        account = self.env['account.move'].sudo().search([('id', 'in', active_move_ids)])
        res.update({
            'move_ids': [(6, 0, account.ids)],
        })
        return res

    def action_account_post(self):
        active_move_ids = self.env['account.move'].browse(self._context.get('active_ids')).ids
        account = self.env['account.move'].sudo().search([('id', 'in', active_move_ids)])
        for accounts in account:
            accounts.action_post()
