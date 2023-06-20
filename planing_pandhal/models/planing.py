from odoo import api, fields, models, _
from odoo.exceptions import Warning, AccessError, UserError
from datetime import datetime, date


class PlanPlaning(models.Model):
    _name = 'plan.planing'
    _description = 'Plan'
    _rec_name = "reference"

    planning_date = fields.Date(string="Planning Date", required=True)
    reference = fields.Char(string='Order Reference', required=True, copy=False, readonly=True,
                            default=lambda self: _('New'))
    reason = fields.Text(String="Reason")
    item_category_id = fields.Many2one('product.category', string="Item Category")
    production_lines_ids = fields.One2many('production.plan.lines', 'ref_id')
    state = fields.Selection(
        [('draft', 'Draft'), ('approval', 'Waiting For Approval'), ('approve', 'Approved'), ('reject', 'Rejected'),
         ('done', 'Done')],
        default='draft', string="Status")
    company_id = fields.Many2one('res.company', string='company', readonly=True,
                                 default=lambda self: self.env.company.id)
    tick = fields.Boolean(string="Consider Closing Stock")

    @api.model
    def create(self, vals):
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('production.planning') or _('New')
        res = super(PlanPlaning, self).create(vals)
        return res

    def action_line_value(self):
        self.production_lines_ids = False
        cdtn = '''where so.state = 'sale' and si.expected_date BETWEEN '%s' AND '%s'

                        ''' % (
        self.planning_date.strftime("%Y-%m-%d 00:00:00"), self.planning_date.strftime("%Y-%m-%d 23:59:59"))

        filter_cdtn = '''where si.state = 'confirmed' and si.expected_date BETWEEN '%s' AND '%s'

        ''' % (self.planning_date.strftime("%Y-%m-%d 00:00:00"), self.planning_date.strftime("%Y-%m-%d 23:59:59"))
        cdtn = '''where so.state = 'sale' and so.validity_date BETWEEN '%s' AND '%s'
                ''' % (
        self.planning_date.strftime("%Y-%m-%d 00:00:00"), self.planning_date.strftime("%Y-%m-%d 23:59:59"))
        if self.item_category_id:
            filter_cdtn += ''' and pt.categ_id = %s 
            ''' % (self.item_category_id.id)
            cdtn += ''' and pt.categ_id = %s 
                                        ''' % (self.item_category_id.id)

        if self.company_id:
            filter_cdtn += ''' and si.company_id = %s
            ''' % (self.company_id.id)
            cdtn += ''' and so.company_id = %s
                                        ''' % (self.company_id.id)

        print(filter_cdtn)
        print(cdtn)

        query = """
            SELECT pt.categ_id AS categ,
                   sil.product_id AS product,
                   uom.id as uom_name,
                   bom.id as bom,
                   SUM(sil.qty) AS total_qty
            FROM sales_indent_lines sil
            LEFT JOIN sales_indent si ON sil.pur_id = si.id
            LEFT JOIN uom_uom uom ON sil.uom_id = uom.id
            LEFT JOIN product_product pp ON sil.product_id = pp.id
            LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
            JOIN mrp_bom bom ON pt.id = bom.product_tmpl_id
            %s 
            GROUP BY sil.product_id, pt.categ_id,uom.id,bom.id
            union all
            SELECT pt.categ_id AS categ,
                           sol.product_id AS product,
                           uom.id as uom_name,
                           bom.id as bom,
                           SUM(sol.product_uom_qty) AS total_qty
                    FROM sale_order_line sol
                    LEFT JOIN sale_order so ON sol.order_id = so.id
                    LEFT JOIN uom_uom uom ON sol.product_uom = uom.id
                    LEFT JOIN product_product pp ON sol.product_id = pp.id
                    LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
                    JOIN mrp_bom bom ON pt.id = bom.product_tmpl_id
                    %s 
                    GROUP BY sol.product_id, pt.categ_id,uom.id,bom.id
            """ % (filter_cdtn, cdtn)
        print(query)
        self._cr.execute(query)
        print(query)
        intent_ids = self._cr.dictfetchall()
        print(intent_ids, 'pandal')
        for each in intent_ids:
            print(each['product'])
            print(each['total_qty'])
            print(each['uom_name'])
            self.write({
                'production_lines_ids': [(0, 0, {
                    'item_list_id': each['product'],
                    'order_quantity': each['total_qty'],
                    'production_uom_id': each['uom_name'],

                })]
            })

    def action_waiting_approval(self):
        # plan = self.production_lines_ids
        user = self.env.uid
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
    #     self.action_create_transfer()
    # def action_create_transfer(self):
    #     if self.company_id.production_operation_type:
    #         if self.company_id.production_operation_type.default_location_src_id and self.company_id.production_operation_type.default_location_dest_id:
    #             picking_type = self.company_id.production_operation_type
    #             to_location_id = self.company_id.production_operation_type.default_location_dest_id
    #             from_location_id = self.company_id.production_operation_type.default_location_src_id
    #             transfer_move = self.env['stock.picking'].create({
    #                 # 'partner_id': self.sale_id.partner_id.id,
    #                 'picking_type_id': picking_type.id,
    #                 'company_id': self.company_id.id,
    #                 'origin': "Material Request",
    #                 # 'project_name': self.project_name_id.id,
    #                 # 'project_task': self.project_task_id.id,
    #                 'location_id': from_location_id.id,
    #                 'location_dest_id': to_location_id.id,
    #                 'production_id': self.id,
    #             })
    #             for vals in self.product_line_ids:
    #                 transfer_move.sudo().write({
    #                     'move_ids_without_package': [(0, 0, {
    #                         'product_id': vals.product_id.id,
    #                         'name': vals.product_id.name,
    #                         'product_uom_qty': vals.quantity,
    #                         'location_id': from_location_id.id,
    #                         'location_dest_id': to_location_id.id,
    #                         'product_uom': vals.product_uom_id.id,
    #                         'company_id': self.company_id.id,
    #                     })]
    #                 })
    def action_reject(self):
        if self.reason:
           self.state = 'reject'

    @api.onchange('tick')
    def _onchange_tick(self):
        self.production_lines_ids._compute_plan_qty()


class ProductionPlanningLines(models.Model):
    _name = 'production.plan.lines'
    _order = 'item_list_id ASC'

    item_list_id = fields.Many2one('product.product', string="Products")
    order_quantity = fields.Float(string="Total Order Qty")
    planed_quantity = fields.Float(string="Plan Qty",compute='_compute_plan_qty', store=True)
    on_quantity = fields.Float(string="Closing Stock",related="item_list_id.product_tmpl_id.qty_available")
    production_uom_id = fields.Many2one('uom.uom', string="Unit")
    ref_id = fields.Many2one('plan.planing')
    varience = fields.Float(string="Varience")
    actual_plan_qty = fields.Float(string="Actual Plan Qty", compute='_compute_actual_plan_qty',store=True)

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

# class ResCompany(models.Model):
#      _inherit = 'res.company'
#
#      production_picking_id = fields.Many2one('')