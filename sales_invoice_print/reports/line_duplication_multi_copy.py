from odoo import models, _
from odoo.exceptions import ValidationError, Warning


class ReportSalesInvoice(models.AbstractModel):
    _name = 'report.sales_invoice_print.report_sales_invoice_template'

    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name(
            'sales_invoice_print.report_sales_invoice_template')
        obj = self.env[report.model].browse(docids)
        for record in obj.invoice_line_ids:
            if len(record.tax_ids) > 1:
                raise Warning(_("Single Tax Value Should Be Given"))
        rows = []
        lens = []
        for i in obj.invoice_line_ids:
            if i.product_id:
                rows.append({
                    'acc_inv_id': i.move_id.id,
                    'product_id': i.product_id.id,
                    'product_label': i.name,
                    'hsn_code': i.product_id.l10n_in_hsn_code,
                    'unit': i.product_id.uom_id.name,
                    'quantity': i.quantity,
                    'rate': i.price_unit,
                    'taxable_value': i.price_subtotal,
                    'tax': i.tax_ids.id,
                    'tax_name': i.tax_ids.name,
                    'total': i.price_total,
                    'dis_amount': i.discount_amount,
                    'name_pro': i.product_id.name,
                })
                lens.append({'data': {
                    'acc_inv_id': i.move_id.id,
                    'product_id': i.product_id.id,
                    'tax': i.tax_ids.id,
                }})

        no_dup = []
        for j in lens:
            if j['data'] not in no_dup:
                no_dup.append(j['data'])

        #
        inv = []
        for v in no_dup:
            prod_id = v['product_id']
            t_id = v['tax']
            a_id = v['acc_inv_id']
            prod_name = ''
            hsn = ''
            unt = ''
            qty = 0
            rte = 0
            t_value = 0
            tot = 0
            dis = 0
            t_name = ''
            for t in rows:
                if t['product_id'] == prod_id and t['tax'] == t_id and t['acc_inv_id'] == a_id:
                    # product_with_num = t['product_label'].split("]")
                    prod_name = t['name_pro']
                    hsn = t['hsn_code']
                    unt = t['unit']
                    qty += t['quantity']
                    rte = t['rate']
                    t_value += t['taxable_value']
                    tot += t['total']
                    dis += t['dis_amount']
                    t_name = t['tax_name']
            inv.append({
                "acc_inv_id": a_id,
                "product_id": prod_id,
                "product_label": prod_name,
                "hsn_code": hsn,
                "unit": unt,
                "quantity": qty,
                "rate": rte,
                "taxable_value": t_value,
                "tax": t_id,
                "total": tot,
                "dis_amount": dis,
                "tax_name": t_name,
            })
        return {
            'docs': obj,
            'values': inv,
        }
