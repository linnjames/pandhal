{
    "name": "Asset Issuance",
    "summary": """Asset Issuance""",
    "sequence": 1,
    "depends": ['base', 'account', 'contacts', 'purchase', 'stock', 'hr', 'hr_holidays'],
    "data": [
        'security/ir.model.access.csv',
        'wizard/asset_wizard_form.xml',
        'views/asset_issuance.xml',

    ],
    "demo": [],
    "application": True,
    "installable": True,
    "auto_install": False,

}
