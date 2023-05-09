import qrcode
import base64
from io import BytesIO
from odoo import models, fields, api, _
from odoo.tools.misc import get_lang
from odoo.exceptions import UserError, ValidationError


class AccountMoveReport(models.Model):
    _inherit = 'account.move'

    amount_in_words = fields.Char(string='Amount In Words', compute='_compute_total_amount_in_words')
    discount_total = fields.Float(string='Total Discount', compute='_compute_discount_total')
    vehicle_number = fields.Char(string='Vehicle No:')
    prnt_qr_code = fields.Binary("QR Code", attachment=True, store=True, copy=False)
    export_type = fields.Selection([('exp_with_pay', 'Export with payment'), ('exp_wo_pay', 'Export without payment')])
    sez_type = fields.Selection([('sez_with_pay', 'SEZ with payment'), ('sez_wo_pay', 'SEZ without payment')])
    is_ship_diff_address = fields.Boolean(string="Is ship to different address?")
    ship_gst = fields.Char(string="GST")
    ship_legal_name = fields.Char(string="Legal Name")
    ship_add1 = fields.Char(string="Address1")
    ship_add2 = fields.Char(string="Address2")
    ship_loc = fields.Char(string="Location")
    ship_pin = fields.Char(string="PIN Code")
    ship_st_code = fields.Char(string="State Code")
    ship_state = fields.Selection([('01', 'Jammu & Kashmir'), ('02', 'Himachal Pradesh'), ('03', 'Punjab'),
                                   ('04', 'Chandigarh'), ('05', 'Uttranchal'), ('06', 'Haryana'), ('07', 'Delhi'),
                                   ('08', ' Rajasthan'), ('09', 'Uttar Pradesh'),
                                   ('10', ' Bihar'), ('11', ' Sikkim'), ('12', 'Arunachal Pradesh'),
                                   ('13', ' Nagaland'), ('14', ' Manipur'), ('15', ' Mizoram'),
                                   ('16', ' Tripura'), ('17', ' Meghalaya'), ('18', 'Assam'),
                                   ('19', ' West Bengal'), ('20', ' Jharkhand'), ('21', ' Orissa'),
                                   ('22', ' Chhattisgarh'), ('23', 'Madhya Pradesh'), ('24', ' Gujarat'),
                                   ('25', 'Daman & Diu'), ('26', 'Dadra & Nagar Haveli'),
                                   ('27', ' Maharashtra'), ('29', ' Karnataka'), ('30', ' Goa'),
                                   ('31', ' Lakshdweep'), ('32', 'Kerala'), ('33', 'Tamil Nadu'),
                                   ('34', ' Pondicherry'), ('35', 'Andaman & Nicobar Islands'),
                                   ('36', ' Telangana'), ('37', ' Andhra Pradesh'), ('38', 'Ladakh'),
                                   ('97', 'Other Territory'), ('96', 'Other Country')], string="State")
    is_export = fields.Boolean(string="Is Export?")
    exp_bill_no = fields.Char(string="Shipping Bill No:")
    exp_bill_date = fields.Date(string="Shipping Bill Date")
    convert_inr = fields.Float(string="INR Conversion", compute='compute_convert_inr')
    guest_name = fields.Char(string="Guest Name:")
    reversal_account_id = fields.Many2one('account.move', string='Invoice Reference No')

    @api.depends('currency_id')
    def compute_convert_inr(self):
        self.convert_inr = 1 / self.currency_id.rate

    def einv_compute(self):
        res = super(AccountMoveReport, self).einv_compute()
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=20,
            border=8,
        )
        # qr.add_data(self.einv_qr_code)
        qr.make(fit=True)
        img = qr.make_image()
        temp = BytesIO()
        img.save(temp, format="PNG")
        qr_image = base64.b64encode(temp.getvalue())
        self.prnt_qr_code = qr_image
        return res

    @api.depends('amount_total', 'currency_id')
    def _compute_total_amount_in_words(self):
        for move in self:
            if move.amount_total:
                move.amount_in_words = move.currency_id.amount_to_text(move.amount_total)
            else:
                move.amount_in_words = False

    @api.depends('invoice_line_ids.discount_amount')
    def _compute_discount_total(self):
        sum = 0
        for i in self.invoice_line_ids:
            sum += i.discount_amount
        self.discount_total = sum

    # @api.onchange('ship_state')
    # def _onchange_ship_state(self):
    #     for rec in self:
    #         if rec.ship_state:
    #             rec.ship_st_code = rec.ship_state

    @api.onchange('reversal_account_id')
    def _onchange_reversal_account_id(self):
        if self.reversal_account_id:
            if not self.partner_id:
                self.partner_id = self.reversal_account_id.partner_id
            if not self.partner_shipping_id:
                self.partner_shipping_id = self.reversal_account_id.partner_shipping_id
            # if not self.l10n_in_gst_treatment:
            #     self.l10n_in_gst_treatment = self.reversal_account_id.l10n_in_gst_treatment
        else:
            self.partner_id = False
            self.partner_shipping_id = False
            # self.l10n_in_gst_treatment = False

    @api.onchange('partner_id')
    def _onchange_customer(self):
        if self.partner_id:
            self.env.cr.execute(("""SELECT am.id 
                                    FROM account_move as am
                                    where am.state = 'posted' and am.partner_id = %s
                                         """)
                                % self.partner_id.id)
            account = self.env.cr.dictfetchall()
            move_list = []
            for move in account:
                move_list.append(move['id'])
            return {'domain': {'reversal_account_id': [('id', 'in', tuple(move_list))]}}

    def action_add_product(self):
        if self.reversal_account_id:
            product_list = []
            for inv in self.reversal_account_id.invoice_line_ids:
                if inv.product_id:
                    product_list.append(inv.product_id.id)
            view = self.env.ref('sales_invoice_print.add_product_wizard_form_view')
            return {
                'name': 'Add Product',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'add.product.wizard',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'context': {
                    'default_productids': product_list,
                    'default_move_id': self.id,
                }
            }


            # def fields_view_get(self, view_id=None, view_type='list', toolbar=False, submenu=False):
    #     res = super().fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
    #     if toolbar:
    #         for action in res['toolbar'].get('action'):
    #             if action.get('xml_id'):
    #                 if action['xml_id'] == 'account.action_validate_account_move':
    #                     res['toolbar']['action'].remove(action)
    #     return res


