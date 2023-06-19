from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class SalesIndent(models.Model):
    _name = 'sales.indent'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _rec_name = 'reference'
    _order = 'create_date desc'



    vendor_id = fields.Many2one('res.partner', string='Partner')
    reference = fields.Char(string='Order Reference', required=True, copy=False, readonly=True,
                            default=lambda self: _('New'))

    currency_id = fields.Many2one('res.currency', string='Currency')
    order_date = fields.Datetime(string='Order Deadline', default=fields.Date.today)
    expected_date = fields.Datetime(string='Expected Date', required=True)
    state = fields.Selection(
        [('draft', "Draft"), ('confirmed', "Confirmed"), ('cancel', "Cancelled")], default='draft',)
    sales_line_ids = fields.One2many('sales.indent.lines','pur_id', string='Sales Line')
    indent_type = fields.Selection([('bakery', 'Bakery'),
                                    ('store', 'Store'),
                                    ('customer order', 'Customer Order')], required=True)
    # sale_id = fields.Integer(string='Purchase Indent Number')
    # sale_id = fields.Char(string='Purchase Indent Number', readonly=True)
    no_id = fields.Many2one('indent.request', string="Purchase Indent Number")
    company_id = fields.Many2one('res.company', string='company', readonly=True,
                                 default=lambda self: self.env.company.id)
    delivery_status = fields.Selection([('draft', 'Draft'),
                                              ('done', 'Done'),
                                              ('cancel', 'Cancelled'),
                                              ('waiting', "Waiting Another Operation"),
                                              ('assigned', "Ready"),
                                              ('confirmed', "Waiting"),
                                              ], required=True, compute='_compute_delivery_state')

    attachment = fields.Binary(string="Attachment")
    is_true = fields.Boolean(string='is_true')


    @api.depends('no_id')
    def _compute_delivery_state(self):
        print('qqqqqqqqqqqqqqqqqqqqqqq')
        for record in self:
            print('wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww')
            x = self.env['stock.picking'].sudo().search([('transfer_id', '=', record.no_id.id)], limit=1).state
            print(x)
            record.delivery_status = x


    @api.model
    def create(self, vals):
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('sales.indent') or _('New')
        res = super(SalesIndent, self).create(vals)
        return res



    def action_confirmed(self):
        self.state = 'confirmed'
        # comp = self.env['res.company'].sudo().search([('partner_id', '=', self.vendor_id.id)])
        # d = self.env['indent.request'].sudo().create({
        #     'vendor_id': self.company_id.partner_id.id,
        #     # 'sale_id': self.reference,
        #     'indent_type': self.indent_type,
        #     'reference_id': self.reference,
        #     'expected_date': self.expected_date,
        #     'company_id': comp.id,
        #     'attachment': self.attachment,
        # })


    def action_cancel(self):
        print('wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww')
        self.state = 'cancel'
        a = self.env['stock.picking'].search([('transfer_id', '=', self.sale_id)], limit=1)
        print(a)
        if a.state == 'draft':
            a.state = 'cancel'
        else:
            raise ValidationError("Transfer In Progress")

    def action_open_transfer(self):
        return {
            'name': _('Transfer'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'tree,form',
            'domain': [('transfer_id', '=', self.no_id.id)],
        }



class SalesIndentLines(models.Model):
    _name = 'sales.indent.lines'

    pur_id = fields.Many2one('sales.indent', string='Purchase Indent')
    product_id = fields.Many2one('product.product', string='Product')
    qty = fields.Float(string='Quantity')
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure')
    # transfer_id = fields.Many2one('indent.request', string='ID')
    item_select = fields.Boolean(string='Select Item')
    message = fields.Char(string="Message")


    @api.onchange('product_id')
    def onchange_course_name(self):
        if self.product_id:
            if self.product_id.uom_id:
                self.uom_id = self.product_id.uom_id


class SalesOrder(models.Model):
    _inherit = 'sale.order'

    indent_type = fields.Selection([('customer order', 'Customer Order'),
                                    ('bakery', 'Bakery'),
                                    ('store', 'Store')], required=True, default='customer order')

    state = fields.Selection(selection_add=[('indent_created', 'Indent Created')])
    attachment = fields.Binary(string="Attachment")
    is_true = fields.Boolean(string='is_true')

    def action_create_purchase_indent(self):
        if not self.order_line.filtered(lambda l: l.select_item):
            raise UserError("Please select at least one item.")

        self.state = "indent_created"
        company = self.env['res.company'].sudo().browse(self.company_id.id)
        print(company)
        b = self.env['indent.request'].sudo().create({
            'vendor_id': company.parent_id.partner_id.id,
            # 'vendor_id': company.id,
            'indent_type': self.indent_type,
            # 'expected_date': self.date_order,
            'expected_date': self.validity_date,
            'sale_purchase_id': self.id,
            # 'picking_type_id': self.env.company.sudo().operation_type_in.id,
            # 'location_id': self.env.company.sudo().operation_type_in.default_location_src_id.id,
            # 'location_dest_id': self.env.company.sudo().operation_type_in.default_location_dest_id.id,
            'company_id': self.env.company.id,
            'attachment': self.attachment,

        })
        for vals in self.order_line.filtered(lambda l: l.select_item):
            b.write({
                'purchase_line_ids': [(0, 0, {
                    'product_id': vals.product_id.id,
                    'qty': vals.product_uom_qty,
                    'uom_id': vals.product_uom.id,
                    'message': vals.message,
                    # 'description_picking': vals.product_id.id,
                    # 'name': vals.product_id.name,
                    # 'company_id': self.env.company.id,
                    # 'location_id': self.env.company.sudo().operation_type_in.default_location_src_id.id,
                    # 'location_dest_id': self.env.company.sudo().operation_type_in.default_location_dest_id.id,
                })]
            })
            # b.action_confirmed()

    def action_view_purchase_indent(self):
        return {
            'name': _('Indent'),
            'type': 'ir.actions.act_window',
            'res_model': 'indent.request',
            'view_mode': 'tree,form',
            'domain': [('sale_purchase_id', '=', self.id)],
        }


class SalesOrderLine(models.Model):
    _inherit = 'sale.order.line'

    message = fields.Char(string='Message')
    select_item = fields.Boolean(string='Select Items', default=True)
