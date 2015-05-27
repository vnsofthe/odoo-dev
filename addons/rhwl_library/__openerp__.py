# -*- coding: utf-8 -*-

{
    'name': 'rhwl_library',
    'version': '0.1',
    'category': 'library',
    'sequence': 16,
    'summary': '人和未来实验生产管理',
    'description': """
人和未来生物科技(长沙)有限公司
==================================
实验生产模块
    """,
    'author': 'VnSoft',
    'website': 'https://www.odoo.com/page/crm',
    # 'images': ['images/Sale_order_line_to_invoice.jpeg','images/sale_order.jpeg','images/sales_analysis.jpeg'],
    'depends': ['base', 'web','vnsoft_base',"stock","rhwl"],
    'data': [ "security/ir.model.access.csv"
                ,"view/rhwl_lib.xml"
                ,"view/library_request_sequence.xml"
                ,"wizard/purchase_requisition_group.xml"
                ,"report/report.xml"],
    "qweb":[],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}