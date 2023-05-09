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
    'depends': ['base', 'sale', 'account', 'stock', 'sale_management', 'l10n_in', 'account_taxes'],
    'data': [
        'security/ir.model.access.csv',
        'reports/sales_invoice_print_multiple_view.xml',
        'reports/sales_invoice_print_view.xml',
        'reports/sales_invoice_pdf.xml',
        # 'wizards/account_post_wizard_views.xml',
        'wizards/sale_advance_payment_views.xml',
        'wizards/add_product_wiz_views.xml',
        'views/account_move.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
