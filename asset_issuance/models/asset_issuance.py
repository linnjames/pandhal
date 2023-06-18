from odoo import models, fields, api, _


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    asset_ids = fields.One2many('asset.transfer', 'default_employee_id', string='Assets')
    asset_count = fields.Integer(string='Asset Count', compute='_compute_asset_count')

    @api.depends('asset_ids')
    def _compute_asset_count(self):
        for employee in self:
            employee.asset_count = len(employee.asset_ids)

    def button_asset_issuance(self):
        pass

    def button_view_transfer(self):
        return {
            'name': _('Asset Transfer'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'tree,form',
            'domain': [('asset_wizard_id', '=', self.id)],
        }


class HrEmployee(models.Model):
    _inherit = "stock.picking"

    asset_wizard_id = fields.Integer(string='id')
