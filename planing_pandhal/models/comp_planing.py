from odoo import api, fields, models, _
from odoo.exceptions import Warning, AccessError,ValidationError, UserError
from datetime import datetime, date
import json


class PlanComponents(models.Model):
    _name = 'plan.components'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Plan'
    _rec_name = "reference"

    planning_date = fields.Date(string="Planning Date", required=True, tracking=True)
    component_lines_ids = fields.One2many('plan.components.line', 'reference_id')

class PlanComponentsLines(models.Model):
    _name = 'plan.components.line'


    product_id = fields.Many2one('product.product', string="Products")
    bom_id = fields.Many2one('mrp.bom', string="Bom")
    production_uom_id = fields.Many2one('uom.uom', string="Unit")
    actual_plan_qty = fields.Float(string="Actual Plan Qty")

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            bom = self.product_id.bom_ids and self.product_id.bom_ids[0] or False
            self.bom_id = bom