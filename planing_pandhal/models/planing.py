from odoo import api, fields, models, _
from odoo.exceptions import Warning, AccessError,ValidationError, UserError
from datetime import datetime, date
import json


class PlanPlaning(models.Model):
    _name = 'plan.planing'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Plan'
    _rec_name = "reference"

    planning_date = fields.Date(string="Planning Date", required=True, tracking=True)
    reference = fields.Char(string='Order Reference', required=True, copy=False, readonly=True,
                            default=lambda self: _('New'))
    reason = fields.Text(String="Reason", tracking=True)
    item_category_id = fields.Many2one('product.category', string="Item Category")
    production_lines_ids = fields.One2many('production.plan.lines', 'ref_id')
    state = fields.Selection(
        [('draft', 'Draft'), ('approval', 'Waiting For Approval'), ('approve', 'Approved'), ('reject', 'Rejected'),
         ('done', 'Done')],
        default='draft', string="Status", tracking=True)
    company_id = fields.Many2one('res.company', string='company', readonly=True,
                                 default=lambda self: self.env.company.id)
    is_confirm = fields.Boolean(string='Is confirm')
    tick = fields.Boolean(string="Consider Closing Stock")
    user_id = fields.Many2one('res.users', string='User', readonly=True,
                              default=lambda self: self.env.user.id, tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('production.planning') or _('New')
        res = super(PlanPlaning, self).create(vals)
        return res

    def action_line_value(self):
        # and so.is_true = false
        # and si.is_true = false
        self.production_lines_ids = False
        cdtn = '''where so.state = 'sale' and so.planing_id is null  and so.validity_date BETWEEN '%s' AND '%s'
                ''' % (
            self.planning_date.strftime("%Y-%m-%d 00:00:00"), self.planning_date.strftime("%Y-%m-%d 23:59:59"))
        if self.item_category_id:
            cdtn += ''' and pt.categ_id = %s 
                                        ''' % (self.item_category_id.id)

        if self.company_id:
            cdtn += ''' and so.company_id = %s
                                        ''' % (self.company_id.id)

        print(cdtn)

        query = """
            SELECT pt.categ_id AS categ,
                           sol.product_id AS product,
                           uom.id as uom_name,
                           bom.id as bom,
                           SUM(sol.product_uom_qty) AS total_qty,
                           '0' as i_type, so.id as s_type
                    FROM sale_order_line sol
                    LEFT JOIN sale_order so ON sol.order_id = so.id
                    LEFT JOIN uom_uom uom ON sol.product_uom = uom.id
                    LEFT JOIN product_product pp ON sol.product_id = pp.id
					LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
                    JOIN mrp_bom bom ON pt.id = bom.product_tmpl_id
                    %s 
                    GROUP BY sol.product_id, pt.categ_id,uom.id,bom.id, so.id
            """ % (cdtn)
        print(query)
        self._cr.execute(query)
        print(query)
        intent_ids = self._cr.dictfetchall()
        print('intent_ids', intent_ids)
        # amal
        row = []
        for line in intent_ids:
            row.append({'data': {
                'product': line['product'],
                'uom_name': line['uom_name']
            }})

        no_dup = []
        for i in row:
            if i['data'] not in no_dup:
                no_dup.append(i['data'])

        lst_final = []
        for v in no_dup:
            product = v['product']
            uom_name = v['uom_name']
            qty = 0
            bom = 0
            sale = []
            print('sale', sale)
            for i in intent_ids:
                if (i['product'] == product) and (i['uom_name'] == uom_name):
                    qty += i['total_qty']
                    bom = i['bom']
                    if i['s_type'] != 0:
                        sale.append(i['s_type'])
            lst_final.append({
                'product': product,
                'uom_name': uom_name,
                'bom': bom,
                'total_qty': qty,
                'sale': list(set(sale)),
            })

        result = lst_final
        # amal

        grouped_data = {}
        for item in intent_ids:
            product_id = item['product']
            if product_id in grouped_data:
                grouped_data[product_id]['total_qty'] += item['total_qty']
            else:
                grouped_data[product_id] = item

        # result = list(grouped_data.values())
        for i in result:
            sale = self.env['sale.order'].browse([value for value in i['sale']])

            self.write({
                'production_lines_ids': [(0, 0, {
                    'item_list_id': i['product'],
                    'bom_id': i['bom'],
                    'production_uom_id': i['uom_name'],
                    'order_quantity': i['total_qty'],
                    'sale_order_ids': [(6, 0, sale.ids)],
                })]
            })

    def action_waiting_approval(self):
        # plan = self.production_lines_ids
        user = self.env.uid
        # self.state = 'approval'
        date_today = date.today()
        print(date_today)
        if self.planning_date >= date_today:
            self.state = 'approval'
        else:
            raise UserError(_("Planning Date Must Be Greater or Equal To Today Date"))

    def action_approve(self):
        user = self.env.uid
        self.state = 'approve'

    def action_confirm(self):
        self.state = 'done'
        sale_ids = self.production_lines_ids.mapped('sale_order_ids')
        for a in sale_ids:
            query = """UPDATE sale_order
                       SET planing_id = %s
                        WHERE id = %s;"""
            query = query % (self.id, a.id)
            self._cr.execute(query)

        transfer_cdtn = '''where si.state ='approve' and si.planning_date BETWEEN '%s' AND '%s'

                                    ''' % (
            self.planning_date.strftime("%Y-%m-%d 00:00:00"), self.planning_date.strftime("%Y-%m-%d 23:59:59"))
        transfer = """
            SELECT ptb.categ_id AS categ,  
                   mbl.product_id AS product,
                   bom.id AS bom_id,
                   uom.id as uom_name,
                   sum(sil.actual_plan_qty * mbl.product_qty) as total
            FROM production_plan_lines sil
            LEFT JOIN plan_planing si ON sil.ref_id = si.id
            LEFT JOIN product_product pp ON sil.item_list_id = pp.id
            LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
            JOIN mrp_bom bom ON pt.id = bom.product_tmpl_id
            INNER JOIN mrp_bom_line mbl ON bom.id = mbl.bom_id
            LEFT JOIN product_product pn ON mbl.product_id = pn.id
            LEFT JOIN product_template ptb ON mbl.product_tmpl_id = ptb.id
            LEFT JOIN uom_uom uom ON mbl.product_uom_id = uom.id
            %s
            GROUP BY mbl.product_id, bom.id, ptb.categ_id, uom.id
        """ % (transfer_cdtn)

        self._cr.execute(transfer)
        transfer_ids = self._cr.dictfetchall()
        print(transfer_ids, 'pandal')
        transfer_list = []

        for j in transfer_ids:
            product = j['product']
            product_obj = self.env['product.product'].browse(product)
            temp = product_obj.product_tmpl_id
            bom = temp.bom_ids
            uom_qty = j['total']
            uom = self.env['uom.uom'].browse(j['uom_name'])
            if bom:
                for component in bom.bom_line_ids:
                    move_uom = component.product_uom_id
                    if move_uom.category_id == product_obj.uom_id.category_id:
                        # Convert UoM to the product's UoM category manually
                        uom_qty = self.env['uom.uom']._compute_quantity(
                            uom_qty,
                            uom,
                            move_uom,
                        )

                    transfer_list.append({
                        'product': component.product_id.id,
                        'qty': uom_qty,
                        'uom': move_uom
                    })
            else:
                if uom.category_id == product_obj.uom_id.category_id:
                    # Convert UoM to the product's UoM category manually
                    uom_qty = self.env['uom.uom']._compute_quantity(
                        uom_qty,
                        uom
                    )

                transfer_list.append({
                    'product': product,
                    'qty': uom_qty,
                    'uom': uom.id,
                })
            row = []
            for li in transfer_list:
                row.append({'data': {
                    'product': li['product'],
                    'uom': li['uom']
                }})

            no_dup = []
            for i in row:
                if i['data'] not in no_dup:
                    no_dup.append(i['data'])
            lst_final = []
            final = []
            for v in no_dup:
                product = v['product']
                uom = v['uom']
                qty = 0

                for i in transfer_list:
                    if (i['product'] == product) and (i['uom'] == uom):
                        qty += i['qty']
                lst_final.append({
                    'product': product,
                    'uom_name': uom,
                    'total_qty': qty
                })
        # Create the transfer move with all items in the list
        transfer_move = self.env['stock.picking'].sudo().create({
            'picking_type_id': self.company_id.production_picking_type_id.id,
            'company_id': self.company_id.id,
            'origin': "Material Request",
            'location_id': self.company_id.production_picking_type_id.default_location_src_id.id,
            'location_dest_id': self.company_id.production_picking_type_id.default_location_dest_id.id,
            'request_id': self.id,
            'move_ids_without_package': [(0, 0, {
                'product_id': item['product'],
                'name': item['product'],
                'product_uom_qty': item['total_qty'],
                'location_id': self.company_id.production_picking_type_id.default_location_src_id.id,
                'location_dest_id': self.company_id.production_picking_type_id.default_location_dest_id.id,
                'product_uom': item['uom_name'],
                'company_id': self.company_id.id,
            }) for item in lst_final]
        })


    def action_reject(self):
        if self.reason:
            self.state = 'reject'

    @api.onchange('tick')
    def _onchange_tick(self):
        self.production_lines_ids._compute_plan_qty()

    def action_open_purchase_transfer(self):
        return {
            'name': _('Transfer'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'tree,form',
            'domain': [('request_id', '=', self.id)],
        }

    # def action_open_manufacture(self):
    #     for j in self:
    #         return {
    #             'name': _('Manufacture'),
    #             'type': 'ir.actions.act_window',
    #             'res_model': 'mrp.production',
    #             'view_mode': 'tree,form',
    #             'domain': [('planing_id', '=', j.id)],
    #         }


class ProductionPlanningLines(models.Model):
    _name = 'production.plan.lines'
    _order = 'item_list_id ASC'

    item_list_id = fields.Many2one('product.product', string="Products")
    bom_id = fields.Many2one('mrp.bom', string="Bom")
    order_quantity = fields.Float(string="Total Order Qty")
    planed_quantity = fields.Float(string="Plan Qty", compute='_compute_plan_qty', store=True)
    on_quantity = fields.Float(string="Closing Stock", related="item_list_id.product_tmpl_id.qty_available")
    production_uom_id = fields.Many2one('uom.uom', string="Unit")
    ref_id = fields.Many2one('plan.planing')
    varience = fields.Float(string="Varience")
    actual_plan_qty = fields.Float(string="Actual Plan Qty", compute='_compute_actual_plan_qty', store=True)
    sale_order_ids = fields.Many2many('sale.order', 'sale_order_production_plan_line_rel',
                                      'plan_line_id', 'sale_id', string='Sales')
    indent_ids = fields.Many2many('indent.request', 'indent_request_production_plan_line_rel',
                                  'plan_line_id', 'indent_id', string='Indents')
    sale_indent_ids = fields.Many2many('sales.indent', 'sale_indent_request_production_plan_line_rel',
                                       'plan_line_id', 'indent_id', string='Indents')

    @api.depends('order_quantity', 'on_quantity')
    def _compute_plan_qty(self):
        self.planed_quantity = False
        for sel in self:
            if sel.ref_id.tick == True:
                if sel.order_quantity >= 0:
                    if sel.on_quantity == 0:
                        sel.planed_quantity = sel.order_quantity
                    elif sel.on_quantity >= sel.order_quantity:
                        sel.planed_quantity = 0
                    elif sel.on_quantity < sel.order_quantity:
                        sel.planed_quantity = sel.order_quantity - sel.on_quantity
                else:
                    sel.planed_quantity = 0
            else:
                if sel.order_quantity >= 0:
                    sel.planed_quantity = sel.order_quantity
                else:
                    sel.planed_quantity = 0

    @api.depends('varience', 'planed_quantity')
    def _compute_actual_plan_qty(self):
        self.actual_plan_qty = False
        for sel in self:
            if sel.planed_quantity > 0:
                if sel.varience > 0:
                    sel.actual_plan_qty = sel.planed_quantity + sel.varience
                elif sel.varience < 0:
                    a = sel.planed_quantity + sel.varience
                    if a < 0:
                        sel.actual_plan_qty = 0
                    else:
                        sel.actual_plan_qty = a
                elif sel.varience == 0:
                    sel.actual_plan_qty = sel.planed_quantity
            elif sel.planed_quantity == 0:
                if sel.varience > 0:
                    sel.actual_plan_qty = sel.planed_quantity + sel.varience
                elif sel.varience == 0:
                    sel.actual_plan_qty = sel.planed_quantity


class ResCompany(models.Model):
    _inherit = 'res.company'

    production_picking_type_id = fields.Many2one('stock.picking.type',
                                                 string='Picking Type For Material From Production')


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    request_id = fields.Many2one('plan.planing', string='Material Request For Production')


class SalesOrder(models.Model):
    _inherit = 'sale.order'

    planing_id = fields.Many2one('plan.planing', string='Planing')

    def action_cancel(self):
        for order in self:
            if order.planing_id:
                raise ValidationError("Cannot cancel order. Production planning already done.")
            else:
                rec = super(SalesOrder, order).action_cancel()
        return rec


class SalesIndent(models.Model):
    _inherit = 'sales.indent'

    planing_id = fields.Many2one('plan.planing', string='Planing')
class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    planing_id = fields.Many2one('plan.planing', string='Planing')

