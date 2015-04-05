# -*- coding: utf-8 -*-
#
{
    'name': 'vnsoft03',
    'version': '0.1',
    'category': 'web',
    'sequence': 23,
    'summary': 'Only single user login',
    'description': """
一个帐号只允许一次登录，当前帐号登录时，清除该帐号下其它客户的session.
    """,
    'author': 'VnSoft',
    'website': 'http://blog.csdn.net/vnsoft',
    # 'images': ['images/Sale_order_line_to_invoice.jpeg','images/sale_order.jpeg','images/sales_analysis.jpeg'],
    'depends': ['base', 'web','vnsoft_base',],
    'data': ["vnsoft03.xml"],
    "qweb":[],
    'demo': [],
    'test': [],
    'js': [ ],
    'installable': True,
    'auto_install': False,
    'application': False,
}