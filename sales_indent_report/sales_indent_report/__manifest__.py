{
    'name': 'Sale Indent Report',
    'version': '1.0',
    'summary': 'Sale Indent Report',
    'sequence': -100,
    'description': """Sale Indent Report""",
    'category': 'productivity',
    'website': 'https://www.odoo.com/app/invoicing',
    'license': 'LGPL-3',
    'depends': ['base', 'stock', 'indent'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/sales_indent_report_wizard.xml',
        'report/report.xml',
        'report/sales_indent_report.xml',
        'views/sales_indent_menu.xml',

    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,

}
