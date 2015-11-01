# -*- coding: utf-8 -*-

{
    'name': 'rhwl_web_material',
    'version': '0.1',
    'category': 'CRM',
    'sequence': 19,
    'summary': 'RHWL微信物料领用申请',
    'description': """
人和未来生物科技(长沙)有限公司
==================================
RHWL微信物料领用申请
    """,
    'author': 'VnSoft',
    'website': 'https://www.odoo.com/page/crm',
    # 'images': ['images/Sale_order_line_to_invoice.jpeg','images/sale_order.jpeg','images/sales_analysis.jpeg'],
    'depends': ['web','vnsoft_base','rhwl_weixin'],
    'data': ["material_seq.xml","material.xml"],
    "qweb":[],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}