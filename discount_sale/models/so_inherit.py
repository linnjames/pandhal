from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    total_price = fields.Float(string="Total Price", compute='_compute_line_amount', store=True)
    discount_amt = fields.Float(string="Discount", compute='_compute_lines_discount_amount', store=True)
    is_discount_sale = fields.Boolean(string="Is Discount Sale")

    def action_confirm(self):
        res = super(SaleOrderInherit, self).action_confirm()
        user = self.env.user
        company = self.env.company
        total_discount = 0
        if self.is_discount_sale:
            discount = (self.discount_amt / self.total_price) * 100
            total_discount = discount
            user_discount_ratio = float(company.user_discount_ratio)
            manager_discount_ratio = float(company.manager_discount_ratio)
            owner_discount_ratio = float(company.owner_discount_ratio)
            if user.id in company.user.ids and total_discount <= user_discount_ratio:
                return res
            elif user.id in company.manager_ids.ids and total_discount <= manager_discount_ratio:
                return res
            elif user.id in company.owner.ids and total_discount <= owner_discount_ratio:
                return res
            else:
                raise UserError(
                    _("Your discount limit is exceeded! \n Kindly contact to your Administrator/Manager."))
        else:
            return res

    @api.depends('order_line.discount', 'order_line.price_unit', 'order_line.product_uom_qty')
    def _compute_lines_discount_amount(self):
        for record in self:
            disc_amt = 0.0
            for line in record.order_line:
                disc_amt += (line.product_uom_qty * line.price_unit * line.discount / 100)
            record.discount_amt = disc_amt

    @api.depends('order_line.product_uom_qty', 'order_line.price_unit')
    def _compute_line_amount(self):
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
        for order in self:
            tot = 0
            for line in order.invoice_line_ids:
                tot += (line.quantity * line.price_unit)
            order.total_price = tot

    @api.depends('invoice_line_ids.discount', 'invoice_line_ids.price_unit')
    def _compute_discount_account_move(self):
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
        for order in self:
            sub = 0
            for line in self:
                sub += (line.quantity * line.price_unit)
            order.subtotal = sub
