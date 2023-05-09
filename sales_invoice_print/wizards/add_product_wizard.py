from odoo import models, fields, api, _


class AddProductWizard(models.TransientModel):
    _name = "add.product.wizard"

    move_id = fields.Many2one('account.move', string='Move')
    product_ids = fields.Many2many('product.product', string='Products')
    productids = fields.Many2many('product.product', 'add_product_rel', 'wiz_id', 'product_id', string='Products')

    def action_add(self):
        if self.product_ids and self.move_id:
            self.move_id.invoice_line_ids = False
            for i in self.product_ids:
                self.move_id.write({
                    'invoice_line_ids': [(0, 0, {
                        'move_id': self.move_id.id,
                        'product_id': i.id,
                    })]})
