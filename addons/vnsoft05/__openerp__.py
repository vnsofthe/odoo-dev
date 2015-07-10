# -*- coding: utf-8 -*-
#
{
    'name': 'vnsoft05',
    'version': '0.1',
    'category': 'web',
    'sequence': 23,
    'summary': 'WEB',
    'description': """
调整Odoo文件上传组件的最大文件大小。
    """,
    'author': 'VnSoft',
    'website': 'http://blog.csdn.net/vnsoft',
    # 'images': ['images/Sale_order_line_to_invoice.jpeg','images/sale_order.jpeg','images/sales_analysis.jpeg'],
    'depends': ['base', 'web',],
    'data': ["view/vnsoft05.xml"],
    "qweb":[],
    'demo': [],
    'test': [],
    'js': [ ],
    'installable': True,
    'auto_install': False,
    'application': False,
}