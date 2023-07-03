# -*- coding: utf-8 -*-

import time

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class UpdateUsdToIneWizard(models.TransientModel):
    _name = "update.usd.to.inr.wizard"
    _description = "Update USD to INR"

    def _get_default_move(self):
        move_ids = self.env['account.move'].browse(self._context.get('active_ids', [])).ids
        move = self.env['account.move'].search([('state', 'in', ('posted',)), ('id', 'in', move_ids)]).ids
        return move

    move_ids = fields.Many2many('account.move', string='Orders', default=_get_default_move)

    def multi_update_inr_converted_amount(self):
        if self.move_ids:
            for move_id in self.move_ids:
               for line in move_id.invoice_line_ids:
                   line.convert_inr_amount = line.move_id.convert_inr * line.price_subtotal


        return {
            'effect': {
                'fadeout': 'fast',
                'message': 'Successful',
                'img_url': '/web/static/src/img/smile.svg',
                'type': 'rainbow_man',
            }
        }
