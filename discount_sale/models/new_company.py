from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'
    _description = 'Company'

    manager_ids = fields.Many2many('res.users', string="Manager")
    user = fields.Many2many('res.users', 'rel_company_user', 'u_id', 'user_id', string='User')
    owner = fields.Many2many('res.users', 'rel_company_owner', 'o_id', 'owner_id', string='Owner')
    manager_discount = fields.Integer(string="Manager Discount Ratio")
    user_discount = fields.Integer(string="User Discount Ratio")
    owner_discount = fields.Integer(string="Owner Discount Ratio")
