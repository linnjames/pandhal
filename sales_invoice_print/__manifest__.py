# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Sales Invoice Print',
    'version': '14.1',
    'summary': 'Report of Sales Invoice',
    'sequence': 1,
    'description': """Report of Sales Invoice""",
    'category': 'Sales',
    "author": "Divergent Catalist pvt ltd",
    "website": "www.catalisterp.com/",
    'depends': ['base', 'sale', 'account', 'stock', 'sale_management', 'l10n_in', 'contacts', 'purchase'],
    'data': [
        'security/ir.model.access.csv',
        'reports/sales_invoice_print_multiple_view.xml',
        'reports/sales_invoice_print_view.xml',
        'reports/sales_invoice_pdf.xml',
        'reports/export_local_invoice_temp.xml',
        'views/account_move.xml',
        # 'views/product_category.xml',
        'views/res_partner.xml',
        'wizard/update_usd_to_inr_wizard_view.xml'
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
