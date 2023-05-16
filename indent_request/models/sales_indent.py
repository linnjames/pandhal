from odoo import models, fields, api, _


class IndentRequest(models.Model):
    _name = 'sales.indent'

    # vendor_id = fields.Many2one('res.partner', string='Vendor')
    vendor_id = fields.Many2one('res.company', string='Partner')

    currency_id = fields.Many2one('res.currency', string='Currency')
    order_date = fields.Datetime(string='Order Deadline', default=fields.Date.today)
    expected_date = fields.Datetime(string='Expected Date')
    # purchase_line_ids = fields.One2many('purchase.indent.lines', 'pur_id', string='Purchase Lines')
    state = fields.Selection(
        [('draft', "Draft"), ('confirmed', "Confirmed"), ('cancel', "Cancelled")], default='draft',)
    sales_line_ids = fields.One2many('sales.indent.lines','pur_id', string='Sales Line')
    indent_type = fields.Selection([('bakery', 'Bakery'), ('store', 'Store')])
    # sale_id = fields.Char('ID')
    sale_id = fields.Many2one('indent.request', string='ID')
    company_id = fields.Many2one('res.company', string='company', readonly=True,
                                 default=lambda self: self.env.company.id)

    def action_confirmed(self):
        self.state = 'confirmed'

    def action_cancel(self):
        self.state = 'cancel'

    def action_open_transfer(self):
        return {
            'name': _('Transfer'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'tree,form',
            'domain': [('transfer_id', '=', self.sale_id.id)],
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

