
{
    'name': "KOT Print ",
    'summary': """
        Kitchen order print """,
    'description': """
This module is used for sending KOT to the network printers    """,
    'author': 'Divergent Catalist ERP Solutions',
    'company': 'Divergent Catalist ERP Solutions',
    'maintainer': 'Divergent Catalist ERP Solutions',
    'website': 'https://www.catalisterp.com/',
    'category': 'Point of Sale',
    'version': '16.0.1.0.0',
    'depends': ['base', 'point_of_sale'],
    'data': [
            'views/pos_printer.xml',
            # 'views/templates.xml',
            # 'views/pos_config.xml',
            'security/ir.model.access.csv',
            'security/security.xml',
        ],
    'assets': {
        'point_of_sale.assets': [
            'kitchen_order_print/static/src/js/clear_button.js',
            # 'pos_delete_orderline/static/src/js/clear_order_line.js',
            'kitchen_order_print/static/src/xml/clear_button.xml',
            'kitchen_order_print/static/src/xml/clear_order_line.xml',
        ],

    },
    'images': ['static/description/banner.png'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,

}
