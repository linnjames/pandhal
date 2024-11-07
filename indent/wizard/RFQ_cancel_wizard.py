from odoo import models, fields, api


class RFQCancelWizard(models.TransientModel):
    _name = 'rfq.cancel.wizard'
    _description = 'RFQ Cancel Wizard'

    reason = fields.Text(string='Reason', widget='text')

    def cancel_rfqs(self):
        active_ids = self.env.context.get('active_ids', [])
        rfqs = self.env['purchase.order'].browse(active_ids)
        rfqs.write({'state': 'cancel', 'reason': self.reason})
        for rfq in self.env['purchase.order'].browse(active_ids):
            rfq.write({
                'reason': self.reason
            })
        return {'type': 'ir.actions.act_window_close'}


class PurchaseState(models.Model):
    _inherit = 'purchase.order'

    reason = fields.Text(string='Cancellation Reason')

    def action_rfq_cancel_wizard(self):
        active_ids = self._context.get('active_ids', [])

        return {
            'name': 'Cancel RFQ Reason',
            'type': 'ir.actions.act_window',
            'res_model': 'rfq.cancel.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('indent.view_rfq_cancel_wizard_form').id,
            'target': 'new',
            'context': {'active_ids': active_ids,
                        'reason': self.reason,
                        }
        }