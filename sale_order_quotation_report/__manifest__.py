# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Sale Order Quotation Report',
    'version': '14.0.1.0.0',
    'summary': 'Print Sale Order Quotation Report ',
    'author': 'Divergent Catalist ERP Solutions',
    'company': 'Divergent Catalist ERP Solutions',
    'maintainer': 'Divergent Catalist ERP Solutions',
    'sequence': 10,
    'description': """Print Sale Order Quotation Report""",
    'category': 'Sales',
    'website': 'https://www.catalisterp.com/',
    'depends': [],
    'data': [
        'report/sale_order_report_pdf.xml',
        'report/sale_order_report_template.xml',
    ],
    'demo': [],
    'qweb': [],
    'licenSe': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
