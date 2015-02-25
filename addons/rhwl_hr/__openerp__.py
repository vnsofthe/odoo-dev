# -*- coding: utf-8 -*-

{
    'name': 'rhwl_hr',
    'version': '0.1',
    'category': 'HR',
    'sequence': 16,
    'summary': '人和未来人力资源管理',
    'description': """
人和未来生物科技(长沙)有限公司
==================================
人力资源管理增强模块
    """,
    'author': 'VnSoft',
    'website': 'https://www.odoo.com/page/crm',
    # 'images': ['images/Sale_order_line_to_invoice.jpeg','images/sale_order.jpeg','images/sales_analysis.jpeg'],
    'depends': ['hr', 'hr_holidays','vnsoft_base'],
    'data': [  "rhwl_view_hr.xml", ],
    "qweb":[],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}