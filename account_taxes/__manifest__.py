{
    "name": "TCS and TDS Management",
    "summary": """TCS and TDS  Management""",
    "category": "Accounting",
    "version": "1.1.1",
    "sequence": 1,
    "depends": ['account', 'contacts', 'purchase', 'stock', 'base'],
    "data": [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/account_journal.xml',
        'data/date_cron.xml',
        'wizard/warning_wizard.xml',
        'wizard/tds_report.xml',
        # 'views/account_journal.xml',
        'views/res_config_settings_view.xml',
        'views/account_move_view.xml',
        'views/tcs_management.xml',
        'views/tds_management.xml',
        # 'views/action_manager.xml',
        'views/res_partner_inherit.xml',
        # 'report/report.xml',
    ],

    'qweb': [
        'views/action_manager.xml',
    ],

    'js': [
        'static/src/js/action_manager.js',
    ],

    "demo": [],
    "application": True,
    "installable": True,
    "auto_install": False,
    # "pre_init_hook": "pre_init_check",
}
