# -*- coding: utf-8 -*-
{
    'name': 'vnsoft stock',
    'version': '0.1',
    'category': 'stock',
    'sequence': 80,
    'summary': 'Stock In/Out Search',
    'description': """
库存进出状况查询
==================================
    """,
    'author': 'VnSoft',
    'website': 'http://blog.csdn.net/vnsoft',
    # 'images': ['images/Sale_order_line_to_invoice.jpeg','images/sale_order.jpeg','images/sales_analysis.jpeg'],
    'depends': ['base',"vnsoft_base"],
    'data': ["vnsoft06.xml","security/ir.model.access.csv"],
    "qweb":[],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}