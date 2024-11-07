{
    'name': "Custom POS Receipt",
    "description": """POS Receipt with Customer Details and Invoice Details""",
    "summary": "POS Receipt with Customer Details and Invoice Details",
    "category": "Point of Sale",
    "version": "16.0.1.0.0",
    'author': 'Divergent Catalist ERP Solutions',
    'company': 'Divergent Catalist ERP Solutions',
    'maintainer': 'Divergent Catalist ERP Solutions',
    'website': 'https://www.catalisterp.com/',
    'depends': ['base','point_of_sale','sales_invoice_print'],
    'data': [
        # 'views/res_config_settings.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_custom_receipt/static/src/xml/OrderReceipt.xml',
            'pos_custom_receipt/static/src/js/load_cust_fields.js',
            # 'pos_receipt_extend/static/src/js/payment.js',
        ]
    },
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
