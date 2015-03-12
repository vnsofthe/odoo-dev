# -*- coding: utf-8 -*-
{
    'name': 'vnsoft020',
    'version': '0.1',
    'category': 'sale',
    'sequence': 20,
    'summary': '根据销售订单手工产生采购单',
    'description': """
手工生成采购订单
==================================
1.指定销售订单产品明细的来源采购供应商，生成对应的采购订单。
    """,
    'author': 'VnSoft',
    'website': 'http://blog.csdn.net/vnsoft',
    # 'images': ['images/Sale_order_line_to_invoice.jpeg','images/sale_order.jpeg','images/sales_analysis.jpeg'],
    'depends': ['base','vnsoft_base', 'sale','purchase'],
    'data': ["view_sale.xml"],
    "qweb":[],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}