# -*- coding: utf-8 -*-
from odoo import models, api, _


class MultiScrapXlsx(models.AbstractModel):
    _name = 'report.multi_scrap_orders.multi_scrap_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, line):
        format1 = workbook.add_format(
            {'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'bold': True, 'border': 5, })
        sheet = workbook.add_worksheet('MultiScrapXlsx')
        sheet.set_column('A:A', 40)
        sheet.set_column('B:B', 18)
        sheet.set_column('C:C', 18)
        sheet.set_column('D:D', 18)
        sheet.set_column('E:E', 27)
        row = 0
        col = 0

        sheet.write(0, 0, 'Product Name', format1)
        format2 = workbook.add_format(
            {'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'bold': True, 'border': 5, })
        sheet.write(0, 1, 'Today Inward Qty', format2)
        format3 = workbook.add_format(
            {'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'bold': True, 'border': 5, })
        sheet.write(0, 2, 'Scrap Qty', format3)
        format4 = workbook.add_format(
            {'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'bold': True, 'border': 5, })
        sheet.write(0, 3, 'Closing Stock', format4)
        format4 = workbook.add_format(
            {'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'bold': True, 'border': 5, })
        sheet.write(0, 4, 'Reason', format4)

        val = self.env['stock.picking'].search([('scheduled_date', '=', line.date)])

        self._cr.execute(('''SELECT pt.name,sp.scheduled_date, pt.id , sum(sml.qty_done)
                       FROM stock_picking sp
                       left join stock_move sm on sp.id = sm.picking_id
                       left join stock_move_line sml on sp.id = sml.picking_id
                       left join product_product pp on sm.product_id = pp.id
                       left join product_template pt on pp.product_tmpl_id = pt.id
                       left join multi_scrap_line msl on pt.id = msl.product_id
                       left join stock_quant sq on pt.id = sq.product_id
						where sp.scheduled_date between '%s' and '%s'
						group by(pt.id,sp.scheduled_date)
                       ''') % (line['date'].strftime('%Y-%m-%d 00:00:00'), line['date'].strftime('%Y-%m-%d 23:59:59')))
        move = self.env.cr.dictfetchall()
        for i in move:
            i['reason'] = ''
            i['quantity'] = 0
            products = self.env['product.template'].search([('id', '=', i['id'])])
            i['qty_avilable'] = products.qty_available
        self._cr.execute(('''SELECT  pt.name, pt.id,ir.res as reason,msl.quantity, ms.expected_date
                                FROM multi_scrap_line msl
                                left join product_product pp on msl.product_id = pp.id
                                left join product_template pt on pp.product_tmpl_id = pt.id
                                left join inventory_reason ir on msl.reason = ir.id
								left join multi_scrap ms on msl.multi_scarp_id = ms.id
 								where ms.expected_date between '%s' and '%s' ''') % (
        line['date'].strftime('%Y-%m-%d 00:00:00'), line['date'].strftime('%Y-%m-%d 23:59:59')))
        moves = self.env.cr.dictfetchall()
        for j in moves:
            j['sum'] = 0
            j['qty_avilable'] = 0
        mo = move + moves
        for inv in mo:
            row += 1
            sheet.write(row + 1, col, inv['name'])
            sheet.write(row + 1, col + 1, inv['sum'])
            sheet.write(row + 1, col + 2, inv['quantity'])
            sheet.write(row + 1, col + 3, inv['qty_avilable'])
            sheet.write(row + 1, col + 4, inv['reason'])
        # count = 2
        # for inv in val.move_ids_without_package:
        #     print(val.move_ids_without_package,'vvvvvvv')
        #     sheet.write(count, 0, inv.product_id.name, format1)
        #     count = count + 1

        # core = self.search([('expected_date', '=', line.date)])
        # print(core,'45454545454545454545454')
        # counts = 2
        # for j in core.operation_ids:
        #     print(core.operation_ids,'lllll')
        #     sheet.write(count, 0, j.product_id.name, format1)
        #     count = count + 1

        # @api.onchange('expected_date')
        # def _onchange_day(self):
        #     val = self.env['stock.picking'].search([('scheduled_date','=',self.expected_date)])
        #     print(val,'prithvi')
        #     line = []
        #     for j in val.move_ids_without_package:
        #         print(j,'ppppppppp')
        #         line.append((0,0,{
        #             'product_id': j.product_id.id,
        #             'quantity': j.quantity_done,
        #             'product_uom_id': j.product_uom.id,
        #         }))
        #     self.write({'operation_ids': line})

        #     master_head = workbook.add_format({'font_size': 11, 'bg_color': '#b3c6ff', 'align': 'center',
        #                                        'valign': 'vcenter', 'bold': True, 'border': 1,})
        #     master_head.set_font_name('Times New Roman')
        #     b2b_head = workbook.add_format({'font_size': 11, 'align': 'vcenter', 'font_color': 'white',
        #                                     'border': 1, 'bg_color': '#007acc', 'bold': True})
        #     b2b_head.set_font_name('Times New Roman')
        #     amt_head = workbook.add_format({'font_size': 11, 'align': 'right', 'font_color': 'white',
        #                                     'valign': 'vcenter', 'border': 1, 'bg_color': '#007acc', 'bold': True})
        #     amt_head.set_font_name('Times New Roman')
        #     center_head = workbook.add_format({'font_size': 11, 'align': 'center', 'font_color': 'white',
        #                                        'valign': 'vcenter', 'border': 1, 'bg_color': '#007acc', 'bold': True})
        #     center_head.set_font_name('Times New Roman')
        #     b2b_body = workbook.add_format({'font_size': 11, 'align': 'vcenter',
        #                                     'valign': 'vcenter', 'bg_color': '#ecc6c6', 'border': 1})
        #     b2b_body.set_font_name('Times New Roman')
        #     amt_body = workbook.add_format({'font_size': 11, 'align': 'right',
        #                                     'valign': 'vcenter', 'bg_color': '#ecc6c6', 'border': 1})
        #     amt_body.set_font_name('Times New Roman')
        #     center_body = workbook.add_format({'font_size': 11, 'align': 'center',
        #                                        'valign': 'vcenter', 'bg_color': '#ecc6c6', 'border': 1})
        #     center_body.set_font_name('Times New Roman')
        #     format3 = workbook.add_format({'font_size': 10, 'valign': 'vcenter'})
        #     format3.set_font_name('Times New Roman')
        #     center_format3 = workbook.add_format({'font_size': 10, 'align': 'center', 'valign': 'vcenter'})
        #     center_format3.set_font_name('Times New Roman')
        #     total_amt = workbook.add_format({'font_size': 10, 'valign': 'vcenter', 'border': 1})
        #     total_amt.set_font_name('Times New Roman')
        #     total_no = workbook.add_format({'font_size': 10, 'align': 'center', 'valign': 'vcenter', 'border': 1})
        #     total_no.set_font_name('Times New Roman')
        #     # sheet
        #     sheet = workbook.add_worksheet(str(object.date_from) + ' - ' + str(object.date_to))
        #
        #     inv_ids = self.env['account.move'].search([('move_type', 'in', ['in_invoice', 'in_refund'])])
        #     inv_id = self.env['account.move.line'].search([('date', '>=', object.date_from),
        #                                                    ('date', '<=', object.date_to),
        #                                                    ('parent_state', '=', 'posted'),
        #                                                    ('move_id', 'in', inv_ids.ids),
        #                                                    ('product_uom_id', '!=', False)], order='date asc, move_name')
        #
        #     taxes = inv_id.search([('tax_group_id', '!=', False),
        #                            ('date', '>=', object.date_from),
        #                            ('date', '<=', object.date_to),
        #                            ('parent_state', '=', 'posted'),
        #                            ('product_id', '!=', False),
        #                            ('move_id', 'in', inv_ids.ids),
        #                            ])
        #     print('inv_id', inv_id)
        #
        #     row = []
        #     for inv in inv_id:
        #
        #         if (inv.tax_ids == inv.tax_ids) and (inv.move_id == inv.move_id):
        #             if inv.move_id.move_type == 'in_refund':
        #                 tp = 'PURCHASE RETURN'
        #             else:
        #                 tp = 'PURCHASE INVOICE'
        #             row.append({'data': {
        #                 'tax': inv.tax_ids.name,
        #                 'in_type': tp,
        #                 'ref': inv.move_id.ref,
        #                 'inv_name': inv.move_id.name,
        #                 'customer_name': inv.partner_id.name,
        #                 # 'hsn': inv.product_hsn_code,
        #                 'inv_date': str(inv.move_id.invoice_date),
        #                 'gst_no': inv.move_id.l10n_in_gstin,
        #                 # 'gst_type': inv.move_id.l10n_in_gst_treatment,
        #                 'state': inv.move_id.l10n_in_state_id.state_code
        #             }})
        #         print('row', row)
        #     no_dup = []
        #     for i in row:
        #         if i['data'] not in no_dup:
        #             no_dup.append(i['data'])
        #     print('no_dup', no_dup)
        #
        #     inv_final = []
        #     for v in no_dup:
        #         tax = v['tax']
        #         inv_name = v['inv_name']
        #         price_total = 0
        #         price_subtotal = 0
        #         qty = 0
        #         for i in inv_id:
        #             if (i.move_id.name == inv_name) and (i.tax_ids.name == tax):
        #                 if i.move_id.move_type == 'in_refund':
        #                     qty += - i.quantity
        #                     price_total += - i.price_total
        #                     price_subtotal += - i.price_subtotal
        #                 else:
        #                     qty += i.quantity
        #                     price_total += i.price_total
        #                     price_subtotal += i.price_subtotal
        #         inv_final.append({
        #             'tax': tax,
        #             'inv_name': inv_name,
        #             'inv_date': v['inv_date'],
        #             'gst_no': v['gst_no'],
        #             'ref': v['ref'],
        #             'state': v['state'],
        #             'customer_name': v['customer_name'],
        #             'in_type': v['in_type'],
        #             'price_total': price_total,
        #             'price_subtotal': price_subtotal,
        #             'qty': qty,
        #         })
        #
        #
        #     sheet.write(0, 0, 'GST Purchase Report', center_head)
        #     sheet.write(1, 0, '', center_head)
        #     sheet.write(1, 1, '', centersheet.set_column_head)
        #     sheet.write(1, 2, '', b2b_head)
        #     sheet.write(1, 3, '', amt_head)
        #     sheet.write(1, 4, '', b2b_head)
        #     sheet.write(1, 5, '', b2b_head)
        #     sheet.write(1, 6, '', b2b_head)
        #     sheet.write(1, 7, '', b2b_head)
        #     sheet.write(1, 8, 'Total Taxable Value', amt_head)
        #     sheet.write(1, 9, '', b2b_head)
        #     sheet.write(1, 10, 'Total SGST', amt_head)
        #     sheet.write(1, 11, 'Total CGST', amt_head)
        #     sheet.write(1, 12, 'Total IGST', amt_head)
        #     sheet.write(1, 13, 'Total Tax Amount', amt_head)
        #     sheet.write(1, 14, 'Total Net Amount', amt_head)
        #
        #     sheet.write('E3', '', total_amt)
        #     sheet.write('F3', '', total_amt)
        #     sheet.write('G3', '', total_amt)
        #     sheet.write('H3', '', total_amt)
        #     sheet.write('I3', '', total_amt)
        #
        #     sheet.set_column('A:A', 24)
        #     sheet.write(3, 0, 'Invoice Type', center_body)
        #     count = 4
        #     for inv in inv_final:
        #         in_type = inv['in_type']
        #         sheet.write(count, 0, in_type, center_format3)
        #         count = count + 1
        #
        #     sheet.set_column('B:B', 24)
        #     sheet.write(3, 1, 'VchrNo', center_body)
        #     count = 4
        #     for inv in inv_final:
        #         inv_name = inv['inv_name']
        #         sheet.write(count, 1, inv_name, center_format3)
        #         count = count + 1
        #
        #     sheet.set_column('C:C', 21)
        #     sheet.write(3, 2, 'Bill Date', center_body)
        #     count = 4
        #     for inv in inv_final:
        #         inv_date = inv['inv_date']
        #         sheet.write(count, 2, inv_date, center_format3)
        #         count = count + 1
        #
        #     sheet.set_column('D:D', 24)
        #     sheet.write(3, 3, 'Bill No', center_body)
        #     count = 4
        #     for inv in inv_final:
        #         ref = inv['ref']
        #         sheet.write(count, 3, ref, center_format3)
        #         count = count + 1
        #
        #     sheet.set_column('E:E', 24)
        #     sheet.write(3, 4, 'Vendor VATRegNo', center_body)
        #     count = 4
        #     for inv in inv_final:
        #         gst_no = inv['gst_no']
        #         sheet.write(count, 4, gst_no, center_format3)
        #         count = count + 1
        #
        #     sheet.set_column('F:F', 24)
        #     sheet.write(3, 5, 'AcName', center_body)
        #     count = 4
        #     for inv in inv_final:
        #         customer_name = inv['customer_name']
        #         sheet.write(count, 5, customer_name, center_format3)
        #         count = count + 1
        #
        #     sheet.set_column('G:G', 18)
        #     sheet.write(3, 6, 'StateCode', center_body)
        #     count = 4
        #     for inv in inv_final:
        #         state = inv['state']
        #         sheet.write(count, 6, state, center_format3)
        #         count = count + 1
        #     sheet.set_column('H:H', 14)
        #     sheet.write(3, 7, 'Qty', center_body)
        #     count = 4
        #     for inv in inv_final:
        #         qty = inv['qty']
        #         sheet.write(count, 7, qty, center_format3)
        #         count = count + 1
        #
        #     sheet.set_column('I:I', 21)
        #     sheet.write(3, 8, 'Taxable Amount', center_body)
        #     count = 4
        #     total_subtotal = 0
        #     for inv in inv_final:
        #         price_subtotal = inv['price_subtotal']
        #         sheet.write(count, 8, price_subtotal, format3)
        #         count = count + 1
        #         total_subtotal += price_subtotal
        #     sheet.write(2, 8, total_subtotal, total_amt)
        #
        #     sheet.set_column('J:J', 21)
        #     sheet.write(3, 9, 'Tax %', center_body)
        #     count = 4
        #     for inv in inv_final:
        #         tax = inv['tax']
        #         sheet.write(count, 9, tax, center_format3)
        #         count = count + 1
        #     sheet.set_column('K:K', 21)
        #
        #     sheet.write(3, 10, 'SGST Amount', center_body)
        ##
        # self._cr.execute(('''SELECT pt.name , sum(sml.qty_done)
        #         FROM stock_picking sp
        #         left join stock_move sm on sp.id = sm.picking_id
        #         left join stock_move_line sml on sp.id = sml.picking_id
        #         left join product_product pp on sm.product_id = pp.id
        #         left join product_template pt on pp.product_tmpl_id = pt.id
        #         left join multi_scrap_line msl on pt.id = msl.product_id
        #         left join stock_quant sq on pt.id = sq.product_id
        #         group by(pt.name)
        #         '''))
        # # where
        # # sp.scheduled_date
        # # between
        # # '%s' and '%s'
        # move = self.env.cr.dictfetchall()
        # print(move)
        # print('//////////////////////////////////////////////////////////')
        # self._cr.execute(('''SELECT  pt.name,msl.reason,msl.quantity
        #                         FROM multi_scrap_line msl
        #                         left join product_product pp on msl.product_id = pp.id
        #                         left join product_template pt on pp.product_tmpl_id = pt.id'''))
        # # where
        # # create_date
        # # between
        # # '%s' and '%s
        # moves = self.env.cr.dictfetchall()
        # print(moves, 'move')
        # mo = move + moves
        # print('////////////////////////////////////////////////////////////////////////////////////')
        # print(mo)
        # for inv in move:
        #     sheet.write(row + 1, col, inv['name'])
        #     sheet.write(row + 1, col + 1, inv['sum'])
        # for inv in moves:
        #     sheet.write(row + 1, col, inv['name'])
        #     sheet.write(row + 1, col + 2, inv['reason'])
        #     sheet.write(row + 1, col + 3, inv['quantity'])

# taxes_sgst = self._cr.dictfetchall()
#     ##
#
#     count = 4
#     s_lst = []
#     sgst_total = 0
#     for tax_total in taxes_sgst:
#         s_lst.append(tax_total['total'])
#         sgst_total += tax_total['total']
#         sheet.write(count, 10, tax_total['total'], format3)
#         count = count + 1
#     sheet.write(2, 10, sgst_total, total_amt)
#
#     sheet.set_column('L:L', 21)
#     sheet.write(3, 11, 'CGST Amount', center_body)
#
#
# for v in inv_final:
#     tax = v['tax']
#     inv_name = v['inv_name']
#     cgst_price = 0
#     for i in taxes:
#         if (i.move_id.name == inv_name) and \
#                 (i.tax_group_id.name == 'CGST'):
#             if i.move_id.move_type == 'in_refund':
#                 cgst_price += - i.price_total
#             else:
#                 cgst_price += i.price_total
#             # sheet.write(count, 11, cgst_price, format3)
#         # else:
#         # sheet.write(count, 11, cgst_price, format3)
#     # cgst_total += cgst_price
#     # count = count + 1
#     # sheet.write(2, 11, cgst_total, total_amt)
#     ##
#     self._cr.execute(('''SELECT account_move_line.move_id, account_move_line.tax_line_id,account_move_line.tax_group_id, account_move_line.move_name,
#                     account_move_line.date,
#                     sum(price_total) as total, account_tax.name, account_tax_group.name as nm
#                     FROM public.account_move_line
#                     Inner join account_tax on account_tax.id = account_move_line.tax_line_id
#                     Inner join account_tax_group on account_tax_group.id = account_move_line.tax_group_id
#                     Inner join account_move on account_move.id = account_move_line.move_id
#                     where account_move_line.tax_line_id != 0 and account_move_line.date BETWEEN '%s' AND '%s'
#                     and account_move.move_type in ('in_invoice', 'in_refund') and account_tax_group.name = 'CGST'
#                     and account_move_line.parent_state = 'posted'
#                     group by account_move_line.move_name, account_move_line.tax_line_id, account_tax_group.name,
#                     account_move_line.tax_group_id, account_tax.name, account_move_line.date,
#                     account_move_line.move_id
#                     ORDER BY move_name,tax_group_id ASC;
#                     ''') % (object.date_from, object.date_to))
#     taxes_cgst = self._cr.dictfetchall()
#     ##
#     count = 4
#     c_lst = []
#     cgst_total = 0
#     for tax_total in taxes_cgst:
#         c_lst.append(tax_total['total'])
#         cgst_total += tax_total['total']
#         sheet.write(count, 11, tax_total['total'], format3)
#         count = count + 1
#     sheet.write(2, 11, cgst_total, total_amt)
#
#     sheet.set_column('M:M', 21)
#     sheet.write(3, 12, 'IGST Amount', center_body)
#     self._cr.execute(('''SELECT account_move_line.move_id, account_move_line.tax_line_id,account_move_line.tax_group_id, account_move_line.move_name,
#                     account_move_line.date,
#                     sum(price_total) as total, account_tax.name, account_tax_group.name as nm
#                     FROM public.account_move_line
#                     Inner join account_tax on account_tax.id = account_move_line.tax_line_id
#                     Inner join account_tax_group on account_tax_group.id = account_move_line.tax_group_id
#                     Inner join account_move on account_move.id = account_move_line.move_id
#                     where account_move_line.tax_line_id != 0 and account_move_line.date BETWEEN '%s' AND '%s'
#                     and account_move.move_type in ('in_invoice', 'in_refund') and account_tax_group.name = 'IGST'
#                     and account_move_line.parent_state = 'posted'
#                     group by account_move_line.move_name, account_move_line.tax_line_id, account_tax_group.name,
#                     account_move_line.tax_group_id, account_tax.name, account_move_line.date,
#                     account_move_line.move_id
#                     ORDER BY move_name,tax_group_id ASC;
#                     ''') % (object.date_from, object.date_to))
#     taxes_igst = self._cr.dictfetchall()
#     ##
#     count = 4
#     i_lst = []
#     igst_total = 0
#     for tax_total in taxes_igst:
#         i_lst.append(tax_total['total'])
#         igst_total += tax_total['total']
#         sheet.write(count, 12, tax_total['total'], format3)
#         count = count + 1
#     sheet.write(2, 12, igst_total, total_amt)
#
#     sheet.set_column('N:N', 21)
#     sheet.write(3, 13, 'Tax Amount', center_body)
#     count = 4
#     total_tax = 0
#     for i in range(len(c_lst)):
#         # if i_lst[i]:
#         #     tax_sum = s_lst[i] + c_lst[i] + i_lst[i]
#         # else:
#         tax_sum = s_lst[i] + c_lst[i]
#         sheet.write(count, 13, tax_sum, format3)
#         count = count + 1
#         total_tax += tax_sum
#     sheet.write(2, 13, total_tax, total_amt)
#
#
#     # count = 4
#     # total_tax = 0
#     # for v in inv_final:
#     #     tax = v['tax']
#     #     inv_name = v['inv_name']
#     #     sgst = 0
#     #     cgst = 0
#     #     igst = 0
#     #     total_tx = 0
#     #     for i in taxes:
#     #         if (i.move_id.name == inv_name) and \
#     #                 (i.tax_group_id.name == 'SGST'):
#     #             if i.move_id.move_type == 'in_refund':
#     #                 sgst += - i.price_total
#     #             else:
#     #                 sgst += i.price_total
#     #             # cgst_total += cgst_price
#     #         if (i.move_id.name == inv_name) and \
#     #                 (i.tax_group_id.name == 'CGST'):
#     #             if i.move_id.move_type == 'in_refund':
#     #                 cgst += - i.price_total
#     #             else:
#     #                 cgst += i.price_total
#     #         if (i.move_id.name == inv_name) and \
#     #                 (i.tax_group_id.name == 'IGST'):
#     #             if i.move_id.move_type == 'in_refund':
#     #                 igst += - i.price_total
#     #             else:
#     #                 igst += i.price_total
#     #         total_tx = sgst + cgst + igst
#     #         # sheet.write(count, 13, total_tx, format3)
#     #     total_tax += total_tx
#     #     count = count + 1
#     # # sheet.write(2, 13, total_tax, total_amt)
#
#     sheet.set_column('O:O', 21)
#     sheet.write(3, 14, 'Net Amount', center_body)
#     count = 4
#     total_price = 0
#     for inv in inv_final:
#         price_total = inv['price_total']
#         sheet.write(count, 14, price_total, format3)
#         count = count + 1
#         total_price += price_total
#     sheet.write(2, 14, total_price, total_amt)
