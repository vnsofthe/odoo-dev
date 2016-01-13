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
泰济生易感检测样本维护，包含录入、信息确认、异常反馈、拍照等功能。
泰济生易感检测样本质检结果导入功能。
泰济生易感检测样本位点结果导入功能。
泰济生易感检测样本DNA库存导入功能。
泰济生易感检测样本发货单维护功能。
导出泰济生发货单位点数据Excel功能。
导出泰济生检测样本DNA质检不合格信息、图片功能。
导出泰济生检测样本信息异常样本信息、图片功能。
导出泰济生发货单样本质量检测报告Excel功能。
导出泰济生样本DNA库存记录Excel功能。
导出泰济生拍照图片到文件服务器功能。
泰济生样本实验结果导入、转报告分析、接收电子报告功能。
泰济生样本每周实验进度提醒功能。
泰济生样本电子报告上传泰济生服务器功能。

新易感检测样本维护，包含录入、信息确认、异常反馈、拍照等功能。
新易感检测样本实验结果导入、转报告分析、接收电子报告功能。
新易感检测样本质检结果导入功能。
新易感检测样本位点结果导入功能。
新易感检测样本发货单维护功能。
新易感导出样本信息Excel功能。
导出新易感检测样本DNA质检不合格信息、图片功能。
导出新易感检测样本信息异常样本信息、图片功能。
新易感检测发货单导出Excel功能。
新易感检测套餐基础资料维护功能。
泰济生易感会计对帐资料维护功能。

泰济生易感检测样本片段分析、Sanger测序数据合并、Sanger测序数据判读工具。

    """,
    'author': 'VnSoft',
    'website': 'https://www.odoo.com/page/crm',
    # 'images': ['images/Sale_order_line_to_invoice.jpeg','images/sale_order.jpeg','images/sales_analysis.jpeg'],
    'depends': ['vnsoft_base','base','pentaho_reports'],
    'data': ["security/gene_security.xml",
             "security/ir.model.access.csv",
             "view/rhwl_gene_view.xml",
             "view/rhwl_gene_import.xml",

             "view/rhwl_risk.xml",
             "view/rhwl_gene_picking.xml",
             "view/rhwl_lib.xml",
             "view/rhwl_cron.xml",
             "view/rhwl_report_except.xml",
             "view/rhwl_gene_batch.xml",
             "view/rhwl_export_excel.xml",
             "view/rhwl_gene.xml",
             "view/rhwl_gene_account.xml",
             "view/rhwl_base.xml",
             "view/rhwl_gene_new_view.xml",
             "view/rhwl_gene_new_picking.xml",
             "view/rhwl_stock_dna.xml"
             ],
    "qweb":[],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}