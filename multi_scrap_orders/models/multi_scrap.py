from odoo import models, fields, api, _
from odoo.tools import float_compare
from odoo.exceptions import AccessError
from datetime import datetime, date

from odoo.exceptions import UserError


class MultiScrap(models.Model):
    _name = 'multi.scrap'
    _rec_name = "name_seq"

    def _get_default_scrap_location_id(self):
        company_id = self.env.context.get('default_company_id') or self.env.company.id
        return self.env['stock.location'].search(
            [('scrap_location', '=', True), ('company_id', 'in', [company_id, False])], limit=1).id

    def _get_default_location_id(self):
        company_id = self.env.context.get('default_company_id') or self.env.company.id
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', company_id)], limit=1)
        if warehouse:
            return warehouse.lot_stock_id.id
        return None

    location_id = fields.Many2one(
        'stock.location', 'Source Location',
        domain="[('usage', '=', 'internal'), ('company_id', 'in', [company_id, False])]",
        required=True, states={'done': [('readonly', True)]}, default=_get_default_location_id , check_company=True)
    expected_date = fields.Date(string='Expected Date',required=True,default=fields.Date.context_today)
    source_doc = fields.Char(string='Source Document')
    task_parent_id = fields.Many2one('multi.scrap', string="Parent Id")
    operation_ids = fields.One2many('multi.scrap.line', 'multi_scarp_id', string="Operation")
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')],
                             string="Status", default='draft')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=True,
                                 states={'done': [('readonly', True)]})
    name_seq = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                           default=lambda self: _('New'))
    scrap_location_id = fields.Many2one(
        'stock.location', 'Scrap Location', default=_get_default_scrap_location_id,
        domain="[('scrap_location', '=', True), ('company_id', 'in', [company_id, False])]", required=True,
        states={'done': [('readonly', True)]}, check_company=True)
    reason_one = fields.Many2one('inventory.reason', string='Reason')

    @api.model
    def default_get(self, fields):
        res = super(MultiScrap, self).default_get(fields)
        x = self.env.company.id
        res.update({
            'company_id': x,
        })
        return res

    @api.model
    def create(self, vals):
        if vals.get('name_seq', _('New')) == _('New'):
            vals['name_seq'] = self.env['ir.sequence'].next_by_code('multi.scrap.sequence') or _('New')
        result = super(MultiScrap, self).create(vals)
        return result

    def action_validate(self):
        x = date.today()
        if self.expected_date < x:
            raise UserError(_('Check Date.'))
        for i in self.operation_ids:
            if i.quantity > i.product_id.qty_available:
                raise AccessError("Units of storage arent available")
            elif i.quantity <= 0:
                raise AccessError("Value should be there")
        self.state = 'done'
        for i in self.operation_ids:
            self.env['stock.move'].create({
                'name': self.name_seq,
                # 'origin': self.origin or self.picking_id.name or self.name,
                'company_id': self.company_id.id,
                'product_id': i.product_id.id,
                'product_uom': i.product_uom_id.id,
                'state': 'done',
                'product_uom_qty': i.quantity,
                'location_id': self.location_id.id,
                'scrapped': True,
                'location_dest_id': self.scrap_location_id.id,

                'move_line_ids': [(0, 0, {'product_id': i.product_id.id,
                                          'product_uom_id': i.product_uom_id.id,
                                          'qty_done': i.quantity,
                                          'location_id': self.location_id.id,
                                          'location_dest_id': self.scrap_location_id.id,
                                          'reference': self.name_seq,
                                          # 'reference': self.name_seq,
                                          'lot_id': i.lot_id.id,
                                          'value_id': self.id,
                                          })],
            })
            qty = i.product_id.qty_available - i.quantity

    def action_scrap_product_move(self):
        return {
            'name': _('multi.scrap'),
            'view_mode': 'tree,form',
            'res_model': 'stock.move.line',
            'type': 'ir.actions.act_window',
            'domain': [('value_id', '=', self.id)],
        }


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    value_id = fields.Many2one('multi.scrap')


class MultiScrapLine(models.Model):
    _name = 'multi.scrap.line'

    product_id = fields.Many2one('product.product', string='Product', required=True)

    multi_scarp_id = fields.Many2one('multi.scrap')
    quantity = fields.Float(string='Quantity', required=True)
    product_uom_id = fields.Many2one(
        'uom.uom', 'Unit of Measure',
        required=True, state={'done': [('readonly', True)]})
    lot_id = fields.Many2one(
        'stock.production.lot', 'Lot/Serial')
    stock_loc = fields.Many2one(string='Location', related='multi_scarp_id.scrap_location_id', store=True)
    reason = fields.Many2one('inventory.reason', string='Reason')
    received_goods = fields.Float(string='Received Product')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id
            self.reason = self.multi_scarp_id.reason_one
