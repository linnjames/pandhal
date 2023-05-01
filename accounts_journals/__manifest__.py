{
    "name": "Account Journals",
    "summary": """Account Journals""",
    "category": "Accounting",
    "sequence": 1,
    "depends": ['base', 'account', 'contacts', 'purchase', 'stock'],
    "data": [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/account_journals.xml'
    ],
    "demo": [],
    "application": True,
    "installable": True,
    "auto_install": False,

}
