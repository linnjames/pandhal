from odoo import _, models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.exceptions import Warning
from datetime import datetime, timedelta, date


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    has_been_confirmed = fields.Boolean(default=False, copy=False)

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        print(res)
        rec = self.sudo()
        to_company_id = self.env['res.company'].sudo().search([('partner_id', '=', rec.partner_id.id),
                                                               ('id', '!=', self.env.company.id)], limit=1,
                                                              order='id desc')
        if to_company_id.is_branch == True:
            # Create a sale order when confirming the purchase order
            sale_order = (
                self.env["sale.order"].with_user(self.env.user.id).sudo().create({
                    "company_id": to_company_id.id,
                    "client_order_ref": rec.name,
                    # 'indent_type': rec.indent_type,
                    "purchase_id": rec.id,
                    "partner_id": self.env.company.partner_id.id,
                    "validity_date": rec.date_planned,
                    # new field/----------------,
                })
            )
            print(sale_order, 'sale_order')
            for line in rec.order_line.sudo():
                tax_lst = []
                for tax in line.product_id.taxes_id.sudo():
                    tax_lst.append(tax.name)
                tax_id = self.env['account.tax'].sudo().search([('name', 'in', tuple(tax_lst)),
                                                                ('type_tax_use', '=', 'sale'),
                                                                ('company_id', '=', to_company_id.id)])

                a = line.product_id.taxes_id.filtered(lambda r: r.company_id == to_company_id)

                sale_order.sudo().write({
                    'order_line': [(0, 0, {
                        "order_id": sale_order.id,
                        "product_id": line.product_id.id,
                        "product_uom": line.product_uom.id,
                        "product_uom_qty": line.product_qty,
                        'tax_id': [(6, 0, tax_id.ids)]
                    })
                                   ]})
            rec.partner_ref = sale_order.name
        else:
            pass

    def button_cancel(self):
        for order in self:
            if order.has_been_confirmed:
                # Find the related RFQ (Purchase order) for the sale order
                rfq = self.env["purchase.order"].search([
                    ("sale_order_id", "=", order.id),
                    ("state", "=", "draft"),
                ], limit=1)

                # Cancel the RFQ if it exists
                if rfq:
                    rfq.button_cancel()

                # Clear the flag indicating the order has been confirmed
                order.has_been_confirmed = False

        # Call the original button_cancel method to handle standard cancellation process
        res = super(PurchaseOrder, self).button_cancel()

        return res


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    purchase_id = fields.Many2one('purchase.order', string='Purchase')

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        validity = self.env['stock.picking'].sudo().search([('origin', '=', self.name)])
        validity.scheduled_date = self.validity_date

        for sale_line in self.order_line:
            purchase_line = self.sudo().purchase_id.order_line.filtered(
                lambda line: line.product_id.id == sale_line.product_id.id
            )
            if purchase_line:
                # Calculate the unit price based on the sale price
                purchase_line.price_unit = sale_line.price_unit
                print(purchase_line.price_unit, 'purchase_line.price_unit')

                # Update the tax_id based on the taxes of the sale order line
                taxes = sale_line.tax_id.filtered(
                    lambda tax: tax.company_id == self.company_id
                )
                purchase_line.taxes_id = [(6, 0, taxes.ids)]
                print(purchase_line.taxes_id, 'purchase_line.taxes_id')

                # Calculate the subtotal based on the updated unit price and quantity
                purchase_line.price_subtotal = purchase_line.price_unit * purchase_line.product_qty
                print(purchase_line.price_subtotal, 'purchase_line.price_subtotal')

        return res

    def action_cancel(self):
        for order in self:
            # Find the related Purchase Order (RFQ) for the sale order
            purchase_order = self.env["purchase.order"].search([
                ("origin", "=", order.name),
                ("state", "in", ["draft", "sent"]),
            ], limit=1)

            # Cancel the Purchase Order (RFQ) if it exists and in draft or sent state
            if purchase_order:
                purchase_order.button_cancel()

            # Cancel the quotation (draft or sent state)
            if order.state in ["draft", "sent"]:
                order.state = "cancel"

        # Call the original action_cancel method to handle standard cancellation process
        res = super(SaleOrder, self).action_cancel()

        return res
