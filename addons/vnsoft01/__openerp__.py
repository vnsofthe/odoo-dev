# -*- coding: utf-8 -*-

{
    'name': 'vnsoft01',
    'version': '0.1',
    'category': 'account',
    'sequence': 15,
    'summary': '二次开发业务增强',
    'description': """
Odoo 二次开发
==================================
1.物料基本资料属性增强
    """,
    'author': 'VnSoft',
    'website': 'https://www.odoo.com/page/crm',
    # 'images': ['images/Sale_order_line_to_invoice.jpeg','images/sale_order.jpeg','images/sales_analysis.jpeg'],
    'depends': ['base', 'product','web'],
    'data': ["vnsoft_view_product.xml" ],
    "qweb":["static/src/xml/base.xml"],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}