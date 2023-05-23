from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SalesIndent(models.Model):
    _name = 'sales.indent'
    _rec_name = 'reference'


    # vendor_id = fields.Many2one('res.partner', string='Vendor')
    # vendor_id = fields.Many2one('res.partner', string='Partner')
    vendor_id = fields.Many2one('res.company', string='Partner')
    reference = fields.Char(string='Order Reference', required=True, copy=False, readonly=True,
                            default=lambda self: _('New'))

    currency_id = fields.Many2one('res.currency', string='Currency')
    order_date = fields.Datetime(string='Order Deadline', default=fields.Date.today)
    expected_date = fields.Datetime(string='Expected Date')
    # purchase_line_ids = fields.One2many('purchase.indent.lines', 'pur_id', string='Purchase Lines')
    state = fields.Selection(
        [('draft', "Draft"), ('confirmed', "Confirmed"), ('cancel', "Cancelled")], default='draft',)
    sales_line_ids = fields.One2many('sales.indent.lines','pur_id', string='Sales Line')
    indent_type = fields.Selection([('bakery', 'Bakery'),
                                    ('store', 'Store')], required=True)
    # sale_id = fields.Char('ID')
    # sale_id = fields.Many2one('indent.request', string='ID')
    sale_id = fields.Integer(string='ID')
    company_id = fields.Many2one('res.company', string='company', readonly=True,
                                 default=lambda self: self.env.company.id)
    delivery_status = fields.Selection([('draft', 'Draft'),
                                              ('done', 'Done'),
                                              ('cancel', 'Cancelled'),
                                              ('waiting', "Waiting Another Operation"),
                                              ('assigned', "Ready"),
                                              ('confirmed', "Waiting"),
                                              ], required=True, compute='_compute_delivery_state_sales')

    @api.depends('sale_id')
    def _compute_delivery_state_sales(self):
        for record in self:
            x = self.env['stock.picking'].sudo().search([('transfer_id', '=', record.sale_id)], limit=1).state
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

    # def action_cancel(self):
    #     self.state = 'cancel'

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
            # 'domain': [('transfer_id', '=', self.sale_id.id)],
            'domain': [('transfer_id', '=', self.sale_id)],
        }



class SalesIndentLines(models.Model):
    _name = 'sales.indent.lines'

    pur_id = fields.Many2one('sales.indent', string='Purchase Indent')
    product_id = fields.Many2one('product.product', string='Product')
    qty = fields.Float(string='Quantity')
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure')
    # transfer_id = fields.Many2one('indent.request', string='ID')
    item_select = fields.Boolean(string='Select Item')


    @api.onchange('product_id')
    def onchange_course_name(self):
        if self.product_id:
            if self.product_id.uom_id:
                self.uom_id = self.product_id.uom_id

    # order_lines = [product_id]  # a list of order lines, each containing product information
    #
    # # create a set of unique product IDs
    # products = set(line['product'] for line in order_lines)
    #
    # # check for duplicates
    # for line in order_lines:
    #     if line['product'] in products:
    #         raise ValueError('Duplicate product found. Please remove one of the duplicates.')
    #     else:
    #         products.add(line['product'])

