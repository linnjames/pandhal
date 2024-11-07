{
    'name' : 'Sale Advance Payment',
    'category': 'Sales',
    'version': '14.0.1.0',
    "author": "Divergent Catalist Pvt Ltd",
    "website": "www.catalisterp.com/",
    'description': """
        This Module allows to create Customers Advance payment from Sales order.
        * Allow user to manage the Customers Advance payment for the Sales order.
        * Manage with Multi Company & Multi Currency.
    """,
    'summary': """create Customers Advance payment from Sales order.advance payment | sale payment | advance sale payment | sale order payment register payment from sale order register payment from so register payment from sales order advance payment sale""",
    'depends' : ['base', 'sale_management'],
    'price': 10,
    'license': 'OPL-1',
    'data': [
        'views/sale_view.xml',
    ],
    'demo': [],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
}
