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
CRM业务增加模块:
开发公司检测项目基本资料维护，并可配置各项目每月预估销量，自动计算库存物料安全库存用量。
开发物料采购申请单功能。
开发物料基础资料中各项目标准用量功能，
开发无创项目医院基础资料维护功能，自动配置各销售、代理、医院的物料库存。
开发无创样本信息维护功能，包括信息录入、确认、接收实验结果、重采血、阳性跟踪、短信通知接口等功能。
开发无创样本物流资料维护功能，并与顺丰系统对接，自动产生电子运单，并设计电子运单套打模板。
开发无创样本接收湘雅实验室结果功能。
开发无创样本统计分析图表。
开发探针标准人份用量图表、库存用量可作样本人份图表。
开发无创导出保险信息单Excel功能。
开发无创导出费用结算单Excel功能。
开发无创导出对帐单Excel功能。
开发无创导出实验结果Excel功能。
开发进销存成本月结功能。
开发进销存导出成本计算表Excel功能。
开发进销存导出费用申请单Excel功能。
采购订单确认时，如果明细有指定税，并且是单价中含税，则需要重新计算未税单价到库存移动表中的单价栏位。
采购人员增加探针标准项目人份、探针库存可用项目人份报表(2016/01/12)
开发Odoo与微信订阅号、公众号、企业号的连通功能。
开发微信端无创驻院助手功能，包括样本查询、样本发送、重采血通知、阳性样本查询、物流查询等。
开发微信端无创销量每日上报功能。
微信公众号端无创销售统计分析图表功能。
开发无创、易感、叶酸、耳聋样本统计微信通知功能。
开发无创样本在实验室状态统计微信通知功能。

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
             "report/rhwl_product_rs.xml",
             "rhwl_view_company.xml",
             "rhwl_sample_import.xml",
             "rhwl_view_account.xml",
             "views/purchase_apply_sequence.xml",
             "views/rhwl_view_purchase.xml",
             "views/purchase_requisition.xml",
             "views/rhwl_sample_express.xml",
             "views/rhwl_account.xml",
             "views/rhwl_menu.xml",
             "wizard/export_excel.xml",

    ],
    "qweb":["static/src/xml/base.xml"],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}