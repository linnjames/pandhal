from odoo import api, fields, models, _
from datetime import datetime, date
from odoo.exceptions import AccessDenied, ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    mrp = fields.Float(string='MRP', tracking=True)
    mrp_line_ids = fields.One2many('mrp.details.line', 'product_id', string='MRP DETAILS',readonly=True)
    # mrp_updated_ids = fields.One2many('mrp.line', 'temp_id', string='MRP_Updated_line')
    product_category_type_id = fields.Many2one('product.category.type', string="Product Category Type", tracking=True)
    mrp_updated_date = fields.Datetime(string="MRP Updated Date",tracking=True)
    user_name = fields.Many2one('res.users', string="Updated by", default=lambda self: self.env.user.partner_id.id,
                                tracking=True)
    # internal_references = fields.Char(string='Internal References', required=True, copy=False, readonly=True,
    #                                   default=lambda self: _('New'))
    #
    # @api.model
    # def create(self, vals):
    #     if vals.get('internal_references', _('New')) == _('New'):
    #         vals['internal_references'] = self.env['ir.sequence'].next_by_code('product.template') or _('New')
    #     res = super(ProductTemplate, self).create(vals)
    #     return res

    # -------------------mrp updation__________
    @api.onchange('mrp')
    def onchange_mrp(self):
        if self.mrp:
            new_mrp_line = self.env['mrp.details.line'].new({
                'mrp_updated_date': fields.Datetime.now(),
                'user_name': self.user_name.id,
                'mrp_updated_value': self.mrp,
                'product_id': self.product_category_type_id,

            })
            self.mrp_line_ids += new_mrp_line

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

    # -------------------mrp (sale.order.line)__________
    # def __init__(self, env, ids, prefetch_ids):
    #     super().__init__(env, ids, prefetch_ids)
    #     self.product_id = None

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.update({'mrp': self.product_id.mrp})


class MrpUpdationDetailsLine(models.Model):
    _name = 'mrp.details.line'
    _description = "MRP Updation Details"

    product_id = fields.Many2one('product.template', string="product id ")
    mrp_line_ids = fields.One2many('mrp.details.line', 'product_id', string='MRP DETAILS')
    mrp_updated_value = fields.Float(string="Updated MRP ")
    # mrp_updated_date = fields.Datetime(string="MRP Updated Date", default=fields.Datetime.now, tracking=True)
    mrp_updated_date = fields.Datetime(string="MRP Updated Date")
    user_name = fields.Many2one('res.users', string="Updated by", default=lambda self: self.env.user.partner_id.id)
