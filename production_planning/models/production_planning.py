from odoo import api, fields, models, _
from odoo.exceptions import Warning, AccessError, UserError
from datetime import datetime, date


class ProductionPlanning(models.Model):
    _name = 'production.planning'
    _description = 'Production Planning'
    _rec_name = "reference"

    planning_date = fields.Date(string="Planning Date", required=True)
    reference = fields.Char(string='Order Reference', required=True, copy=False, readonly=True,
                            default=lambda self: _('New'))
    reason = fields.Text(String="Reason")
    # kitchen_ids = fields.Many2many('item.kitchen', string='Kitchen', required=True)
    item_category_id = fields.Many2one('product.category', string="Item Category")
    production_lines_ids = fields.One2many('production.planning.lines', 'ref_id')
    state = fields.Selection(
        [('draft', 'Draft'), ('approval', 'Waiting For Approval'), ('approve', 'Approved'), ('reject', 'Rejected'),
         ('done', 'Done')],
        default='draft', string="Status")
    company_id = fields.Many2one('res.company', string='company', readonly=True,
                                 default=lambda self: self.env.company.id)
    # trip_ids = fields.Many2many('trip.details', string='Trip', default=lambda self: self.env['trip.details'].search([]))
    tick = fields.Boolean(string="Consider Closing Stock")
    production_sale_lines_ids = fields.One2many('production.order.lines', 'production_sale')

    @api.model
    def create(self, vals):
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('production.planning') or _('New')
        res = super(ProductionPlanning, self).create(vals)
        return res

    @api.returns('self')
    def copy(self, default=None):
        rec = super(ProductionPlanning, self).copy(default)
        if rec:
            raise UserError(_('You cannot duplicate production planning'))
        return rec

    def action_line_value(self):
        t1_name = self.production_lines_ids._fields['trip_1'].string
        t2_name = self.production_lines_ids._fields['trip_2'].string
        t3_name = self.production_lines_ids._fields['trip_3'].string
        t4_name = self.production_lines_ids._fields['trip_4'].string

        self.production_lines_ids.unlink()
        self.production_sale_lines_ids.unlink()
        user = self.env.uid
        for kit in self.kitchen_ids:
            material = self.env['operational.type.privilege'].search(
                [('user_ids', '=', user), ('kitchen_id', '=', kit.id)])
            if not material:
                raise AccessError(_("You Have No Access In The %s") % kit.name)

        # if self.planning_date:
        filter_cdtn = '''where so.state = 'sale' and  so.date_expected_delivery = '%s'
         ''' % (self.planning_date)
        if self.kitchen_ids:
            if len(self.kitchen_ids) == 1:
                filter_cdtn += '''and pt.item_kitchen_id = '%s'
                ''' % (self.kitchen_ids.ids[0])
            else:
                filter_cdtn += '''and pt.item_kitchen_id in {}
                '''.format(tuple(self.kitchen_ids.ids))
        if self.trip_ids:
            if len(self.trip_ids) == 1:
                filter_cdtn += '''and so.trip_id = '%s'
                ''' % (self.trip_ids.ids[0])
            else:
                filter_cdtn += '''and so.trip_id in {}
                '''.format(tuple(self.trip_ids.ids))
        if self.item_category_id:
            filter_cdtn += '''and pt.categ_id = '%s'
            ''' % self.item_category_id.id
        if self.company_id:
            filter_cdtn += '''and sal.company_id = '%s'
            ''' % self.company_id.id
        query = """select so.date_expected_delivery date,pt.item_kitchen_id kitchen,pt.categ_id categ,so.trip_id trip, td.name trip_name,
                        sal.product_id product,sal.product_uom uom,sal.product_uom_qty qty,sal.company_id com, sal.id sal_id from sale_order_line sal
                        left join sale_order so on sal.order_id = so.id
                        left join product_product pp on sal.product_id = pp.id
                        left join product_template pt on pp.product_tmpl_id = pt.id
                        left join trip_details td on so.trip_id = td.id    %s""" % (filter_cdtn)

        self._cr.execute(query)
        sale_order_ids = self._cr.dictfetchall()

        kitchen_vals = self.env['production.planning.lines']
        sale_vals = self.env['production.order.lines']
        rows = []
        lens = []
        for each in sale_order_ids:
            block = self.env['production.planning'].search(
                [('planning_date', '=', self.planning_date),
                 ('production_sale_lines_ids.pro_sale_line_id.id', '=', each['sal_id'])])
            if not block:
                rows.append({
                    'item_list_id': each['product'],
                    'order_quantity': each['qty'],
                    # 'on_quantity': each.product_id.qty_available,
                    'product_kitchen_id': each['kitchen'],
                    'production_uom_id': each['uom'],
                    'trip': each['trip_name'],
                    'ref_id': each['sal_id'],
                })
                lens.append({'data': {
                    'item_list_id': each['product'],
                }})

        no_dup = []
        for j in lens:
            if j['data'] not in no_dup:
                no_dup.append(j['data'])
        inv = []
        for v in no_dup:
            produc_id = v['item_list_id']
            # on_qt = 0
            pro_kit_id = ''
            pro_uom = ''
            trip1 = 0
            trip2 = 0
            trip3 = 0
            trip4 = 0
            for t in rows:
                if t['item_list_id'] == produc_id:
                    # on_qt = t['on_quantity']
                    pro_kit_id = t['product_kitchen_id']
                    pro_uom = t['production_uom_id']
                    if t1_name == t['trip']:
                        trip1 += t['order_quantity']
                    elif t2_name == t['trip']:
                        trip2 += t['order_quantity']
                    elif t3_name == t['trip']:
                        trip3 += t['order_quantity']
                    elif t4_name == t['trip']:
                        trip4 += t['order_quantity']
            inv.append({
                "item_list_id": produc_id,
                # "on_quantity": on_qt,
                "product_kitchen_id": pro_kit_id,
                "production_uom_id": pro_uom,
                "trip1": trip1,
                "trip2": trip2,
                "trip3": trip3,
                "trip4": trip4,
            })
        for k in inv:
            vals = {
                "item_list_id": k['item_list_id'],
                # "on_quantity": k['on_quantity'],
                "product_kitchen_id": k['product_kitchen_id'],
                "production_uom_id": k['production_uom_id'],
                "trip_1": k['trip1'],
                "trip_2": k['trip2'],
                "trip_3": k['trip3'],
                "trip_4": k['trip4'],
                "ref_id": self.id,
            }
            kitchen_vals.create(vals)
        for r in rows:
            val = {
                "pro_sale_line_id": r['ref_id'],
                "production_sale": self.id,
            }
            sale_vals.create(val)
        for pro_hand in self.production_lines_ids:
            pro_hand._onchange_product_item()

    def action_waiting_approval(self):
        plan = self.production_lines_ids
        user = self.env.uid
        date_today = date.today()
        if self.planning_date:
            if self.planning_date < date_today:
                raise Warning(_("Planning Date Must Be Greater or Equal To Today Date"))
            else:
                for kit in self.kitchen_ids:
                    material = self.env['operational.type.privilege'].search(
                        [('user_ids', '=', user), ('kitchen_id', '=', kit.id)])
                    if not material:
                        raise AccessError(_("You Have No Access In The %s") % kit.name)
                if plan:
                    for d in plan:
                        if d.product_kitchen_id:
                            mat = self.env['operational.type.privilege'].search(
                                [('user_ids', '=', user), ('kitchen_id', '=', d.product_kitchen_id.id)])
                            if not mat:
                                raise AccessError(_("You Have No Access In The %s") % d.product_kitchen_id.name)
                        else:
                            raise Warning(_("There Is No Product Kitchen"))
                    self.state = 'approval'
                else:
                    raise Warning(_("There Is No Products"))

    def action_approve(self):
        plan = self.production_lines_ids
        user = self.env.uid
        date_today = date.today()
        if self.planning_date:
            if self.planning_date < date_today:
                raise Warning(_("Planning Date Must Be Greater or Equal To Today Date"))
            else:
                for kit in self.kitchen_ids:
                    material = self.env['operational.type.privilege'].search(
                        [('user_ids', '=', user), ('kitchen_id', '=', kit.id)])
                    if not material:
                        raise AccessError(_("You Have No Access In The %s") % kit.name)
                if plan:
                    for d in plan:
                        if d.product_kitchen_id:
                            mat = self.env['operational.type.privilege'].search(
                                [('user_ids', '=', user), ('kitchen_id', '=', d.product_kitchen_id.id)])
                            if not mat:
                                raise AccessError(_("You Have No Access In The %s") % d.product_kitchen_id.name)
                        else:
                            raise Warning(_("There Is No Product Kitchen"))
                    self.state = 'approve'
                else:
                    raise Warning(_("There Is No Products"))

    def action_reject(self):
        if self.reason:
            self.state = 'reject'
        else:
            raise Warning(_("Please Add Reject Reason"))

    def action_confirm(self):
        plan = self.production_lines_ids
        user = self.env.uid
        row_kitchen = []
        if plan:
            for d in plan:
                if d.product_kitchen_id:
                    mat = self.env['operational.type.privilege'].search(
                        [('user_ids', '=', user), ('kitchen_id', '=', d.product_kitchen_id.id)])
                    if not mat:
                        raise AccessError(_("You Have No Access In The %s") % d.product_kitchen_id.name)
                else:
                    raise Warning(_("There Is No Product Kitchen"))

            length = []
            for loc in plan:
                if loc.actual_plan_qty != 0:
                    location = self.env['operational.type.privilege'].search(
                        [('user_ids', 'in', user), ('kitchen_id', '=', loc.product_kitchen_id.id),
                         ('operational_type_id.code', '=', 'internal')])
                    if location.id:
                        length.append(location.id)

            no_dup_id = []
            for dup_id in length:
                if dup_id not in no_dup_id:
                    no_dup_id.append(dup_id)

            if len(no_dup_id) >= 1:
                for op_type in no_dup_id:
                    operation_search = self.env['operational.type.privilege'].search([('id', '=', op_type)])
                    if not (
                            operation_search.operational_type_id.default_location_src_id and
                            operation_search.operational_type_id.default_location_dest_id):
                        raise Warning(_("Operation Type Was No Source or Destination Location"))
            else:
                raise Warning(_("You Cannot Create A Transfer"))

            for plan_kitchen in plan:
                if plan_kitchen.actual_plan_qty != 0:
                    check_kit = self.env['operational.type.privilege'].search(
                        [('user_ids', '=', user), ('kitchen_id', '=', plan_kitchen.product_kitchen_id.id),
                         ('operational_type_id.code', '=', 'internal')])
                    if check_kit:
                        row_kitchen.append(plan_kitchen.product_kitchen_id.id)

            no_dup_kitchen = []
            for dup_kitchen in row_kitchen:
                if dup_kitchen not in no_dup_kitchen:
                    no_dup_kitchen.append(dup_kitchen)

            for mul_transfer in no_dup_kitchen:
                operation_type_kitchen = self.env['operational.type.privilege'].search(
                    [('user_ids', '=', user), ('kitchen_id', '=', mul_transfer),
                     ('operational_type_id.code', '=', 'internal')])
                move_id = self.env['stock.picking'].create({
                    'picking_type_id': operation_type_kitchen.operational_type_id.id,
                    'location_id': operation_type_kitchen.operational_type_id.default_location_src_id.id,
                    'location_dest_id': operation_type_kitchen.operational_type_id.default_location_dest_id.id
                })
                rows = []
                lens = []
                for transfer in plan:
                    if transfer.actual_plan_qty != 0:
                        item = self.env['mrp.bom'].search(
                            [('product_tmpl_id', '=', transfer.item_list_id.product_tmpl_id.id)])
                        if item:
                            for i in item.bom_line_ids:
                                rows.append({
                                    'product_id': i.product_id.id,
                                    'product_qty': i.product_qty * transfer.actual_plan_qty,
                                    'part': i.product_id.partner_ref,
                                    'uom': i.product_uom_id.id,
                                    'kit': transfer.product_kitchen_id.id,
                                })
                                lens.append({'data': {
                                    'product_id': i.product_id.id,
                                    'kit': transfer.product_kitchen_id.id,
                                }})
                        else:
                            raise AccessError(_("Some Products Are Not Available In BOM"))

                no_dup = []
                for j in lens:
                    if j['data'] not in no_dup:
                        no_dup.append(j['data'])
                inv = []
                for v in no_dup:
                    produc_id = v['product_id']
                    kitc_id = v['kit']
                    product_qt = 0
                    partner = ''
                    pro_uom = 0
                    for t in rows:
                        if t['product_id'] == produc_id and t['kit'] == kitc_id:
                            product_qt += t['product_qty']
                            partner = t['part']
                            pro_uom = t['uom']
                    inv.append({
                        'product_id': produc_id,
                        'product_qty': product_qt,
                        'partner_ref': partner,
                        'product_uom': pro_uom,
                        'kitch': kitc_id,
                    })
                for x in inv:
                    if operation_type_kitchen.kitchen_id.id == x['kitch']:
                        move_id.write({
                            'move_ids_without_package': [(0, 0, {
                                'product_id': x['product_id'],
                                'product_uom_qty': x['product_qty'],
                                'name': x['partner_ref'],
                                'product_uom': x['product_uom'],
                                'location_id': move_id.location_id.id,
                                'location_dest_id': move_id.location_dest_id.id,
                            })]
                        })
            self.state = 'done'
        else:
            raise Warning(_("There Is No Products"))

    @api.onchange('tick')
    def _onchange_tick(self):
        self.production_lines_ids._compute_plan_qty()

    @api.onchange('planning_date')
    def _onchange_planning_date_(self):
        self.production_lines_ids.unlink()
        self.production_sale_lines_ids.unlink()

    @api.onchange('item_category_id')
    def _onchange_item_category_id_(self):
        self.production_lines_ids.unlink()
        self.production_sale_lines_ids.unlink()

    @api.onchange('kitchen_ids')
    def _onchange_kitchen_ids_(self):
        self.production_lines_ids.unlink()
        self.production_sale_lines_ids.unlink()

    @api.onchange('trip_ids')
    def _onchange_trip_ids_(self):
        self.production_lines_ids.unlink()
        self.production_sale_lines_ids.unlink()


