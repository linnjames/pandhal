# -*- coding: utf-8 -*-
{
    "name": "Quick Sale Order To Purchase Order",
    "author": "Divergent Catalist pvt ltd",
    "category": "Purchases",
    "website": "www.catalisterp.com/",
    "summary": """Quick Sale Order To Purchase Order""",
    "description": """This module is useful for creating purchase orders from the sale order directly.""",
    "version": "14.1",
    "depends": [
        "base",
        "sale_management",
        "purchase",
        "indent",
        "purchase_sale_intercompany",
    ],
    "application": True,
    "data": [
        "security/ir.model.access.csv",
        # "security/record_rule.xml",
        "views/sale_view.xml",
        "views/purchase_view.xml",
        # "views/preferred_vendor_list.xml",
        "views/res_company_views.xml",
        "wizard/purchase_order_wizard.xml",
    ],
    "auto_install": False,
    "installable": True,
}
