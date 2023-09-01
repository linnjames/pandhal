{
    'name': 'Indent Request',
    'version': '14.0.1.0.0',
    'summary': 'Indent Request',
    'author': 'Divergent Catalist ERP Solutions',
    'company': 'Divergent Catalist ERP Solutions',
    'maintainer': 'Divergent Catalist ERP Solutions',
    'sequence': 10,
    'description': """Indent Request""",
    'website': 'https://www.catalisterp.com/',
    'depends': ['base', 'sale', 'sale_management', 'account', 'purchase', 'stock', 'point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/data.xml',
        'wizard/RFQ_cancel_wizard.xml',
        'views/indent_request.xml',
        'views/res_company.xml',
        'views/stock_picking.xml',
        'views/product_privilege.xml',
        'views/purchase_approval.xml',
        'views/sales_indent.xml',
        'views/salesorder_indent.xml',
        'views/sale_purchase_actions.xml',
        # 'views/pos_price_restriction.xml',
    ],
    'demo': [],
    'licenSe': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
