from odoo import _, models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.exceptions import Warning
from datetime import datetime, timedelta, date


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        print(res)
        rec = self.sudo()
        to_company_id = self.env['res.company'].sudo().search([
            ('partner_id', '=', rec.partner_id.id),
            ('id', '!=', self.env.company.id)
        ], limit=1, order='id desc')

        if to_company_id.is_branch:
            # Check for an existing sale order
            existing_sale_order = self.env["sale.order"].sudo().search([
                ("purchase_id", "=", rec.id),
                ("company_id", "=", to_company_id.id),
            ], limit=1)

            if not existing_sale_order:
                # Create a sale order when confirming the purchase order
                sale_order = (
                    self.env["sale.order"].with_user(self.env.user.id).sudo().create({
                        "company_id": to_company_id.id,
                        "client_order_ref": rec.name,
                        "indent_type": rec.indent_type,
                        "purchase_id": rec.id,
                        "partner_id": self.env.company.partner_id.id,
                        "validity_date": rec.date_planned,
                    })
                )
                print(sale_order, 'sale_order')

                for line in rec.order_line.sudo():
                    # Create sale order line
                    self.env["sale.order.line"].sudo().create({
                        "order_id": sale_order.id,
                        "message": line.message,
                        "product_id": line.product_id.id,
                        "product_uom": line.product_uom.id,
                        "product_uom_qty": line.product_qty,
                        'tax_id': False
                    })

                rec.partner_ref = sale_order.name

        else:
            pass



class PurchaseOrderLines(models.Model):
    _inherit = "purchase.order.line"

    message = fields.Char(string="Message")



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
                print(purchase_line.price_unit,'purchase_line.price_unit')

                # Update the tax_id based on the taxes of the sale order line
                taxes = sale_line.tax_id.filtered(
                    lambda tax: tax.company_id == self.company_id
                )
                purchase_line.taxes_id = [(6, 0, taxes.ids)]
                print(purchase_line.taxes_id,'purchase_line.taxes_id')

                # Calculate the subtotal based on the updated unit price and quantity
                purchase_line.price_subtotal = purchase_line.price_unit * purchase_line.product_qty
                print(purchase_line.price_subtotal,'purchase_line.price_subtotal')

        return res
class ResCompany(models.Model):
    _inherit = 'res.company'


    is_branch = fields.Boolean(string="Branch")