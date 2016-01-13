# -*- coding: utf-8 -*-

{
    'name': 'mongo',
    'version': '0.1',
    'category': 'web',
    'sequence': 18,
    'summary': '人和未来业务',
    'description': """
人和未来生物科技(长沙)有限公司
==================================
1.对接分析部门MongoDB数据，开发疾病、性状、用药基础数据维护UI。
2.开发泰济生易感套餐信息检索平台。
    """,
    'author': 'VnSoft',
    'website': 'https://www.odoo.com/page/crm',
    # 'images': ['images/Sale_order_line_to_invoice.jpeg','images/sale_order.jpeg','images/sales_analysis.jpeg'],
    'depends': ['web'],
    'data': ["security/rhwl_security.xml" ],
    "qweb":[],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}