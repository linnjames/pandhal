from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    total_amount = fields.Float(string='Total Amount', compute='_compute_total_amount')
    currency_id = fields.Many2one('res.currency', string='Currency')
    amount_in_words = fields.Char(string='Amount In Words', compute='_compute_total_amount_in_words')

    @api.depends('move_line_ids')
    def _compute_total_amount(self):
        for picking in self:
            picking.total_amount = sum(
                move_line.product_id.standard_price * move_line.qty_done for move_line in picking.move_line_ids)


    @api.depends('total_amount', 'currency_id')
    def _compute_total_amount_in_words(self):
        INR = self.env['res.currency'].search([('name', '=', 'INR')])

        for move in self:
            if move.total_amount:
                total = move.total_amount
                move.amount_in_words = INR.amount_to_text(total)
            else:
                move.amount_in_words = False




class AccountInvoice(models.Model):
    _inherit = 'account.move'

    total_amount = fields.Float(string='Total Amount', compute='_compute_total_amount')
    amount_in_words = fields.Char(string='Amount In Words', compute='_compute_total_amount_in_words')

    @api.depends('invoice_line_ids')
    def _compute_total_amount(self):
        for invoice in self:
            invoice.total_amount = sum(
                line.price_subtotal for line in invoice.invoice_line_ids)

    @api.depends('total_amount', 'currency_id')
    def _compute_total_amount_in_words(self):
        INR = self.env['res.currency'].search([('name', '=', 'INR')])

        for invoice in self:
            if invoice.total_amount and invoice.currency_id.name == 'INR':
                total = invoice.total_amount
                invoice.amount_in_words = INR.amount_to_text(total)
            else:
                invoice.amount_in_words = False



