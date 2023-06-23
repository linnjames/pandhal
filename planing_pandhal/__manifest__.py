{
    'name': 'planning pandhal',
    'version': '14.0.1.0.0',
    'category': 'Production',
    'summary': 'Production planning for Pandhal',
    'author': 'Divergent Catalist ERP Solutions',
    'company': 'Divergent Catalist ERP Solutions',
    'maintainer': 'Divergent Catalist ERP Solutions',
    'website': 'https://www.catalisterp.com/',
    'depends': ['base','mrp', 'stock', 'indent',
                'uom','sale','sale_management'],

    'data': ['security/ir.model.access.csv',
             # 'security/security.xml',
             # 'data/trip_name.xml',
             'data/sequence.xml',
             'report/production_planning_template.xml',
             'report/production_planning.xml',
             'views/planing.xml'],
    'qweb': [],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
