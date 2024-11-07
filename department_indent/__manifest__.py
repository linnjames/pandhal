{
    'name': 'Department Material Request',
    'version': '14.0.1.0.0',
    'summary': 'Department Material Request',
    'author': 'Divergent Catalist ERP Solutions',
    'company': 'Divergent Catalist ERP Solutions',
    'maintainer': 'Divergent Catalist ERP Solutions',
    'sequence': 10,
    'description': """Department Material Request""",
    'website': 'https://www.catalisterp.com/',
    'depends': ['base', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/department_indent_wizard.xml'

    ],
    'demo': [],
    'licenSe': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
