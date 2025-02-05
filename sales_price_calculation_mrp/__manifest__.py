{
    'name': 'MRP wise Sales Price Calculation',
    'version': '13.0.1',
    'category': 'Sales',
    'sequence': 2,
    'summary': 'MRP wise Sales Price Calculation',
    'description': """When Click the Get Sales Price Button then automatically calculate Sales Price
        
    """,
    'author': 'Catalist',
    'depends': ['base', 'sale', 'sale_management', 'account', 'l10n_in', 'stock', 'purchase', 'contacts'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/sales_price_calculation.xml',
        'reports/mrp_updation_report.xml',
        'reports/mrp_updation_template.xml',
        'wizard/multi_sales_price_wizard_view.xml',
        'wizard/mrp.xml',
    ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
