# -*- coding: utf-8 -*-

{
    'name': 'rhwl_ysel',
    'version': '0.1',
    'category': 'CRM',
    'sequence': 18,
    'summary': '叶酸&耳聋项目',
    'description': """
人和未来生物科技(长沙)有限公司
==================================
叶酸、耳聋样本检测资料维护，包括录入、确认、信息反馈、拍照、导入实验结果、生成电子报告、建立发货单等功能。
    """,
    'author': 'VnSoft',
    'website': 'https://www.odoo.com/page/crm',
    # 'images': ['images/Sale_order_line_to_invoice.jpeg','images/sale_order.jpeg','images/sales_analysis.jpeg'],
    'depends': ['vnsoft_base'],
    'data': [ "security/group_security.xml",
              "security/ir.model.access.csv",
              "views/rhwl_ys.xml",
              "views/rhwl_el.xml",
              "wizard/wizard_import.xml",
              "views/rhwl_el_picking.xml",
              "views/rhwl_ys_picking.xml",
              ],
    "qweb":[],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}