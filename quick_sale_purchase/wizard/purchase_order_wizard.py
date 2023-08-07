# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError


class PurchaseOrderWizard(models.TransientModel):
    _name = 'purchase.order.wizard'
    _description = "Purchase Order Wizard"

    order_line = fields.One2many(
        'purchase.order.line.wizard', 'wizard_id', string='Order Lines')
    expected_delivery_date = fields.Datetime(string=" Expected Delivery")
    # sale_attachment = fields.Binary(string="Attachment")
    order_type = fields.Selection([('indent', 'Indent'),
                                    ('store', 'Store'),
                                    ('customer order', 'Customer Order')], required=True)
    date_expected_delivery = fields.Date(string=" Expected Delivery")
    vendor_id = fields.Many2one('res.partner',string='vendor')

    def sh_create_purchase_order(self):
        if not self.vendor_id.id:
            raise ValidationError(_(" Vendors should be added to the Current Company!"))

        active_so_id = self.env.context.get("active_id")
        purchase_order_lines = []

        for partner in self.order_line:
            vals = {
                'product_id': partner.product_id.id,
                'name': partner.name,
                'product_uom': partner.product_id.uom_id.id,
                'product_qty': partner.product_qty,
                'price_unit': partner.price_unit,
                'message': partner.message,
            }
            purchase_order_lines.append((0, 0, vals))

        vals = {
            'partner_id': self.vendor_id.id,
            'sh_sale_order_id': active_so_id,
            'date_planned': self.expected_delivery_date,
            'indent_type': self.order_type,
            'order_line': purchase_order_lines,
        }
        created_po = self.env['purchase.order'].create(vals)
        created_po.button_confirm()

    @api.model
    def default_get(self, fields):
        res = super(PurchaseOrderWizard, self).default_get(fields)
        active_so_id = self.env.context.get("active_id")
        sale_order_obj = self.env['sale.order']
        if active_so_id:
            sale_order_search = sale_order_obj.search(
                [('id', '=', active_so_id)], limit=1)
            vendor = sale_order_search.company_id.vendor
            if sale_order_search and sale_order_search.order_line:
                tick_order_line = []
                for rec in sale_order_search.order_line:
                    if rec.tick:
                        tick_order_line.append(rec.id)
                if len(tick_order_line) > 0:
                    result = []
                    for record in sale_order_search.order_line.search([('id', 'in', tick_order_line)]):
                        result.append((0, 0, {'product_id': record.product_id.id,
                                              'name': record.name,
                                              'product_qty': record.product_uom_qty,
                                              'price_unit': record.price_unit,
                                              'product_uom': record.product_uom.id,
                                              # 'unit_mrp': rec.price_mrp,
                                              'message': rec.message,
                                              'price_subtotal': record.price_unit * rec.product_uom_qty
                                              }))

                    res.update({
                        'order_line': result,
                        'vendor_id':vendor,
                        'date_expected_delivery': sale_order_search.validity_date,
                        'order_type': sale_order_search.indent_type,
                    })

                elif len(tick_order_line) == 0:
                    result = []
                    for records in sale_order_search.order_line:
                        result.append((0, 0, {'product_id': records.product_id.id,
                                              'name': records.name,
                                              'product_qty': records.product_uom_qty,
                                              'price_unit': records.product_id.standard_price,
                                              'product_uom': records.product_uom.id,
                                              # 'message': rec.message,
                                              'price_subtotal': records.price_unit * records.product_uom_qty
                                              }))
                    res.update({
                        'order_line': result,
                        'date_expected_delivery': sale_order_search.validity_date,
                        'order_type': sale_order_search.indent_type,
                    })
        return res

