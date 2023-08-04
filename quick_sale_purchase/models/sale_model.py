# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    sh_purchase_count = fields.Integer(
        string='# of Purchases', compute='_compute_purchase', readonly=True)
    purchase_tick_count = fields.Integer(
        compute='_compute_purchase_tick', store=True)
    purchase_button_bool = fields.Boolean(string="Quick Purchase Bool", default=False, copy=False)

    # def _prepare_invoice(self):
    #     res = super(SaleOrder, self)._prepare_invoice()
    #     print(res)
    #     res['is_icing_bool'] = self.is_icing_bool
    #     return res

    @api.depends('order_line', 'order_line.tick')
    def _compute_purchase_tick(self):
        for rec in self:
            count = 0
            for line in rec.order_line:
                if line.tick:
                    count += 1
            rec.purchase_tick_count = count

    def _compute_purchase(self):
        purchase_order_obj = self.env['purchase.order']
        if self:
            for rec in self:
                rec.sh_purchase_count = 0
                po_count = purchase_order_obj.search_count(
                    [('sh_sale_order_id', '=', rec.id)])
                rec.sh_purchase_count = po_count

    def sh_action_view_purchase(self):
        purchase_order_obj = self.env['purchase.order']
        if self and self.id:
            if self.sh_purchase_count == 1:
                po_search = purchase_order_obj.sudo().search(
                    [('sh_sale_order_id', '=', self.id)], limit=1)
                if po_search:
                    return {
                        "type": "ir.actions.act_window",
                        "res_model": "purchase.order",
                        "views": [[False, "form"]],
                        "res_id": po_search.id,
                        "target": "self",
                    }
            if self.sh_purchase_count > 1:
                po_search = purchase_order_obj.sudo().search(
                    [('sh_sale_order_id', '=', self.id)])
                if po_search:
                    action = self.env.ref('purchase.purchase_rfq').sudo().read()[0]
                    action['domain'] = [('id', 'in', po_search.ids)]
                    action['target'] = 'self'
                    return action

    def sh_create_po(self):
        if not self.company_id.vendor:
            raise ValidationError((" Vendor should be added to the Current Company!"))
        """
            this method fire the action and open create purchase order wizard
        """
        view = self.env.ref('quick_sale_purchase.sh_purchase_order_wizard')
        # context = self.env.context
        context = {'default_ship_sale_order': self.id}
        return {
            'name': 'Create Purchase Order',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'purchase.order.wizard',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': context,
        }

    def action_check(self):
        if self.order_line:
            for line in self.order_line:
                line.tick = True

    def action_uncheck(self):
        if self.order_line:
            for line in self.order_line:
                line.tick = False


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    tick = fields.Boolean(string="Select Product", default=True)

    def btn_tick_untick(self):
        if self.tick == True:
            self.tick = False
        else:
            self.tick = True
