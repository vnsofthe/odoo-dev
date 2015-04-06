# -*- coding: utf-8 -*-
#
{
    'name': 'only_single_user',
    'version': '0.1',
    'category': 'web',
    'sequence': 23,
    'summary': 'Only single user login',
    'description': """
Only single user login，other session is logout for this id when user login.
    """,
    'author': 'VnSoft',
    'website': 'http://blog.csdn.net/vnsoft',
    # 'images': ['images/Sale_order_line_to_invoice.jpeg','images/sale_order.jpeg','images/sales_analysis.jpeg'],
    'depends': ['base', 'web',],
    'data': ["data.xml"],
    "qweb":[],
    'demo': [],
    'test': [],
    'js': [ ],
    'installable': True,
    'auto_install': False,
    'application': False,
}