class ProductionPlanningLines(models.Model):
    _name = 'production.planning.lines'
    _order = 'item_list_id ASC'

    item_list_id = fields.Many2one('product.product', string="Products")
    order_quantity = fields.Float(string="Total Order Qty", compute='_compute_line_order_qty')
    planed_quantity = fields.Float(string="Plan Qty", compute='_compute_plan_qty', store=True)
    on_quantity = fields.Float(string="Closing Stock")
    production_uom_id = fields.Many2one('uom.uom', string="Unit")
    ref_id = fields.Many2one('production.planning')
    product_kitchen_id = fields.Many2one('item.kitchen', string="Kitchen Name")
    varience = fields.Float(string="Varience")
    actual_plan_qty = fields.Float(string="Actual Plan Qty", compute='_compute_actual_plan_qty')
    trip_1 = fields.Float(string="Trip 1")
    trip_2 = fields.Float(string="Trip 2")
    trip_3 = fields.Float(string="Trip 3")
    trip_4 = fields.Float(string="Trip 4")

    @api.onchange('item_list_id')
    def _onchange_production_product_id(self):
        plan = self.ref_id
        list1 = []
        if plan.item_category_id:
            plan_category = self.env['product.product'].search(
                [('product_tmpl_id.categ_id', '=', plan.item_category_id.id)])
            for b in plan_category:
                list1.append(b.id)
            return {'domain': {'item_list_id': [('id', 'in', list1)]}}

    @api.depends('trip_1', 'trip_2', 'trip_3', 'trip_4')
    def _compute_line_order_qty(self):
        self.order_quantity = False
        for sel in self:
            if sel.trip_1 >= 0 and sel.trip_2 >= 0 and sel.trip_3 >= 0 and sel.trip_4 >= 0:
                sel.order_quantity = sel.trip_1 + sel.trip_2 + sel.trip_3 + sel.trip_4
            else:
                sel.order_quantity = 0

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

    @api.onchange('item_list_id')
    def _onchange_product_item(self):
        if self.item_list_id:
            if self.item_list_id.qty_available:
                self.on_quantity = self.item_list_id.qty_available
            if self.item_list_id.uom_id:
                self.production_uom_id = self.item_list_id.uom_id.id
            if self.item_list_id.item_kitchen_id:
                self.product_kitchen_id = self.item_list_id.item_kitchen_id.id

    @api.onchange('product_kitchen_id')
    def onchange_operation_kitchen_id(self):
        user = self.env.uid
        material = self.env['operational.type.privilege'].search([('user_ids', '=', user)])
        branch = []
        for com in material:
            branch.append(com.kitchen_id.id)
        domain = {'product_kitchen_id': [('id', 'in', branch)]}
        return {'domain': domain}

    _sql_constraints = [('plan_product_uniq', 'unique (ref_id, item_list_id)',
                         'Duplicate products in line not allowed !')]


class SaleOrderLines(models.Model):
    _name = 'production.order.lines'

    pro_sale_line_id = fields.Many2one('sale.order.line', string="Sale")
    production_sale = fields.Many2one('production.planning')


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    demand_no = fields.Char(string='Demand Note No')
