from odoo import models, fields
class SaleOrderInherit(models.Model):
    _inherit = "sale.order"

    order_type = fields.Selection(
        [('indent', 'Indent'), ('customer_order', 'Customer Order')],
        string="Order Type")

    is_confirmed = fields.Boolean(string="Confirmed", default=False, invisible=True)

    def action_quick_sale(self):
        self.is_confirmed = True
        self.action_confirm()

    def action_confirm(self):
        res = super(SaleOrderInherit, self).action_confirm()
        print(res)

        rec = self.sudo()
        to_company_id = self.env['res.company'].sudo().search([('partner_id', '=', rec.partner_id.id),
                                                               ('id', '!=', self.env.company.id)], limit=1,
                                                              order='id desc')
        print(to_company_id, 'to_company')
        if self.is_confirmed:
            purchase_order = (
                self.env["purchase.order"].with_user(self.env.user.id).sudo().create({
                    "company_id": to_company_id.id,
                    "partner_ref": rec.name,
                    # "sales_id": rec.id,
                    "partner_id": self.env.company.partner_id.id,
                    "date_order": rec.date_order,

                })
            )
            print(purchase_order, 'purchase_order')
            for line in rec.order_line.sudo():
                purchase_order.sudo().write({
                    'order_line': [(0, 0, {
                        "order_id": purchase_order.id,
                        "product_id": line.product_id.id,
                        "product_uom": line.product_uom.id,
                        "product_qty": line.product_uom_qty,
                        "available_qty": line.qty_invoiced,
                        "price_unit": line.price_unit,
                        'taxes_id': False
                    })
                                   ]})
            purchase_order.button_confirm()
