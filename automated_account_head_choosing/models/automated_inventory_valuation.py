from odoo import api, fields, models, _ ,exceptions


class AutomatedInventoryValuation(models.Model):
    _name = 'automated.inventory.valuation'
    _rec_name ="reference"

    reference = fields.Char(string='Sl No', copy=False, default=lambda self: _('New'))
    costing_method = fields.Selection([
        ('standard', 'Standard Price'),
        ('fifo', 'First In First Out (FIFO)'),
        ('average', 'Average Cost (AVCO)')],
        required=True, string="Costing Method"
    )

    stock_valuation_account_id = fields.Many2one('account.account', string="Stock Valuation Account", required=True)
    stock_journal_id = fields.Many2one('account.journal', string="Stock Journal", required=True)
    stock_input_account_id = fields.Many2one('account.account', string="Stock Input Account", required=True)
    stock_output_account_id = fields.Many2one('account.account', string="Stock Output Account", required=True)
    company_id = fields.Many2one('res.company', string='company', required=True, readonly=True)

    @api.onchange('costing_method')
    def name_duplicate(self):
        if self.costing_method:
            rec = self.search([('costing_method', '=', self.costing_method)])
            if rec:
                raise exceptions.ValidationError(_("This Costing Method is Already exists!"))

    @api.model
    def create(self, vals):
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('automated.inventory.valuation') or _('New')
        res = super(AutomatedInventoryValuation, self).create(vals)
        return res


    @api.model
    def default_get(self, fields):
        res = super(AutomatedInventoryValuation, self).default_get(fields)
        x = self.env.company.id
        res.update({
            'company_id': x,
        })
        return res


class ProductCategory(models.Model):
    _inherit = 'product.category'


    @api.onchange('property_cost_method')
    def _onchange_property_cost_method(self):
        for k in self:
            k.property_stock_valuation_account_id =False
            k.property_stock_journal = False
            k.property_stock_account_input_categ_id =False
            k.property_stock_account_output_categ_id = False
            automated = self.env['automated.inventory.valuation'].search(
                [('costing_method', '=', k.property_cost_method)])
            print(automated,"yyyyy")
            for i in automated:
                if k.property_cost_method:
                    if i.stock_valuation_account_id.id:
                        k.property_stock_valuation_account_id = i.stock_valuation_account_id.id
                    if i.stock_journal_id:
                        k.property_stock_journal = i.stock_journal_id.id
                    if i.stock_input_account_id:
                        k.property_stock_account_input_categ_id = i.stock_input_account_id.id
                    if i.stock_output_account_id:
                        k.property_stock_account_output_categ_id = i.stock_output_account_id.id

# print(item,"ppppp")
# # if item:
# for i in item.bom_line_ids:
#     if k.product_id:
#         print(i.product_id.name)
#         print(i.product_id.id)
#         k.bom_id = i.product_id.id
