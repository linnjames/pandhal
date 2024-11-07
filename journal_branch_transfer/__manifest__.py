{
    'name': 'Inter Company Journal Transfer',
    'version': '14.0.1.0.0',
    'summary': 'This module is used for create journal in multiple company.',
    'sequence': 8,
    'description': """This module is used for create journal in multiple company.""",
    'category': 'Accounting',
    'website': 'https://www.catalisterp.com/',
    'depends': ['base', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/account_account_views.xml',
        'views/res_company_view.xml',
        'views/journal_branch_transfer_view.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,

}
