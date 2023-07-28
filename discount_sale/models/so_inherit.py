from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    total_price = fields.Float(string="Total Price", compute='_compute_line_amount', store=True)
    discount_amt = fields.Float(string="Discount", compute='_compute_lines_discount_amount', store=True)
    is_discount_sale = fields.Boolean(string="Is Discount Sale")

    @api.depends('order_line.discount', 'order_line.price_unit')
    def _compute_lines_discount_amount(self):
        print("eeeeeeeeeeeeeeeeeeeeeeeee")
        if self.is_discount_sale:
            for record in self:
                disc_amt = 0.0
                for line in record.order_line:
                    disc_amt += (line.price_unit * line.discount / 100)
                record.discount_amt = disc_amt

    @api.depends('order_line.product_uom_qty', 'order_line.price_unit')
    def _compute_line_amount(self):
        print("ppppppppppppppppppppppppppp")
        if self.is_discount_sale:
            for order in self:
                tot = 0
                for line in order.order_line:
                    tot += (line.product_uom_qty * line.price_unit)
                order.total_price = tot

class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    subtotal = fields.Float(string="Subtotal", compute="compute_amount_subtotal", store=True)

    @api.depends('product_uom_qty', 'price_unit')
    def compute_amount_subtotal(self):
        print("ssssssssssssssssssssssssss")
        for order in self:
            sub = 0
            for line in self:
                sub += (line.product_uom_qty * line.price_unit)
            order.subtotal = sub


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    total_price = fields.Float(string="Total Price", compute='_compute_price_account_move', store=True)
    discount_amt = fields.Float(string="Discount", compute='_compute_discount_account_move', store=True)

    @api.depends('invoice_line_ids.quantity', 'invoice_line_ids.price_unit')
    def _compute_price_account_move(self):
        print("lllllllllllllllllllll")
        for order in self:
            tot = 0
            for line in order.invoice_line_ids:
                tot += (line.quantity * line.price_unit)
            order.total_price = tot

    @api.depends('invoice_line_ids.discount', 'invoice_line_ids.price_unit')
    def _compute_discount_account_move(self):
        print("kkkkkkkkkkkkkkkkkkkkkkkkkk")
        for record in self:
            disc_amt = 0.0
            for line in record.invoice_line_ids:
                disc_amt += (line.price_unit * line.discount / 100)
            record.discount_amt = disc_amt


class AccountMoveLineInherit(models.Model):
    _inherit = 'account.move.line'

    subtotal = fields.Float(string="Subtotal", compute="compute_amount_subtotal_accounts", store=True)

    @api.depends('quantity', 'price_unit')
    def compute_amount_subtotal_accounts(self):
        print("ffffffffffffffffffffffff")
        for order in self:
            sub = 0
            for line in self:
                sub += (line.quantity * line.price_unit)
            order.subtotal = sub
