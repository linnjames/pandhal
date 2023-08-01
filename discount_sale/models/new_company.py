from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = 'res.company'
    _description = 'Company'

    manager_ids = fields.Many2many('res.users', string="Manager")
    user = fields.Many2many('res.users', 'rel_company_user', 'u_id', 'user_id', string='User')
    owner = fields.Many2many('res.users', 'rel_company_owner', 'o_id', 'owner_id', string='Owner')
    user_discount_ratio = fields.Char('User Discount Ratio', default=10)
    manager_discount_ratio = fields.Char('Manager Discount Ratio', default=20)
    owner_discount_ratio = fields.Char('Owner/Administrator Discount Ratio', default=30)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.constrains('discount_per')
    def _check_discount_percentage(self):
        for order in self:
            if not order.company_id or not order.user_id:
                continue

            privilege_level = self._get_privilege_level(order.user_id, order.company_id)

            if privilege_level == 'user' and order.discount_per != order.company_id.user_discount_ratio:
                raise ValidationError(
                    f"Invalid discount percentage. Allowed percentage for {order.user_id.company_id.name}: {order.company_id.user_discount_ratio}")

            elif privilege_level == 'manager' and order.discount_per not in [
                order.company_id.user_discount_ratio, order.company_id.manager_discount_ratio]:
                raise ValidationError(
                    f"Invalid discount percentage. Allowed percentages for {order.user_id.company_id.name}: {order.company_id.user_discount_ratio}, {order.company_id.manager_discount_ratio}")

            elif privilege_level == 'owner' and order.discount_per not in [order.company_id.user_discount_ratio,
                                                                                  order.company_id.manager_discount_ratio,
                                                                                  order.company_id.owner_discount_ratio]:
                raise ValidationError(
                    f"Invalid discount percentage. Allowed percentages for {order.user_id.company_id.name}: {order.company_id.user_discount_ratio}, {order.company_id.manager_discount_ratio}, {order.company_id.owner_discount_ratio}")

    def _get_privilege_level(self, user, company):
        if user.id in company.user.ids:
            return 'user'
        elif user.id in company.manager_ids.ids:
            return 'manager'
        elif user.id in company.owner.ids:
            return 'owner'
        return ''
