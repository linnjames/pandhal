from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)




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
        [('draft', "Draft"), ('confirmed', "Confirmed"), ('cancel', "Cancelled"), ('indent created', 'Indent Created')], default='draft',)
    sales_line_ids = fields.One2many('sales.indent.lines', 'pur_id', string='Sales Line')
    indent_type = fields.Selection([('bakery', 'Bakery'),
                                    ('store', 'Store'),
                                    ('customer order', 'Customer Order'),
                                    ], required=True)
    # sale_id = fields.Integer(string='Purchase Indent Number')
    # sale_id = fields.Char(string='Purchase Indent Number', readonly=True)
    no_id = fields.Many2one('indent.request', string="Purchase Indent Number", copy=False)
    company_id = fields.Many2one('res.company', string='company', readonly=True,
                                 default=lambda self: self.env.company.id)
    delivery_status = fields.Selection([('draft', 'Draft'),
                                       ('done', 'Done'),
                                       ('cancel', 'Cancelled'),
                                       ('waiting', "Waiting Another Operation"),
                                       ('assigned', "Ready"),
                                       ('confirmed', "Waiting"),
                                       ('no_transfer', "No Valid Transfer"),
                                       ], required=True, compute='_compute_sales_delivery_state')

    attachment = fields.Binary(string="Attachment")
    is_true = fields.Boolean(string='is_true')

    @api.depends('no_id')
    def _compute_sales_delivery_state(self):
        for record in self:
            x = self.env['stock.picking'].sudo().search([('sale_transfer_id', '=', record.reference)], limit=1).state
            if x:
                record.delivery_status = x
            else:
                record.delivery_status = 'no_transfer'


    @api.model
    def create(self, vals):
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('sales.indent') or _('New')
        res = super(SalesIndent, self).create(vals)
        return res


    def action_confirmed(self):
        for record in self:
            if not record.no_id:
                comp = self.env['res.company'].sudo().search([('partner_id', '=', record.vendor_id.id)])
                d = self.env['indent.request'].sudo().create({
                    'vendor_id': record.company_id.partner_id.id,
                    'indent_type': record.indent_type,
                    'reference_id': record.reference,
                    'expected_date': record.expected_date,
                    'company_id': comp.id,
                    'attachment': record.attachment,
                })
                record.no_id = d.id
                for vals in record.sales_line_ids:
                    d.write({
                        'purchase_line_ids': [(0, 0, {
                            'product_id': vals.product_id.id,
                            'qty': vals.qty,
                            'uom_id': vals.uom_id.id,
                            'message': vals.message,
                        })]
                    })
                    print(d, 'dddddddddddddddddddddddddddddddddd')

            current_company = self.env['res.company'].sudo().search([('id', '=', self.env.company.id)], limit=1)
            a = self.env['stock.picking'].sudo().create({
                'partner_id': record.vendor_id.id,
                'picking_type_id': current_company.sudo().operation_type_out.id,
                'location_id': current_company.sudo().operation_type_out.default_location_src_id.id,
                'location_dest_id': current_company.sudo().operation_type_out.default_location_dest_id.id,
                'company_id': current_company.id,
                'sale_transfer_id': record.id,
                'scheduled_date': False,
                'date_done': False,
            })
            for vals in record.sales_line_ids:
                a.write({
                    'move_ids_without_package': [(0, 0, {
                        'product_id': vals.product_id.id,
                        'product_uom_qty': vals.qty,
                        'name': vals.product_id.name,
                        'company_id': self.env.company.id,
                        'location_id': self.env.company.sudo().operation_type_out.default_location_src_id.id,
                        'location_dest_id': self.env.company.sudo().operation_type_out.default_location_dest_id.id,
                    })]
                })
                print(a, 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
            a.scheduled_date = record.expected_date
            a.date_done = record.expected_date
            print(a, "multi")

        records_to_confirm = self.filtered(lambda r: r.state == 'draft')
        records_to_confirm.write({'state': 'confirmed'})

    def action_cancel(self):
        for record in self:
            if record.state == 'draft':
                record.state = 'cancel'
            elif record.state == 'confirmed':
                raise ValidationError("Transfer In Progress")

    def action_open_transfer(self):
        return {
            'name': _('Transfer'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'tree,form',
            # 'domain': [('transfer_id', '=', self.no_id.id)],
            'domain': [('sale_transfer_id', '=', self.id)],
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
                                    ('indent', 'Indent'), ], required=True,
                                   string="Order Type")

    state = fields.Selection(selection_add=[('indent_created', 'Indent Created')])
    attachment = fields.Binary(string="Attachment")
    is_true = fields.Boolean(string='is_true')
    validity_date = fields.Date(string='Expected Date', date_format='%d/%m/%Y', required=True)

    @api.depends('company_id', 'indent_type')
    def _compute_l10n_in_journal_id(self):
        _logger.debug("Starting _compute_l10n_in_journal_id")
        super()._compute_l10n_in_journal_id()

        for order in self:
            _logger.debug(f"Processing order: {order.name}")
            if order.indent_type == 'indent':
                journal_domain = [
                    ('company_id', '=', order.company_id.id),
                    ('indent_type', '=', order.indent_type)
                ]
                _logger.debug(f"Journal domain: {journal_domain}")
                bakery_journal = self.env['account.journal'].sudo().search(journal_domain, limit=1)

                if bakery_journal:
                    order.l10n_in_journal_id = bakery_journal.id

        _logger.debug("Finished _compute_l10n_in_journal_id")

    def action_create_purchase_indent(self):
        if not self.order_line.filtered(lambda l: l.select_item):
            raise UserError("Please select at least one item.")

        # self.state = "indent_created"
        company = self.env['res.company'].sudo().browse(self.company_id.id)
        print(company)
        b = self.env['indent.request'].sudo().create({
            'vendor_id': company.parent_id.partner_id.id,
            'indent_type': self.indent_type,
            'expected_date': self.validity_date,
            'sale_purchase_id': self.id,
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
                })]
            })
        b.action_confirmed()

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


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    indent_type = fields.Selection([('customer order', 'Customer Order'),
                                    ('indent', 'Indent'), ],
                                   string="Order Type")


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    l10n_in_branch_journal_id = fields.Many2one('account.journal', string='Branch Journal')
    l10n_in_branch_purchase_journal_id = fields.Many2one('account.journal', string='Branch Purchase Journal')
