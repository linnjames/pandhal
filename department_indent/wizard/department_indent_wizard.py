from odoo import models, fields, api, _


class DepartmentRequest(models.TransientModel):
    _name = 'department.indent.wizard'


    name_id = fields.Many2one('res.partner', string='Name', default=lambda self: self.env.user.partner_id.id)

    operation_type_id = fields.Many2one('stock.picking.type', string="Operation Types", required=True,
                                        default=lambda self: self.env['stock.picking.type'].search(
                                            [('sequence_code', '=', 'DT IN')]).id)

    dept_line_ids = fields.One2many('department.indent.lines', 'dept_transfer_id', string='Dept')

    def action_transfer(self):
        x = self.env['stock.picking'].sudo().create({
            'partner_id': self.name_id.id,
            'picking_type_id': self.operation_type_id.id,
            'location_id': self.operation_type_id.default_location_src_id.id,
            'location_dest_id': self.operation_type_id.default_location_dest_id.id,
            # 'asset_wizard_id': self.default_employee_id.id,
        })
        print(x, "pppppppppppppppppppppppppp")
        for vals in self.dept_line_ids:
            x.write({
                'move_ids_without_package': [(0, 0, {
                    'product_id': vals.product_id.id,
                    'product_uom_qty': vals.qty,
                    # 'description_picking': vals.product_id.name,
                    'name': vals.product_id.name,
                    'location_id': self.operation_type_id.default_location_src_id.id,
                    'location_dest_id': self.operation_type_id.default_location_dest_id.id,
                })]
            })

class DepartmentIndentLines(models.TransientModel):
    _name = 'department.indent.lines'

    product_id = fields.Many2one('product.product', string='Product')
    qty = fields.Float(string='Quantity')
    dept_transfer_id = fields.Many2one('department.indent.wizard', string='Dept Transfer')
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure')






