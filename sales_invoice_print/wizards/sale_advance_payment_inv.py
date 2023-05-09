from odoo import models, fields, api, _


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    # trip_id = fields.Many2one('trip.details', string='Trip')

    # def create_invoices(self):
    #     res = super(SaleAdvancePaymentInv, self).create_invoices()
    #     if res['res_id']:
    #         a = self.env['account.move'].browse(res['res_id'])
    #         a.trip_id = self.trip_id
    #     else:
    #         a = self.env['account.move'].search(res['domain'])
    #         for i in a:
    #             if not i.trip_id:
    #                 i.trip_id = self.trip_id
    #     return res

    # {'id': 208, 'name': 'Invoices', 'type': 'ir.actions.act_window', 'view_id': (615, 'account.out.invoice.tree'),
    #  'domain': [('id', 'in', [89505, 89504])], 'context': {'default_move_type': 'out_invoice'}, 'res_id': 0,
    #  'res_model': 'account.move', 'target': 'current', 'view_mode': 'tree,kanban,form',
    #  'views': [(615, 'tree'), (False, 'kanban'), (False, 'form')], 'limit': 80, 'groups_id': [],
    #  'search_view_id': (620, 'account.invoice.select'),

    # {'id': 208, 'name': 'Invoices', 'type': 'ir.actions.act_window', 'view_id': (615, 'account.out.invoice.tree'),
    #  'domain': "[('move_type', '=', 'out_invoice')]",
    #  'context': {'default_move_type': 'out_invoice', 'default_partner_id': 9, 'default_partner_shipping_id': 9,
    #              'default_invoice_payment_term_id': None, 'default_invoice_origin': 'NBCI-S02142',
    #              'default_user_id': 2}, 'res_id': 89508, 'res_model': 'account.move', 'target': 'current

