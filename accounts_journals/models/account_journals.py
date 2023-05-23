from odoo import models, fields, api, exceptions
from odoo.exceptions import ValidationError


class AccountAccount(models.Model):
    _inherit = 'account.account'

    set_limit = fields.Float(string="Limit Price")
    limit = fields.Boolean(string="Set Limit")
    negative_limit = fields.Boolean(srting='Negative Cash Limit')


class AccountMove(models.Model):
    _inherit = 'account.move'


    # def action_post(self):
    #     print('wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww')
    #     res = super().action_post()
    #     for j in self:
    #         print('qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq')
    #         for i in j.invoice_line_ids:
    #             print("oooooooooo")
    #             if j.move_type == 'in_invoice':
    #                 print("ppp")
    #                 if i.account_id.negative_limit:
    #                     if i.account_id.current_balance < 0:
    #                         print('eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee')
    #                         raise ValidationError("Balance should not be negative")
    #
    #                     elif i.account_id.current_balance - i.price_subtotal < 0:
    #                         print('rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr')
    #                         raise ValidationError("Balance should not be negative")
    #
    #                     else:
    #                         pass
    #             elif j.move_type == 'out_invoice':
    #                 if i.account_id.set_limit and i.account_id.set_limit < i.price_subtotal:
    #                     print('tttttttttttttttttttttttttttttttttttttttt')
    #                     raise ValidationError("Payment exceeds set limit on account")
    #     return res
    def _post(self, soft=True):
        res = super(AccountMove, self)._post(soft)
        print('wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww')
        print(res, '///////////////////')
        for move in res:
            if move.move_type == 'entry':
                print('sssssssssssssssssssssss')
                for line in move.line_ids:
                    print(line, 'llllllllllllllllll')
                    if line.account_id.limit:
                        # if line.account_id.set_limit > line.account_id.current_balance:
                        if line.account_id.current_balance > line.account_id.set_limit:
                            raise ValidationError("Payment exceeds set limit on account")

                        if line.account_id.negative_limit:
                            print('qqqqqqqqqqqqqqqqqqqqqqqqqqq')
                            if line.account_id.current_balance < 0:
                                raise ValidationError("Balance should not be negative")

        return res
