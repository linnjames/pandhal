from odoo import api,fields, models, _
from ast import literal_eval


class ResConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'
    multi_user = fields.Boolean(string='Multi User Report')

    mail_ids = fields.Many2many('res.users', 'res_company_favorite_users_rel', 'company_id', 'user_id',
                                string='User To Mail')

    def set_values(self):
        super(ResConfigSetting, self).set_values()
        IrConfigPrmtr = self.env['ir.config_parameter'].sudo()
        IrConfigPrmtr.set_param('multi_scrap_orders.multi_user', self.multi_user)
        IrConfigPrmtr.set_param('multi_scrap_orders.mail_ids', self.mail_ids.ids)

    def get_values(self):
        res = super(ResConfigSetting, self).get_values()
        IrConfigPrmtr = self.env['ir.config_parameter'].sudo()
        multi_user = IrConfigPrmtr.get_param('multi_scrap_orders.multi_user')
        user_id = IrConfigPrmtr.get_param('multi_scrap_orders.mail_ids')
        res.update(
            mail_ids=[(6, 0, literal_eval(user_id))] if user_id else False
        )
        res.update({
            'multi_user': multi_user
        })
        return res
