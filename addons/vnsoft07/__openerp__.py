# -*- coding: utf-8 -*-
#
{
    'name': 'vnsoft07',
    'version': '0.1',
    'category': 'web',
    'sequence': 15,
    'summary': 'Export for Administrator',
    'description': """
设置只有管理员才可以导出数据。
    """,
    'author': 'VnSoft',
    'website': 'http://blog.csdn.net/vnsoft',
    # 'images': ['images/Sale_order_line_to_invoice.jpeg','images/sale_order.jpeg','images/sales_analysis.jpeg'],
    'depends': ['base', 'web','vnsoft_base',],
    'data': ["vnsoft07.xml"],
    "qweb":[],
    'demo': [],
    'test': [],
    'js': [
        'static/src/js/vnsoft07.js',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}