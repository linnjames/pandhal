# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Delivery Note Print',
    'version': '1.1',
    'summary': 'This module used to set master details of equipments gone for service or maintenance.',
    'sequence': -10,
    'description': """This Odoo app helps to set details of equipments gone for service or maintenance.""",
    'category': 'Productivity',
    'author': "Divergent Catalist",
    'website': "https://www.catalisterp.com",
    'depends': ['base','mail','account','contacts', 'sale', 'stock', 'l10n_in', 'purchase'],
    'data': [
        'reports/delivery_out_print_report.xml',
        # 'reports/delivery_out_print_template.xml',
        'reports/delivery_out_trnasfer_template.xml',
        'reports/invoice_delivery_note.xml',
        'reports/invoice_delivery_note_template.xml',

    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}