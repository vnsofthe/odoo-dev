# -*- coding: utf-8 -*-
#
{
    'name': 'vnsoft02',
    'version': '0.1',
    'category': 'web',
    'sequence': 15,
    'summary': 'Modal enable drag',
    'description': """
设置Odoo的弹窗可以通过标题栏进行拖动。
    """,
    'author': 'VnSoft',
    'website': 'http://blog.csdn.net/vnsoft',
    # 'images': ['images/Sale_order_line_to_invoice.jpeg','images/sale_order.jpeg','images/sales_analysis.jpeg'],
    'depends': ['base', 'web','vnsoft_base',],
    'data': ["vnsoft02.xml"],
    "qweb":[],
    'demo': [],
    'test': [],
    'js': [
        'static/src/js/vnsoft02.js',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}