
from odoo import api, fields, models, _



class HrEmployee(models.Model):
    _inherit = "hr.employee"

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

