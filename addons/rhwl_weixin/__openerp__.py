# -*- coding: utf-8 -*-

{
    'name': 'rhwl_weixin',
    'version': '0.1',
    'category': 'CRM',
    'sequence': 16,
    'summary': '人和未来微信管理',
    'description': """
人和未来生物科技(长沙)有限公司
==================================
微信管理模块
    """,
    'author': 'VnSoft',
    'website': 'https://www.odoo.com/page/crm',
    # 'images': ['images/Sale_order_line_to_invoice.jpeg','images/sale_order.jpeg','images/sales_analysis.jpeg'],
    'depends': ['rhwl','rhwl_hr','vnsoft_base'],
    'data': [
        "view_weixin_base.xml",
        "view_weixin.xml",
        "view_weixin_menu.xml",
        "view_weixin_htmlmsg.xml"
    ],
    "qweb":[],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}