class AccountMoveReportLine(models.Model):
    _inherit = 'account.move.line'

    discount_amount = fields.Float(string='Discount Amount', compute='_compute_line_discount_amount')
    sgst_perc = fields.Monetary(string='SGST', copy=False, store=True, compute='_compute_tax_computation')
    cgst_perc = fields.Monetary(string='CGST', copy=False, store=True, compute='_compute_tax_computation')
    igst_perc = fields.Monetary(string='IGST', copy=False, store=True, compute='_compute_tax_computation')
    cess = fields.Monetary(string='Cess', copy=False, store=True, compute='_compute_tax_computation')
    sgst_amount = fields.Monetary(string='sgst Rate', copy=False, store=True, compute='_compute_tax_computation')
    cgst_amount = fields.Monetary(string='cgst Rate', copy=False, store=True, compute='_compute_tax_computation')
    igst_amount = fields.Monetary(string='igst Rate', copy=False, store=True, compute='_compute_tax_computation')
    cess_amount = fields.Monetary(string='cess Rate', copy=False, store=True, compute='_compute_tax_computation')

    @api.depends('tax_ids', 'product_id', 'price_subtotal')
    def _compute_tax_computation(self):
        for i in self:
            if i.move_id.move_type == 'out_invoice':
                if i.tax_ids:
                    if len(i.tax_ids) == 1:
                        if i.tax_ids.amount != 0:
                            print('5')
                            res = i.tax_ids._origin.compute_all(i.price_subtotal, product=i.product_id,
                                                                partner=i.partner_id)
                            for tax in res['taxes']:
                                if tax['amount'] > 0:
                                    amount_tax = self.env['account.tax'].search([('id', '=', tax['id'])])
                                    if 'CESS' in tax['name'].upper():
                                        i.cess = tax['amount']
                                        i.cess_amount = amount_tax.amount
                                    if 'SGST' in tax['name'].upper():
                                        i.sgst_perc = tax['amount']
                                        i.sgst_amount = amount_tax.amount
                                    if 'CGST' in tax['name'].upper():
                                        i.cgst_perc = tax['amount']
                                        i.cgst_amount = amount_tax.amount
                                    if 'IGST' in tax['name'].upper():
                                        i.igst_perc = tax['amount']
                                        i.igst_amount = amount_tax.amount
                        else:
                            i.cess = False
                            i.cess_amount = False
                            i.sgst_perc = False
                            i.sgst_amount = False
                            i.cgst_perc = False
                            i.cgst_amount = False
                            i.igst_perc = False
                            i.igst_amount = False
                    else:
                        i.cess = False
                        i.cess_amount = False
                        i.sgst_perc = False
                        i.sgst_amount = False
                        i.cgst_perc = False
                        i.cgst_amount = False
                        i.igst_perc = False
                        i.igst_amount = False
                else:
                    i.cess = False
                    i.cess_amount = False
                    i.sgst_perc = False
                    i.sgst_amount = False
                    i.cgst_perc = False
                    i.cgst_amount = False
                    i.igst_perc = False
                    i.igst_amount = False
            else:
                i.cess = False
                i.cess_amount = False
                i.sgst_perc = False
                i.sgst_amount = False
                i.cgst_perc = False
                i.cgst_amount = False
                i.igst_perc = False
                i.igst_amount = False

    # @api.onchange('discount', 'price_unit', 'quantity')
    # def onchange_discount_amount(self):
    #     if self.discount:
    #         disc = (self.discount * (self.price_unit * self.quantity)) / 100
    #         self.discount_amount = disc

    @api.depends('discount', 'price_unit', 'quantity')
    def _compute_line_discount_amount(self):
        for d in self:
            if d.discount:
                disc = (d.discount * (d.price_unit * d.quantity)) / 100
                d.discount_amount = disc
            else:
                d.discount_amount = False

    @api.onchange('move_id.reversal_account_id', 'product_id')
    def _onchange_invoice_ref(self):
        if self.move_id.reversal_account_id:
            product_list = []
            for inv in self.move_id.reversal_account_id.invoice_line_ids:
                if inv.product_id:
                    product_list.append(inv.product_id.id)
            return {'domain': {'product_id': [('id', 'in', tuple(product_list))]}}


