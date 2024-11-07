# -*- coding: utf-8 -*-
{
    'name': 'Catalist Centrum',
    'version': '14.0.1.0.0',
    'summary': 'Customer Management System',
    'description': """
Customer Management System
==========================
Customer Support System
""",
    'category': 'Industries',
    'website': 'https://www.catalisterp.com',
    'depends': [
        'base', 'mail', 'website', 'base_vat', 'l10n_in', 'account', 'stock'
    ],
    'data': [
        'security/res_groups_data.xml',
        'security/record_rules.xml',
        'security/ir.model.access.csv',
        'data/mail_templates.xml',
        'data/sequence.xml',
        'data/case_type_default.xml',
        'views/support_center_views.xml',
        'views/res_partner_inherit.xml',
        'views/portal_template.xml',
        'wizard/ticket_reschedule_wizard.xml',
        'report/support_center_pivot_report.xml',

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
