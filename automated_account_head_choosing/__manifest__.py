

{
    'name': 'Automated account head choosing',
    'version': '13.0.1',
    'category': 'Sales',
    'sequence': 2,
    'summary': 'Automated account head choosing',
    'description': """Automated account head choosing
        
    """,
    'author': 'Catalist',
    'depends': ['base', 'sale', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'security/record_rule.xml',
        'data/automated_sequence.xml',
        'views/automated_inventory_valuation_views.xml',
            ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}