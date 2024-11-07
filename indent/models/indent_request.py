from odoo import models, fields, api, _
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, format_amount, format_date, formatLang, get_lang, groupby


from odoo.exceptions import ValidationError, UserError


class IndentRequest(models.Model):
    _name = 'indent.request'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = 'reference'
    _order = 'create_date desc'

    reference = fields.Char(string='Order Reference', required=True, copy=False, readonly=True,
                            default=lambda self: _('New'))
    vendor_id = fields.Many2one('res.partner', string='Partner')

    uom_id = fields.Many2one('uom.uom', string='Unit of Measure')
    indent_type = fields.Selection([('bakery', 'Bakery'),
                                    ('store', 'Store'),
                                    ('customer order', 'Customer Order')], required=True)
    currency_id = fields.Many2one('res.currency', string='Currency')
    expected_date = fields.Datetime(string='Expected Date', date_format='%d/%m/%Y', required=True)
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
                                        ('no_transfer', "No Valid Transfer"),
                                        ], required=True, compute='_compute_delivery_state')

    sale_purchase_id = fields.Many2one('sale.order', string='ID')
    sale_indent_purchase_id = fields.Many2one('sales.indent', string='sale indent purchase id')
    attachment = fields.Binary(string="Attachment")
    reference_id = fields.Char(string='Sale Indent Number', copy=False)

    @api.depends('reference')
    def _compute_delivery_state(self):
        for record in self:
            x = self.env['stock.picking'].sudo().search([('transfer_id', '=', record.reference)], limit=1).state
            if x:
                record.delivery_status = x
            else:
                record.delivery_status = 'no_transfer'

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
        for record in self:
            if record.state == 'draft':
                record.state = 'cancel'
            elif record.state == 'confirmed':
                raise ValidationError("Transfer In Progress")



    def action_confirmed(self):
        records_to_confirm = self.filtered(lambda r: r.state == 'draft')

        for record in records_to_confirm:
            if not record.reference_id:
                if not record.expected_date:
                    raise ValidationError('Please provide required date.')

                if not record.reference_id:
                    partner = self.env['res.company'].sudo().search([('partner_id', '=', record.vendor_id.id)])
                    print(partner)
                    if partner.partner_id.id == self.env.company.partner_id.id:
                        print("qqqqqqqqqqqqqqqqqqqqqq")
                        raise ValidationError('Partner cannot be the same as company.')

                    comp = self.env['res.company'].sudo().search([('partner_id', '=', record.vendor_id.id)])
                    c = self.env['sales.indent'].sudo().create({
                        'vendor_id': record.company_id.partner_id.id,
                        'no_id': record.id,
                        'indent_type': record.indent_type,
                        'expected_date': record.expected_date,
                        'company_id': comp.id,
                        'attachment': record.attachment,
                    })
                    record.reference_id = c.reference
                    for vals in record.purchase_line_ids:
                        c.write({
                            'sales_line_ids': [(0, 0, {
                                'product_id': vals.product_id.id,
                                'qty': vals.qty,
                                'uom_id': vals.uom_id.id,
                                'message': vals.message,
                            })]
                        })
                        print(c, 'ccccccccccccccccccccccccccccccccccc')

            b = self.env['stock.picking'].sudo().create({
                'partner_id': record.vendor_id.id,
                'picking_type_id': self.env.company.sudo().operation_type_in.id,
                'location_id': self.env.company.sudo().operation_type_in.default_location_src_id.id,
                'location_dest_id': self.env.company.sudo().operation_type_in.default_location_dest_id.id,
                'company_id': self.env.company.id,
                'transfer_id': record.id,
                'scheduled_date': False,
                'date_done': False,
            })
            for vals in record.purchase_line_ids:
                b.write({
                    'move_ids_without_package': [(0, 0, {
                        'product_id': vals.product_id.id,
                        'product_uom_qty': vals.qty,
                        'name': vals.product_id.name,
                        'company_id': self.env.company.id,
                        'location_id': self.env.company.sudo().operation_type_in.default_location_src_id.id,
                        'location_dest_id': self.env.company.sudo().operation_type_in.default_location_dest_id.id,
                    })]
                })
                print(b, 'bbbbbbbbbbbbbbbbbbbbbbbbbbbb')

            b.scheduled_date = record.expected_date
            b.date_done = record.expected_date
            print(b, "multi")

        records_to_confirm.write({'state': 'confirmed'})


class PurchaseIndentLines(models.Model):
    _name = 'purchase.indent.lines'

    pur_id = fields.Many2one('indent.request', string='Purchase Indent')
    product_id = fields.Many2one('product.product', string='Product')
    qty = fields.Float(string='Quantity')
    transfer_id = fields.Many2one('indent.request', string='ID')
    item_select = fields.Boolean(string='Select Item')
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure')
    message = fields.Char(string="Message")

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

    transfer_id = fields.Many2one('indent.request', string='Purchase Transfer ID')
    sale_transfer_id = fields.Many2one('sales.indent', string='Sales Transfer ID')
    location_id = fields.Many2one(states={'assigned': [('readonly', True)]})
    location_dest_id = fields.Many2one(states={'assigned': [('readonly', True)]})


class PurchaseState(models.Model):
    _inherit = 'purchase.order'

    state = fields.Selection(selection_add=[('approve', 'Approved'), ("purchase",)])
    indent_type = fields.Selection([('customer order', 'Customer Order'),
                                    ('indent', 'Indent'), ], required=True, default='indent',
                                   string="Order Type")

    def button_purchase_approval(self):
        pass

    @api.depends('order_line.date_planned')
    def _compute_date_planned(self):
        """ date_planned = the earliest date_planned across all order lines. """
        for order in self:
            dates_list = order.order_line.filtered(lambda x: not x.display_type and x.date_planned).mapped(
                'date_planned')
            if not order.date_planned:
                order.date_planned = False


class PurchaseQuantity(models.Model):
    _inherit = 'purchase.order.line'

    available_qty = fields.Float(string='Quantity On Hand')

    @api.onchange('product_id')
    def _onchange_product_id_warning(self):
        for line in self:
            if line.product_id:
                line.available_qty = line.product_id.qty_available
            else:
                line.available_qty = 0.0


class SaleOrderInherit(models.Model):
    _inherit = "sale.order"

    @api.depends('company_id', 'warehouse_id','indent_type')
    def _compute_l10n_in_journal_id(self):
        super()._compute_l10n_in_journal_id()
        for order in self:
            if order.indent_type == 'bakery':
                if order.warehouse_id.l10n_in_branch_journal_id:
                    order.l10n_in_journal_id = order.warehouse_id.l10n_in_branch_journal_id.id

