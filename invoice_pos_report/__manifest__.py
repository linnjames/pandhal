# -*- coding: utf-8 -*-
{
    'name': 'Invoice POS Report',
    'version': '14.1',
    'category': 'Accounting',
    'sequence': 10,
    'summary': 'This Module helps to get a report',
    'description': """
      This Module helps to get a report
    """,
    'author': 'Divergent Catalist Pvt Ltd',
    'website': "https://www.catalisterp.com/",
    'depends': ['base', 'account', 'point_of_sale', 'contacts', 'stock'],

    'demo': [],
    'data': [
        'security/ir.model.access.csv',
        # 'security/security.xml',
        'wizard/invoice_pos_reort_wiz_views.xml',
        'views/invoice_pos_report.xml',
        # 'views/product_template_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': [],
    'qweb': [],
}
