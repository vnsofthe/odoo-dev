# -*- coding: utf-8 -*-

{
    'name': 'rhwl',
    'version': '0.1',
    'category': 'CRM',
    'sequence': 15,
    'summary': '人和未来业务',
    'description': """
人和未来生物科技(长沙)有限公司
==================================
CRM业务增加模块
    """,
    'author': 'VnSoft',
    'website': 'https://www.odoo.com/page/crm',
    # 'images': ['images/Sale_order_line_to_invoice.jpeg','images/sale_order.jpeg','images/sales_analysis.jpeg'],
    'depends': ['hr', 'sale', 'stock', 'purchase','l10n_cn_express_track'],
    'data': ["rhwl_view_hr.xml",
             "rhwl_view_partner.xml",
             "rhwl_view_express.xml",
             "rhwl_view_sample.xml",
             "rhwl_view_stock.xml",
             'security/ir.model.access.csv',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}