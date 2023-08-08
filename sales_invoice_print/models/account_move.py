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
    total_global_discount = fields.Float(string='Total Global Discount')
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
    convert_inr = fields.Float(string="INR Conversion", compute='compute_convert_inr', store=True)
    terms_and_con = fields.Char(string="Terms and Condition")

    supplier_bill_ref = fields.Char(string="Supplier Bill Reference")
    supplier_bill_date = fields.Date(string="Supplier Bill Date")

    sales_amount_in_words = fields.Char(string='Amount In Words', compute='_compute_total_sales_amount_in_words')

    show_fssai = fields.Boolean(string="FSSAI", default=True)

    def action_reverse(self):
        res = super(AccountMoveReport, self).action_reverse()
        self.supplier_bill_ref = self.ref
        self.supplier_bill_date = self.invoice_date
        return res

    @api.depends('currency_id', 'invoice_date')
    def compute_convert_inr(self):
        for sel in self:
            if sel.invoice_date:
                rate = self.env['res.currency.rate'].search(
                    [('name', '<=', sel.invoice_date), ('currency_id', '=', sel.currency_id.id)], limit=1,
                    order='name desc')
                if rate:
                    sel.convert_inr = 1 / rate.rate
                elif not rate:
                    sel.convert_inr = 1 / sel.currency_id.rate
                else:
                    sel.convert_inr = 1
            else:
                sel.convert_inr = 1 / sel.currency_id.rate

    def inv_compute(self):
        res = super(AccountMoveReport, self).inv_compute()
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=20,
            border=8,
        )
        # qr.add_data(self.inv_qr_code)
        qr.make(fit=True)
        img = qr.make_image()
        temp = BytesIO()
        img.save(temp, format="PNG")
        qr_image = base64.b64encode(temp.getvalue())
        self.prnt_qr_code = qr_image
        return res

    # def inv_qr_generate(self):
    #     if self.inv_qr_code:
    #         qr = qrcode.QRCode(
    #             version=1,
    #             error_correction=qrcode.constants.ERROR_CORRECT_L,
    #             box_size=20,
    #             border=8,
    #         )
    #         qr.add_data(self.inv_qr_code)
    #         qr.make(fit=True)
    #         img = qr.make_image()
    #         temp = BytesIO()
    #         img.save(temp, format="PNG")
    #         qr_image = base64.b64encode(temp.getvalue())
    #         self.prnt_qr_code = qr_image

    @api.depends('amount_untaxed', 'currency_id')
    def _compute_total_amount_in_words(self):
        INR = self.env['res.currency'].search([('name', '=', 'INR')])
        for move in self:
            # if move.amount_total:
            #     total = move.amount_total * move.convert_inr
            #     move.amount_in_words = INR.amount_to_text(total)
            # else:
            #     move.amount_in_words = False
            sgst = 0
            cgst = 0
            igst = 0
            for i in self.invoice_line_ids:
                sgst += round(i.sgst_perc + 10 ** (-2 * 2), 2)
                cgst += round(i.cgst_perc + 10 ** (-2 * 2), 2)
                igst += round(i.igst_perc + 10 ** (-2 * 2), 2)
            # sgst = sum(self.invoice_line_ids.mapped('sgst_perc'))
            # cgst = sum(self.invoice_line_ids.mapped('cgst_perc'))
            # igst = sum(self.invoice_line_ids.mapped('igst_perc'))
            dis = move.total_global_discount * move.convert_inr
            if move.amount_untaxed:
                total = (
                                move.amount_untaxed * move.convert_inr + sgst * move.convert_inr + cgst * move.convert_inr + igst * move.convert_inr) - dis
                move.amount_in_words = INR.amount_to_text(total)
            else:
                move.amount_in_words = False

    @api.depends('amount_untaxed', 'currency_id')
    def _compute_total_sales_amount_in_words(self):
        INR = self.env['res.currency'].search([('name', '=', 'INR')])
        for move in self:
            sub_total = 0
            sgst = 0
            cgst = 0
            igst = 0
            for i in self.invoice_line_ids:
                sub_total += i.price_subtotal
                sgst += i.sgst_perc
                cgst += i.cgst_perc
                igst += i.igst_perc
            # sgst = sum(self.invoice_line_ids.mapped('sgst_perc'))
            # cgst = sum(self.invoice_line_ids.mapped('cgst_perc'))
            # igst = sum(self.invoice_line_ids.mapped('igst_perc'))
            dis = move.total_global_discount
            if move.amount_untaxed:
                total = round((((sub_total + sgst + cgst + igst) - dis) * move.convert_inr) + 10 ** (-2 * 2), 2)
                move.sales_amount_in_words = INR.amount_to_text(total)
            else:
                move.sales_amount_in_words = False

    # @api.depends('amount_total')
    # def _compute_total_amount_in_words(self):
    #     amount_words = self.currency_id.id
    #     value = self.env['res.currency'].search([('id', '=', amount_words)])
    #     for move in self:
    #         if move.amount_total:
    #             if move.convert_inr > 0:
    #                 move.amount_in_words = value.amount_to_text(move.amount_total * move.convert_inr)
    #             else:
    #                 move.amount_in_words = value.amount_to_text(move.amount_total)
    #         else:
    #             move.amount_in_words = False

    @api.depends('invoice_line_ids.discount_amount')
    def _compute_discount_total(self):
        sum = 0
        for i in self.invoice_line_ids:
            sum += i.discount_amount
        self.discount_total = sum

    def action_post(self):
        res = super(AccountMoveReport, self).action_post()
        for i in self.invoice_line_ids:
            i.convert_inr_amount = i.move_id.convert_inr * i.price_subtotal
        return res

    # def action_post(self):
    #     res = super(AccountMoveReport, self).action_post()
    #     for i in self.invoice_line_ids:
    #         if len(i.tax_ids) > 1:
    #             raise ValidationError(_('Single Tax value should be given'))
    #
    #     for inv in self.invoice_line_ids:
    #         if inv.tax_ids.tax_group_id.name == 'IGST' and inv.tax_ids.amount:
    #             inv.igst_perc = (inv.price_subtotal * inv.tax_ids.amount) / 100
    #             inv.igst_amount = inv.tax_ids.amount
    #             inv.sgst_perc = 0.00
    #             inv.cgst_perc = 0.00
    #             inv.sgst_amount = 0.00
    #             inv.cgst_amount = 0.00
    #             tax = inv.tax_ids.compute_all(inv.price_unit, product=inv.product_id,
    #                                           partner=inv.env.user.partner_id)
    #             print(tax)
    #             print(tax['taxes'][0]['amount'])
    #             print(inv.price_unit, '////')
    #             print(tax['taxes'][0]['amount'] * inv.quantity)
    #             print(inv.move_id.convert_inr)
    #             print(tax['taxes'][0]['amount'] * inv.quantity * inv.move_id.convert_inr)
    #             print(inv.tax_ids.amount, "ghsdjturytdftuyjtkfhgh")
    #             print(inv.igst_amount, "ghsdjturytdftuyjtkfhgh")
    #
    #         elif inv.tax_ids.amount:
    #             inv.cgst_perc = (inv.price_subtotal * (inv.tax_ids.amount / 2)) / 100
    #             inv.sgst_perc = (inv.price_subtotal * (inv.tax_ids.amount / 2)) / 100
    #             inv.sgst_amount = inv.tax_ids.amount / 2
    #             inv.cgst_amount = inv.tax_ids.amount / 2
    #             inv.igst_perc = 0.00
    #             inv.igst_amount = 0.00
    #
    #             ### old V
    #             # account = self.env['account.move.line'].search(
    #             #     [('move_id', '=', inv.move_id.id), ('id', '!=', inv.id),
    #             #      ('product_id', '=', inv.product_id.id)])
    #             # for k in account:
    #             #     for j in inv.tax_ids.children_tax_ids:
    #             #         if k.tax_line_id.id == j.id:
    #             #             # if self.move_type == 'out_invoice':
    #             #             #     inv.sgst_perc = k.credit if k.credit else k.debit
    #             #             #     inv.cgst_perc = k.credit if k.credit else k.debit
    #             #             #     inv.sgst_amount = j.amount
    #             #             #     inv.cgst_amount = j.amount
    #             #             #     inv.igst_perc = 0.00
    #             #             #     inv.igst_amount = 0.00
    #             #             # if self.move_type == 'out_refund':
    #             #             #     inv.sgst_perc = k.debit if k.credit else k.debit
    #             #             #     inv.cgst_perc = k.debit if k.credit else k.debit
    #             #             #     inv.sgst_amount = j.amount
    #             #             #     inv.cgst_amount = j.amount
    #             #             #     inv.igst_perc = 0.00
    #             #             #     inv.igst_amount = 0.00
    #             #             # else:
    #             #             inv.sgst_perc = k.credit if k.credit else k.debit
    #             #             inv.cgst_perc = k.credit if k.credit else k.debit
    #             #             inv.sgst_amount = j.amount
    #             #             inv.cgst_amount = j.amount
    #             #             inv.igst_perc = 0.00
    #             #             inv.igst_amount = 0.00
    #
    #         # for d in self.line_ids:
    #         #     for w in self.invoice_line_ids:
    #         #         print(w.price_total)
    #         #         if d.product_id.id == w.product_id.id:
    #         #             if d.tax_line_id:
    #         #                 if d.tax_line_id.id == w.tax_ids.id:
    #         #                     # w.igst_perc = w.price_total - w.price_subtotal
    #         #                     # w.igst_perc = d.credit if d.credit else d.debit
    #         #                     w.igst_perc = (w.price_subtotal * w.tax_ids.amount)/100
    #         #                     w.igst_amount = w.tax_ids.amount
    #         #                     w.sgst_perc = 0.00
    #         #                     w.cgst_perc = 0.00
    #         #                     w.sgst_amount = 0.00
    #         #                     w.cgst_amount = 0.00
    #         ##old ^
    #         tax = self.invoice_line_ids.mapped('tax_ids')
    #         lst = []
    #         for t in tax:
    #             line = self.invoice_line_ids.filtered(lambda line: line.tax_ids == t)
    #             sgst = sum(line.mapped('sgst_perc'))
    #             cgst = sum(line.mapped('cgst_perc'))
    #             igst = sum(line.mapped('igst_perc'))
    #             non_tax_tot = sum(line.mapped('price_unit'))
    #             tax_tot = sum(line.mapped('price_subtotal'))
    #     return res

    # def button_draft(self):
    #     res = super(AccountMoveReport, self).button_draft()
    #     for w in self.invoice_line_ids:
    #         w.igst_perc = 0.00
    #         w.igst_amount = 0.00
    #         w.sgst_perc = 0.00
    #         w.cgst_perc = 0.00
    #         w.sgst_amount = 0.00
    #         w.cgst_amount = 0.00
    #     return res

    @api.onchange('ship_state')
    def _onchange_ship_state(self):
        for rec in self:
            if rec.ship_state:
                rec.ship_st_code = rec.ship_state


