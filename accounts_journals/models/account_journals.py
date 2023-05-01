from odoo import models, fields, api, exceptions
from odoo.exceptions import ValidationError


class AccountAccount(models.Model):
    _inherit = 'account.account'


    set_limit = fields.Float(string="Set Limit")
    negative_limit = fields.Boolean(srting='Negative Cash Limit')


class AccountMove(models.Model):
    _inherit = 'account.move'

    # def action_post(self):
    #     res = super().action_post()
    #     for i in self.invoice_line_ids:
    #         if i.account_id.negative_limit:
    #             if i.account_id.current_balance < 0:
    #                 raise ValidationError("Balance should not be negative")
    #
    #             elif i.account_id.current_balance - i.price_subtotal < 0:
    #                 raise ValidationError("Balance should not be negative")
    #
    #             else:
    #                 pass
    #         if self.move_type == 'in_invoice':
    #             continue
    #             if i.account_id.set_limit and i.account_id.set_limit < i.price_subtotal:
    #                 raise ValidationError("Payment exceeds set limit on account")
    #
    #     return res

    def action_post(self):
        res = super().action_post()
        for j in self:
            for i in j.invoice_line_ids:
                if j.move_type == 'in_invoice':
                    if i.account_id.negative_limit:
                        if i.account_id.current_balance < 0:
                            raise ValidationError("Balance should not be negative")

                        elif i.account_id.current_balance - i.price_subtotal < 0:
                            raise ValidationError("Balance should not be negative")

                        else:
                            pass
                elif j.move_type == 'out_invoice':
                    if i.account_id.set_limit and i.account_id.set_limit < i.price_subtotal:
                        raise ValidationError("Payment exceeds set limit on account")
        return res
