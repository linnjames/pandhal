from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    multi_user = fields.Boolean(string='Multi User Report')

    mail_ids = fields.Many2many('res.users', 'res_company_favorite_users_rel', 'company_id', 'user_id',  string='User To Mail')
