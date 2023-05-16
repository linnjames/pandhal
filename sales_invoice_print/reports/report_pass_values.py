from odoo import models, _
from odoo.exceptions import Warning


class SalesInvoicePrintReport(models.AbstractModel):
    _name = 'report.sales_invoice_print.record_sales_invoice_report_print'

    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name(
            'sales_invoice_print.record_sales_invoice_report_print')
        obj = self.env[report.model].browse(docids)
        for record in obj:
            record.einv_qr_generate()
            if record.state == 'draft':
                raise Warning(_("Not Available In Draft Stage"))
        for l in obj.invoice_line_ids:
            l._compute_line_tax_values()
        # for f in obj:
        #     if f.show_fssai == True:
        #         for line in f.invoice_line_ids:
        #             if line.product_id and line.product_id.categ_id:
        #                 if line.product_id.categ_id.product_fssai == False:
        #                     raise Warning(_("Tick FSSAI In Product Category : %s", line.product_id.categ_id.name))
        return {
            'docs': obj,
        }


class SalesInvoicePrintMultipleReport(models.AbstractModel):
    _name = 'report.sales_invoice_print.report_sales_invoice_template'

    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name(
            'sales_invoice_print.report_sales_invoice_template')
        obj = self.env[report.model].browse(docids)
        for record in obj:
            record.einv_qr_generate()
            if record.state == 'draft':
                raise Warning(_("Not Available In Draft Stage"))
        for l in obj.invoice_line_ids:
            l._compute_line_tax_values()
        # for f in obj:
        #     if f.show_fssai == True:
        #         for line in f.invoice_line_ids:
        #             if line.product_id and line.product_id.categ_id:
        #                 if line.product_id.categ_id.product_fssai == False:
        #                     raise Warning(_("Tick FSSAI In Product Category : %s", line.product_id.categ_id.name))
        return {
            'docs': obj,
        }


class SalesInvoiceExportLocalInvoice(models.AbstractModel):
    _name = 'report.sales_invoice_print.report_export_local_invoice'

    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name(
            'sales_invoice_print.report_export_local_invoice')
        obj = self.env[report.model].browse(docids)
        for record in obj:
            record.einv_qr_generate()
            record._compute_total_amount_in_words()
            if record.state == 'draft':
                raise Warning(_("Not Available In Draft Stage"))
        for l in obj.invoice_line_ids:
            l._compute_line_tax_values()
        # for f in obj:
        #     if f.show_fssai == True:
        #         for line in f.invoice_line_ids:
        #             if line.product_id and line.product_id.categ_id:
        #                 if line.product_id.categ_id.product_fssai == False:
        #                     raise Warning(_("Tick FSSAI In Product Category : %s", line.product_id.categ_id.name))
        return {
            'docs': obj,
        }
