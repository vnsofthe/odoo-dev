# -*- coding: utf-8 -*-
#QQ:3085969661
{
    'name': 'vnsoft023',
    'version': '0.1',
    'category': 'product',
    'sequence': 15,
    'summary': '产品基本资料',
    'description': """
Odoo 二次开发
==================================
1.产品资料增加品牌属性
    """,
    'author': 'VnSoft',
    'website': 'http://blog.csdn.net/vnsoft',
    # 'images': ['images/Sale_order_line_to_invoice.jpeg','images/sale_order.jpeg','images/sales_analysis.jpeg'],
    'depends': ['base', 'product','web','sale','purchase','stock'],
    'data': ["vnsoft_view_product.xml" ],
    "qweb":["static/src/xml/base.xml"],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}