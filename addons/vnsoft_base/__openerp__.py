# -*- coding: utf-8 -*-
#QQ:3085969661
{
    'name': 'vnsoft base',
    'version': '0.1',
    'category': 'tools',
    'sequence': 99,
    'summary': 'Vnsoft Developer Base Model',
    'description': """
Odoo 二次开发基础工具包
==================================
    """,
    'author': 'VnSoft',
    'website': 'http://blog.csdn.net/vnsoft',
    # 'images': ['images/Sale_order_line_to_invoice.jpeg','images/sale_order.jpeg','images/sales_analysis.jpeg'],
    'depends': ['base', 'web'],
    'data': [],
    "qweb":["static/src/xml/base.xml"],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}