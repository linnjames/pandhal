from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_order_taxes = fields.Boolean(
        string="Allow TCS/TDS",
        implied_group='account_taxes.group_order_taxes',
        config_parameter='account.group_order_taxes',
        help="Allows TCS")
    account_taxes = fields.Many2one(
        string="Allow TCS/TDS Account",
        comodel_name='account.account',
        related="company_id.account_taxes",
        readonly=False,
        help="Allow TCS Account")

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        IrConfigPrmtr = self.env['ir.config_parameter'].sudo()
        IrConfigPrmtr.set_param('account.group_order_taxes',
                                self.group_order_taxes)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        IrConfigPrmtr = self.env['ir.config_parameter'].sudo()
        group_order_taxes = IrConfigPrmtr.get_param(
            'account.group_order_taxes')
        res.update({
            'group_order_taxes': group_order_taxes,
        })
        return res
