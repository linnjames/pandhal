from odoo import api, fields, models, _


class AssetTransfer(models.TransientModel):
    _name = 'asset.transfer'

    name_id = fields.Many2one('res.partner', string='Name', default=lambda self: self.env.user.partner_id.id)
    product_id = fields.Many2one('product.product', string="Product")
    qty = fields.Float(string="Quantity")
    operation_type_id = fields.Many2one('stock.picking.type', string="Operation Types", required=True,
                                        default=lambda self: self.env['stock.picking.type'].search(
                                            [('sequence_code', '=', 'AT OUT')]).id)
    asset_line_ids = fields.One2many('asset.transfer.lines', 'asset_transfer_id', string='Asset')
    default_employee_id = fields.Many2one('hr.employee', string="ID")

    @api.model
    def default_get(self, fields_list):
        defaults = super(AssetTransfer, self).default_get(fields_list)
        defaults['default_employee_id'] = self.env.context.get('active_id')
        return defaults

    def wizard_action_transfer(self):
        employee = self.env['hr.employee'].browse(self.default_employee_id.id)
        assets = self.env['asset.transfer'].search([('default_employee_id', '=', employee.id)])
        a = self.env['stock.picking'].sudo().create({
            'partner_id': self.name_id.id,
            'picking_type_id': self.operation_type_id.id,
            'location_id': self.operation_type_id.default_location_src_id.id,
            'location_dest_id': self.operation_type_id.default_location_dest_id.id,
            'asset_wizard_id': self.default_employee_id.id,
        })
        for vals in self.asset_line_ids:
            a.write({
                'move_ids_without_package': [(0, 0, {
                    'product_id': vals.product_id.id,
                    'product_uom_qty': vals.qty,
                    # 'description_picking': vals.product_id.name,
                    'name': vals.product_id.name,
                    'location_id': self.operation_type_id.default_location_src_id.id,
                    'location_dest_id': self.operation_type_id.default_location_dest_id.id,
                })]
            })
            a.button_validate


class AssetTransferLines(models.TransientModel):
    _name = 'asset.transfer.lines'

    product_id = fields.Many2one('product.product', string='Product')
    qty = fields.Float(string='Quantity')
    asset_transfer_id = fields.Many2one('asset.transfer', string='Asset Transfer')
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure')
