from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class IndentRequest(models.Model):
    _name = 'indent.request'
    _rec_name = 'reference'

    reference = fields.Char(string='Order Reference', required=True, copy=False, readonly=True,
                            default=lambda self: _('New'))
    vendor_id = fields.Many2one('res.partner', string='Partner')
    # vendor_id = fields.Many2one('res.company', string='Partner')
    # vendor_id = fields.Many2one('res.partner', string='Company', domain="[('company_type', '=', 'company_id')]")

    uom_id = fields.Many2one('uom.uom', string='Unit of Measure')
    indent_type = fields.Selection([('bakery', 'Bakery'),
                                    ('store', 'Store'),
                                    ('customer order', 'Customer Order')], required=True)
    currency_id = fields.Many2one('res.currency', string='Currency')
    # order_date = fields.Datetime(string='Order Deadline', default=fields.Date.today)
    expected_date = fields.Datetime(string='Expected Date')
    purchase_line_ids = fields.One2many('purchase.indent.lines', 'pur_id', string='Purchase Lines')
    state = fields.Selection(
        [('draft', "Draft"), ('confirmed', "Confirmed"), ('cancel', "Cancelled")],
        default='draft')
    company_id = fields.Many2one('res.company', string='company', readonly=True,
                                 default=lambda self: self.env.company.id)

    delivery_status = fields.Selection([('draft', 'Draft'),
                                        ('done', 'Done'),
                                        ('cancel', 'Cancelled'),
                                        ('waiting', "Waiting Another Operation"),
                                        ('assigned', "Ready"),
                                        ('confirmed', "Waiting"),
                                        ], required=True, compute='_compute_delivery_state')
    sale_purchase_id = fields.Many2one('sale.order', string='ID')
    sale_indent_purchase_id = fields.Many2one('sales.indent', string='sale indent purchase id')

    @api.depends('reference')
    def _compute_delivery_state(self):
        for record in self:
            x = self.env['stock.picking'].sudo().search([('transfer_id', '=', record.reference)], limit=1).state
            record.delivery_status = x

    @api.model
    def create(self, vals):
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('indent.sequence') or _('New')
        res = super(IndentRequest, self).create(vals)
        return res

    def action_open_purchase_transfer(self):
        return {
            'name': _('Transfer'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'tree,form',
            'domain': [('transfer_id', '=', self.id)],
        }

    def action_cancel(self):
        print('yyyyyyyyyyyyyyyyyyyyyyyyyyy')
        self.state = 'cancel'
        a = self.env['stock.picking'].search([('transfer_id', '=', self.reference)], limit=1)
        print(a)
        if a.state == 'draft':
            a.state = 'cancel'
        else:
            raise ValidationError("Transfer In Progress")

    def action_confirmed(self):
        partner = self.env['res.company'].sudo().search([('partner_id', '=', self.vendor_id.id)])
        print(partner)
        if partner.partner_id.id == self.env.company.partner_id.id:
            print("qqqqqqqqqqqqqqqqqqqqqq")
            raise ValidationError('Partner cannot be the same as company.')

        if self.expected_date == False:
            raise ValidationError('Please provide required date.')

        if self.purchase_line_ids.qty == False:
            raise ValidationError('Please provide required quantity.')

        operation = partner.operation_type_out
        print('wwwwwwwwwwwwwwww')
        op = partner
        print('eeeeeeee')
        self.state = 'confirmed'
        print(operation.name)
        print(operation.sudo().company_id.name)
        a = self.env['stock.picking'].sudo().create({
            'partner_id': partner.partner_id.id,
            'picking_type_id': operation.id,
            'location_id': op.sudo().operation_type_out.default_location_src_id.id,
            'location_dest_id': op.sudo().operation_type_out.default_location_dest_id.id,
            'company_id': self.vendor_id.id,
            'transfer_id': self.id,
            # 'origin': self.id,
        })
        for vals in self.purchase_line_ids:
            a.write({
                'move_ids_without_package': [(0, 0, {
                    'product_id': vals.product_id.id,
                    'product_uom_qty': vals.qty,
                    # 'description_picking': vals.product_id.id,
                    'name': vals.product_id.name,
                    'company_id': self.vendor_id.id,
                    'location_id': op.sudo().operation_type_out.default_location_src_id.id,
                    'location_dest_id': op.sudo().operation_type_out.default_location_dest_id.id,
                })]
            })

        b = self.env['stock.picking'].sudo().create({
            # 'partner_id': self.env.company.partner_id.id,
            'partner_id': self.vendor_id.id,
            'picking_type_id': self.env.company.sudo().operation_type_in.id,
            'location_id': self.env.company.sudo().operation_type_in.default_location_src_id.id,
            'location_dest_id': self.env.company.sudo().operation_type_in.default_location_dest_id.id,
            'company_id': self.env.company.id,
            'transfer_id': self.id,
        })
        for vals in self.purchase_line_ids:
            b.write({
                'move_ids_without_package': [(0, 0, {
                    'product_id': vals.product_id.id,
                    'product_uom_qty': vals.qty,
                    # 'description_picking': vals.product_id.id,
                    'name': vals.product_id.name,
                    'company_id': self.env.company.id,
                    'location_id': self.env.company.sudo().operation_type_in.default_location_src_id.id,
                    'location_dest_id': self.env.company.sudo().operation_type_in.default_location_dest_id.id,
                })]
            })


        c = self.env['sales.indent'].sudo().create({
            # 'vendor_id': self.vendor_id.id,
            'vendor_id': self.company_id.id,
            'sale_id': self.id,
            'indent_type': self.indent_type,
            # 'order_date': self.order_date,
            'expected_date': self.expected_date,
            'company_id': self.vendor_id.id,
        })
        for vals in self.purchase_line_ids:
            tax = self.env['account.tax'].sudo().search(
                [('name', '=', vals.product_id.taxes_id.name), ('company_id', '=', self.vendor_id.id)])
            print(tax)
            c.write({
                'sales_line_ids': [(0, 0, {
                    # 'product_template_id': vals.product_id.id,
                    'product_id': vals.product_id.id,
                    'qty': vals.qty,
                    'uom_id': vals.uom_id.id,

                })]
            })


    # def action_confirmed(self):
    #     for vals in self:
    #         print('qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq')
    #         if vals.vendor_id.partner_id == self.env.company.partner_id:
    #         # if vals.vendor_id.name == self.env.company.partner_id:
    #             raise ValidationError('Partner cannot be the same as company.')
    #
    #         # if vals.vendor_id.name == self.env.company.partner_id:
    #         #     raise ValidationError('Partner cannot be the same as company.')
    #
    #         if vals.expected_date == False:
    #             raise ValidationError('Please provide required date.')
    #
    #         if any(line.qty == False for line in vals.purchase_line_ids):
    #             raise ValidationError('Please provide required quantity.')
    #         print("////////////////////////")
    #         operation = self.sudo().vendor_id.operation_type_out
    #         op = self.vendor_id
    #         self.state = 'confirmed'
    #         print(operation.name)
    #         print(operation.sudo().company_id.name)
    #         a = self.env['stock.picking'].sudo().create({
    #             'partner_id': self.vendor_id.partner_id.id,
    #             'picking_type_id': operation.id,
    #             'location_id': op.sudo().operation_type_out.default_location_src_id.id,
    #             'location_dest_id': op.sudo().operation_type_out.default_location_dest_id.id,
    #             'company_id': self.vendor_id.id,
    #             'transfer_id': self.id,
    #             # 'origin': self.id,
    #         })
    #         for vals in self.purchase_line_ids:
    #             a.write({
    #                 'move_ids_without_package': [(0, 0, {
    #                     'product_id': vals.product_id.id,
    #                     'product_uom_qty': vals.qty,
    #                     # 'description_picking': vals.product_id.id,
    #                     'name': vals.product_id.name,
    #                     'company_id': self.vendor_id.id,
    #                     'location_id': op.sudo().operation_type_out.default_location_src_id.id,
    #                     'location_dest_id': op.sudo().operation_type_out.default_location_dest_id.id,
    #                 })]
    #             })
    #
    #         b = self.env['stock.picking'].sudo().create({
    #             # 'partner_id': self.env.company.partner_id.id,
    #             'partner_id': self.vendor_id.id,
    #             'picking_type_id': self.env.company.sudo().operation_type_in.id,
    #             'location_id': self.env.company.sudo().operation_type_in.default_location_src_id.id,
    #             'location_dest_id': self.env.company.sudo().operation_type_in.default_location_dest_id.id,
    #             'company_id': self.env.company.id,
    #             'transfer_id': self.id,
    #         })
    #         for vals in self.purchase_line_ids:
    #             b.write({
    #                 'move_ids_without_package': [(0, 0, {
    #                     'product_id': vals.product_id.id,
    #                     'product_uom_qty': vals.qty,
    #                     # 'description_picking': vals.product_id.id,
    #                     'name': vals.product_id.name,
    #                     'company_id': self.env.company.id,
    #                     'location_id': self.env.company.sudo().operation_type_in.default_location_src_id.id,
    #                     'location_dest_id': self.env.company.sudo().operation_type_in.default_location_dest_id.id,
    #                 })]
    #             })
    #
    #
    #         # company_id = self.env.company
    #         c = self.env['sales.indent'].sudo().create({
    #             # 'vendor_id': self.vendor_id.id,
    #             'vendor_id': self.company_id.id,
    #             'sale_id': self.id,
    #             'indent_type': self.indent_type,
    #             # 'order_date': self.order_date,
    #             'expected_date': self.expected_date,
    #             'company_id': self.vendor_id.id,
    #         })
    #         for vals in self.purchase_line_ids:
    #             tax = self.env['account.tax'].sudo().search(
    #                 [('name', '=', vals.product_id.taxes_id.name), ('company_id', '=', self.vendor_id.id)])
    #             print(tax)
    #             c.write({
    #                 'sales_line_ids': [(0, 0, {
    #                     # 'product_template_id': vals.product_id.id,
    #                     'product_id': vals.product_id.id,
    #                     'qty': vals.qty,
    #                     'uom_id': vals.uom_id.id,
    #
    #                 })]
    #             })

    # def action_create_purchase(self):
    #     if not self.purchase_line_ids.filtered(lambda l: l.item_select):
    #         raise UserError("Please select at least one item to create purchase order.")
    #     self.state = 'purchase'
    #     b = self.env['purchase.order'].sudo().create({
    #         'partner_id': self.vendor_id.partner_id.id,
    #         'company_id': self.vendor_id.id,
    #
    #     })
    #     for vals in self.purchase_line_ids:
    #         b.write({
    #             'order_line': [(0, 0, {
    #                 'product_id': vals.product_id.id,
    #                 # 'product_uom_qty': vals.qty,
    #                 'product_qty': vals.qty,
    #                 'price_unit': vals.product_id.standard_price,
    #                 'taxes_id': vals.product_id.taxes_id,
    #             })]
    #         })


class PurchaseIndentLines(models.Model):
    _name = 'purchase.indent.lines'

    pur_id = fields.Many2one('indent.request', string='Purchase Indent')
    product_id = fields.Many2one('product.product', string='Product')
    qty = fields.Float(string='Quantity')
    transfer_id = fields.Many2one('indent.request', string='ID')
    item_select = fields.Boolean(string='Select Item')
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure')
    # image = fields.Image(
    #     string="Image", max_width=64, max_height=64)
    img = fields.Binary(string="Image", readonly=True)
    message = fields.Char(string="Message")


    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id.image_1920:
            self.img = self.product_id.image_1920


    @api.onchange('product_id')
    def onchange_course_name(self):
        if self.product_id:
            if self.product_id.uom_id:
                self.uom_id = self.product_id.uom_id


class ResCompany(models.Model):
    _inherit = 'res.company'

    operation_type_in = fields.Many2one('stock.picking.type', string='Indent Operation Type IN')
    operation_type_out = fields.Many2one('stock.picking.type', string='Indent Operation Type OUT')


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    transfer_id = fields.Many2one('indent.request', string='ID')


class PurchaseState(models.Model):
    _inherit = 'purchase.order'

    state = fields.Selection(selection_add=[('approve', 'Approved'), ("purchase",)])

    def button_purchase_approval(self):
        self.state = 'approve'

    def button_confirm(self):
        res = super(PurchaseState, self).button_confirm()
        for order in self:
            if order.state in ['approve']:

                order.order_line._validate_analytic_distribution()
                order._add_supplier_to_product()
                # Deal with double validation process
                if order._approval_allowed():
                    order.button_approve()
                else:
                    order.write({'state': 'to approve'})
                if order.partner_id not in order.message_partner_ids:
                    order.message_subscribe([order.partner_id.id])
            order.state = 'purchase'
        return res
