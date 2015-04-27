# -*- coding: utf-8 -*-

{
    'name': 'rhwl_gene',
    'version': '0.1',
    'category': 'CRM',
    'sequence': 20,
    'summary': '易感基因',
    'description': """
人和未来生物科技(长沙)有限公司
==================================
易感基因业务模块
    """,
    'author': 'VnSoft',
    'website': 'https://www.odoo.com/page/crm',
    # 'images': ['images/Sale_order_line_to_invoice.jpeg','images/sale_order.jpeg','images/sales_analysis.jpeg'],
    'depends': ['vnsoft_base','base','pentaho_reports'],
    'data': ["security/gene_security.xml",
             "security/ir.model.access.csv",
             "view/rhwl_gene_view.xml",
             "view/rhwl_gene_import.xml",
             "report/gene_report.xml",
             "view/rhwl_risk.xml",
             "view/rhwl_gene_picking.xml",
             "view/rhwl_lib.xml"
             ],
    "qweb":[],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}