class ResPartnerInherit(models.Model):
    _inherit = 'res.company'

    acc_bank_name = fields.Char(string='Bank Name')
    bank_branch = fields.Char(string='Bank Branch')
    acc_number = fields.Char(string='Account Number')
    bank_ifsc = fields.Char(string='IFSC Code')
    fssai_no = fields.Char(string='FSSAI No')
    code_qr = fields.Binary(string='UPI')
    swift_code = fields.Char(string='Swift Code')
    currency_remitted = fields.Many2one('res.currency', string='Currency to be remitted')
    cin_no = fields.Char(string='CIN Number')


class SaleOrderConfirm(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super(SaleOrderConfirm, self).action_confirm()
        for i in self.order_line:
            if len(i.tax_id) > 1:
                raise ValidationError(_('Single Tax value should be given'))
        return res

    def _prepare_invoice(self):
        res = super(SaleOrderConfirm, self)._prepare_invoice()
        if self.ship_partner_id.state_id.name == 'Jammu & Kashmir':
            res['ship_state'] = '01'
            res['ship_st_code'] = '01'
        if self.ship_partner_id.state_id.name == 'Himachal Pradesh':
            res['ship_state'] = '02'
            res['ship_st_code'] = '02'
        if self.ship_partner_id.state_id.name == 'Punjab':
            res['ship_state'] = '03'
            res['ship_st_code'] = '03'
        if self.ship_partner_id.state_id.name == 'Chandigarh':
            res['ship_state'] = '04'
            res['ship_st_code'] = '04'
        if self.ship_partner_id.state_id.name == 'Uttranchal':
            res['ship_state'] = '05'
            res['ship_st_code'] = '05'
        if self.ship_partner_id.state_id.name == 'Haryana':
            res['ship_state'] = '06'
            res['ship_st_code'] = '06'
        if self.ship_partner_id.state_id.name == 'Delhi':
            res['ship_state'] = '07'
            res['ship_st_code'] = '07'
        if self.ship_partner_id.state_id.name == 'Rajasthan':
            res['ship_state'] = '08'
            res['ship_st_code'] = '08'
        if self.ship_partner_id.state_id.name == 'Uttar Pradesh':
            res['ship_state'] = '09'
            res['ship_st_code'] = '09'
        if self.ship_partner_id.state_id.name == 'Bihar':
            res['ship_state'] = '10'
            res['ship_st_code'] = '10'
        if self.ship_partner_id.state_id.name == 'Sikkim':
            res['ship_state'] = '11'
            res['ship_st_code'] = '11'
        if self.ship_partner_id.state_id.name == 'Arunachal Pradesh':
            res['ship_state'] = '12'
            res['ship_st_code'] = '12'
        if self.ship_partner_id.state_id.name == 'Nagaland':
            res['ship_state'] = '13'
            res['ship_st_code'] = '13'
        if self.ship_partner_id.state_id.name == 'Manipur':
            res['ship_state'] = '14'
            res['ship_st_code'] = '14'
        if self.ship_partner_id.state_id.name == 'Mizoram':
            res['ship_state'] = '15'
            res['ship_st_code'] = '15'
        if self.ship_partner_id.state_id.name == 'Tripura':
            res['ship_state'] = '16'
            res['ship_st_code'] = '16'
        if self.ship_partner_id.state_id.name == 'Meghalaya':
            res['ship_state'] = '17'
            res['ship_st_code'] = '17'
        if self.ship_partner_id.state_id.name == 'Assam':
            res['ship_state'] = '18'
            res['ship_st_code'] = '18'
        if self.ship_partner_id.state_id.name == 'West Bengal':
            res['ship_state'] = '19'
            res['ship_st_code'] = '19'
        if self.ship_partner_id.state_id.name == 'Jharkhand':
            res['ship_state'] = '20'
            res['ship_st_code'] = '20'
        if self.ship_partner_id.state_id.name == 'Orissa':
            res['ship_state'] = '21'
            res['ship_st_code'] = '21'
        if self.ship_partner_id.state_id.name == 'Chhattisgarh':
            res['ship_state'] = '22'
            res['ship_st_code'] = '22'
        if self.ship_partner_id.state_id.name == 'Madhya Pradesh':
            res['ship_state'] = '23'
            res['ship_st_code'] = '23'
        if self.ship_partner_id.state_id.name == 'Gujarat':
            res['ship_state'] = '24'
            res['ship_st_code'] = '24'
        if self.ship_partner_id.state_id.name == 'Daman & Diu':
            res['ship_state'] = '25'
            res['ship_st_code'] = '25'
        if self.ship_partner_id.state_id.name == 'Dadra & Nagar Haveli':
            res['ship_state'] = '26'
            res['ship_st_code'] = '26'
        if self.ship_partner_id.state_id.name == 'Maharashtra':
            res['ship_state'] = '27'
            res['ship_st_code'] = '27'
        if self.ship_partner_id.state_id.name == 'Karnataka':
            res['ship_state'] = '29'
            res['ship_st_code'] = '29'
        if self.ship_partner_id.state_id.name == 'Goa':
            res['ship_state'] = '30'
            res['ship_st_code'] = '30'
        if self.ship_partner_id.state_id.name == 'Lakshadweep':
            res['ship_state'] = '31'
            res['ship_st_code'] = '31'
        if self.ship_partner_id.state_id.name == 'Kerala':
            res['ship_state'] = '32'
            res['ship_st_code'] = '32'
        if self.ship_partner_id.state_id.name == 'Tamil Nadu':
            res['ship_state'] = '33'
            res['ship_st_code'] = '33'
        if self.ship_partner_id.state_id.name == 'Pondicherry':
            res['ship_state'] = '34'
            res['ship_st_code'] = '34'
        if self.ship_partner_id.state_id.name == 'Andaman & Nicobar Islands':
            res['ship_state'] = '35'
            res['ship_st_code'] = '35'
        if self.ship_partner_id.state_id.name == 'Telangana':
            res['ship_state'] = '36'
            res['ship_st_code'] = '36'
        if self.ship_partner_id.state_id.name == 'Andhra Pradesh':
            res['ship_state'] = '37'
            res['ship_st_code'] = '37'
        if self.ship_partner_id.state_id.name == 'Ladakh':
            res['ship_state'] = '38'
            res['ship_st_code'] = '38'
        if self.ship_partner_id.state_id.name == 'Other Territory':
            res['ship_state'] = '97'
            res['ship_st_code'] = '97'
        if self.ship_partner_id.state_id.name == 'Other Country':
            res['ship_state'] = '96'
            res['ship_st_code'] = '96'

        res['is_ship_diff_address'] = self.is_ship_to
        res['ship_legal_name'] = self.ship_partner_id.name
        res['ship_add1'] = self.ship_partner_id.street
        res['ship_add2'] = self.ship_partner_id.street2
        res['ship_loc'] = self.ship_partner_id.city
        res['ship_pin'] = self.ship_partner_id.zip
        res['ship_state'] = self.ship_partner_id.state_id.id
        account_id = self.env['account.move'].sudo().search([('invoice_origin', '=', res['invoice_origin'])])
        return res


class ProductQR(models.Model):
    _inherit = "account.move"
    qr_code = fields.Binary("QR Code", attachment=True, store=True)

    @api.onchange('default_code')
    def generate_qr_code(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.default_code)
        qr.make(fit=True)
        img = qr.make_image()
        temp = BytesIO()
        img.save(temp, format="PNG")
        qr_image = base64.b64encode(temp.getvalue())
        self.qr_code = qr_image