class AccountMoveReportLine(models.Model):
    _inherit = 'account.move.line'

    discount_amount = fields.Float(string='Discount Amount')
    sgst_perc = fields.Float(string='SGST', compute='_compute_line_tax_values', store=True, copy=False)
    cgst_perc = fields.Float(string='CGST', compute='_compute_line_tax_values', store=True, copy=False)
    igst_perc = fields.Float(string='IGST', compute='_compute_line_tax_values', store=True, copy=False)
    cess = fields.Float(string='CESS', compute='_compute_line_tax_values', store=True, copy=False)

    sgst_amount = fields.Float(string='sgst amount', compute='_compute_line_tax_values', store=True, copy=False)
    cgst_amount = fields.Float(string='cgst amount', compute='_compute_line_tax_values', store=True, copy=False)
    igst_amount = fields.Float(string='igst amount', compute='_compute_line_tax_values', store=True, copy=False)
    cess_amount = fields.Float(string='cess amount', compute='_compute_line_tax_values', store=True, copy=False)
    convert_inr_amount = fields.Float(string='Convert Amount', store=True)

    @api.depends('tax_ids', 'product_id')
    def _compute_line_tax_values(self):
        for i in self:
            # if i.move_id.move_type == 'out_invoice':
            if i.tax_ids:
                if len(i.tax_ids) == 1:
                    if i.tax_ids.amount != 0:
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
        # else:
        #     i.cess = False
        #     i.cess_amount = False
        #     i.sgst_perc = False
        #     i.sgst_amount = False
        #     i.cgst_perc = False
        #     i.cgst_amount = False
        #     i.igst_perc = False
        #     i.igst_amount = False

    # @api.depends('price_subtotal', 'tax_ids')
    # def _compute_line_tax_values(self):
    #     for i in self:
    #         if len(i.tax_ids) == 1:
    #             print("hii")
    #             if i.tax_ids.tax_group_id.name == 'SGST':
    #                 i.sgst_perc = (i.price_subtotal * i.tax_ids.amount) / 100
    #                 i.sgst_amount = i.tax_ids.amount
    #
    #             if i.tax_ids.tax_group_id.name == 'CGST':
    #                 i.cgst_perc = (i.price_subtotal * i.tax_ids.amount) / 100
    #                 i.cgst_amount = i.tax_ids.amount
    #
    #             if i.tax_ids.tax_group_id.name == 'IGST':
    #                 i.igst_perc = (i.price_subtotal * i.tax_ids.amount) / 100
    #                 i.igst_amount = i.tax_ids.amount
    #
    #             if i.tax_ids.tax_group_id.name == 'Cess':
    #                 i.cess_perc = (i.price_subtotal * i.tax_ids.amount) / 100
    #                 i.cess_amount = i.tax_ids.amount

    @api.onchange('discount', 'price_unit', 'quantity')
    def onchange_discount_amount(self):
        if self.discount:
            disc = (self.discount * (self.price_unit * self.quantity)) / 100
            self.discount_amount = disc


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


class SaleOrderConfirm(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super(SaleOrderConfirm, self).action_confirm()
        for i in self.order_line:
            if len(i.tax_id) > 1:
                raise ValidationError(_('Single Tax value should be given'))
        return res

# class ProductQR(models.Model):
#     _inherit = "account.move"
#     qr_code = fields.Binary("QR Code", attachment=True, store=True)
#
#     @api.onchange('default_code')
#     def generate_qr_code(self):
#         qr = qrcode.QRCode(
#             version=1,
#             error_correction=qrcode.constants.ERROR_CORRECT_L,
#             box_size=10,
#             border=4,
#         )
#         qr.add_data(self.default_code)
#         qr.make(fit=True)
#         img = qr.make_image()
#         temp = BytesIO()
#         img.save(temp, format="PNG")
#         qr_image = base64.b64encode(temp.getvalue())
#         self.qr_code = qr_image
