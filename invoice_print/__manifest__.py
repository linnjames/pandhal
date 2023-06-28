# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'invoice_print',
    'version': '16.0.0',
    'summary': 'invoice print',
    'sequence': 1,
    'description': """""",
    'category': 'accunt/invoice_print',
    'website': 'https://www.odoo.com/app/invoicing',
    'depends': ['account'],
    'data': ['reports/invoice_print.xml',
             'reports/invoice_print_template.xml'
             ],
    'demo': [],
    'installable': True,
    'application': True,

}
