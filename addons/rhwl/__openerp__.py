# -*- coding: utf-8 -*-

{
    'name': 'rhwl',
    'version': '0.1',
    'category': 'CRM',
    'sequence': 15,
    'summary': '人和未来业务',
    'description': """
人和未来生物科技(长沙)有限公司
==================================
CRM业务增加模块
    """,
    'author': 'VnSoft',
    'website': 'https://www.odoo.com/page/crm',
    # 'images': ['images/Sale_order_line_to_invoice.jpeg','images/sale_order.jpeg','images/sales_analysis.jpeg'],
    'depends': ['vnsoft_base','sale', 'stock', 'purchase','l10n_cn_express_track','hr','purchase_requisition'],
    'data': ['security/rhwl_security.xml',
             'security/ir.model.access.csv',
             "rhwl_view_partner.xml",
             "rhwl_view_express.xml",
             "rhwl_view_sample.xml",
             "rhwl_view_stock.xml",
             "rhwl_view_product.xml",
             "rhwl_project.xml",
             "rhwl_report.xml",
             "views/report_sample_one.xml",
             "views/rhwl.xml",
             "report/rhwl_sample_one.xml",
             "rhwl_view_company.xml",
             "rhwl_sample_import.xml",
             "rhwl_view_account.xml",
             "views/purchase_apply_sequence.xml",
             "views/rhwl_view_purchase.xml",
             "views/purchase_requisition.xml",
             "views/rhwl_sample_express.xml",
             "views/rhwl_menu.xml",
             "wizard/export_excel.xml"
    ],
    "qweb":["static/src/xml/base.xml"],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}