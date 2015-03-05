# -*- coding: utf-8 -*-
#巫老师
{
    'name': 'vnsoft01',
    'version': '0.1',
    'category': 'account',
    'sequence': 15,
    'summary': '二次开发业务增强',
    'description': """
Odoo 二次开发
==================================
1.物料基本资料属性增强
2.销售订单、发票增加课题组，下单人员属性
3.增加库存产品拆包功能
    """,
    'author': 'VnSoft',
    'website': 'https://www.odoo.com/page/crm',
    # 'images': ['images/Sale_order_line_to_invoice.jpeg','images/sale_order.jpeg','images/sales_analysis.jpeg'],
    'depends': ['base', 'vnsoft_base','sale','purchase','account',"auth_crypt"],
    'data': ["vnsoft_view_product.xml",
                "vnsoft_view_sale.xml",
                "vnsoft_view_account.xml",
                "vnsoft_view_stock.xml",
                "vnsoft_view_purchase.xml",
                "vnsoft_sequence.xml"],
    "qweb":[],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}