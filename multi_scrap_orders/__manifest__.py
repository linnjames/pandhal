# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Multi Scrap Order',
    'version': '14.0.1.0.0',
    'summary': 'Scrap management software',
    'sequence': 12,
    'description': """Scrap management""",
    'category': 'Productivity/Discuss',
    'website': 'https://www.odoo.com/page/billing',
    'depends': ['base', 'stock', 'daily_product', 'report_xlsx', 'mrp_scrap_customization'],
    'data': [
        'security/ir.model.access.csv',
        'security/record_rule.xml',
        'security/security.xml',
        'data/sequence.xml',
        'wizard/multi_scrap_wizard.xml',
        'views/multi_scrap.xml',
        'views/res_config_settings.xml',
        'views/action_manager.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,

}
