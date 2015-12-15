# -*- coding: utf-8 -*-

{
    'name': 'gbsoft_weixin',
    'version': '0.1',
    'category': 'CRM',
    'sequence': 16,
    'summary': '金豆云微信',
    'description': """
金商信息科技有限公司
==================================
微信管理模块
    """,
    'author': 'VnSoft',
    'website': 'https://www.odoo.com/page/crm',
    # 'images': ['images/Sale_order_line_to_invoice.jpeg','images/sale_order.jpeg','images/sales_analysis.jpeg'],
    'depends': ['web'],
    'data': [
        "view_weixin_base.xml",
        "view_weixin.xml",
        "view_weixin_menu.xml",
        "view_weixin_htmlmsg.xml",
        "security/ir.model.access.csv"
    ],
    "qweb":[],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}