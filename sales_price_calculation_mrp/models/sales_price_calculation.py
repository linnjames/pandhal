from odoo import api, fields, models, _
from odoo.exceptions import AccessDenied, ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    mrp = fields.Float(string='MRP')

    product_category_type_id = fields.Many2one('product.category.type', string="Product Category Type")

    def action_mrp(self):
        # for mrp in self:
        qq = []
        self.list_price = 0
        amount_tax = 0
        sum_taxes = 0
        for i in self.taxes_id:
            if i.amount_type == 'group':
                sum_taxes += sum(i.children_tax_ids.mapped('amount'))
            else:
                if i.amount == 0:
                    # self.list_price = self.unit_mrp
                    self.list_price = self.mrp
                sum_taxes += i.amount

        # if (self.list_price <= self.unit_mrp) and (sum_taxes == 0):
        #     for j in self.taxes_id.children_tax_ids:
        #         print("J:", j.amount)
        #         amount_tax += j.amount
        #
        #         z = self.unit_mrp / (1 + (amount_tax / 100))
        #         re = "{:.2f}".format(z)
        #         # print(int(res))
        #         print(float(re))
        #         mm = float(re)
        #         print('kkkkkkkkkkkk', mm)
        #         print(self.list_price, "qqqqq")
        #
        #         # mrp.list_price = mrp.unit_mrp - sum_taxes

        # if self.list_price <= self.unit_mrp:
        if self.list_price <= self.mrp:
            # b = self.unit_mrp / (1 + (sum_taxes / 100))
            b = self.mrp / (1 + (sum_taxes / 100))
            print(b, "bbbbbbbbb")
            aa = "{:.4f}".format(b)
            print(aa, "aaaaaaaaa")
            mm = float(aa)
            self.list_price = mm

        if self.list_price < 0:
            raise ValidationError(("Product Sales price is should not less than Zero"))

    @api.onchange('taxes_id')
    def compute_taxes_id(self):
        self.list_price = False


class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    mrp = fields.Float(string='MRP')

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.mrp = self.product_id.mrp
