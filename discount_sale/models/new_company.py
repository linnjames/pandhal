from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = 'res.company'
    _description = 'Company'

    manager_ids = fields.Many2many('res.users', string="Manager")
    user = fields.Many2many('res.users', 'rel_company_user', 'u_id', 'user_id', string='User')
    owner = fields.Many2many('res.users', 'rel_company_owner', 'o_id', 'owner_id', string='Owner')
    user_discount_ratio = fields.Char('User Discount Ratio', default='10')
    manager_discount_ratio = fields.Char('Manager Discount Ratio', default='20')
    owner_discount_ratio = fields.Char('Owner/Administrator Discount Ratio', default='30')


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    company_ids = fields.Many2many('res.company', string='Related Companies')

    @api.constrains('discount_per')
    def _check_discount_percentage(self):
        for order in self:
            if not order.company_ids or not order.user_id or not order.discount_per:
                continue

            privilege_level = self._get_privilege_level(order.user_id, order.company_ids)

            allowed_discounts = []
            for company in order.company_ids:
                if privilege_level == 'user':
                    allowed_discounts.append(company.user_discount_ratio)
                elif privilege_level == 'manager':
                    allowed_discounts.extend([company.user_discount_ratio, company.manager_discount_ratio])
                elif privilege_level == 'owner':
                    allowed_discounts.extend(
                        [company.user_discount_ratio, company.manager_discount_ratio, company.owner_discount_ratio])

            if order.discount_per not in allowed_discounts:
                raise ValidationError(
                    f"Invalid discount percentage. Allowed percentages for {order.user_id.company_id.name}: {', '.join(allowed_discounts)}")

    def _get_privilege_level(self, user, company):
        if user.id in company.user.ids:
            return 'user'
        elif user.id in company.manager_ids.ids:
            return 'manager'
        elif user.id in company.owner.ids:
            return 'owner'
        return ''
