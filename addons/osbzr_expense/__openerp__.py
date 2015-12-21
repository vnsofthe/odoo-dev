# -*- coding: utf-8 -*-

{
    "name": "报销单上直接选择付款方式",
    "description":
        """
            原有功能是员工提交报销单，经会计过账后生成会计凭证，记账后针对员工付款，
            此模块增加直接选择付款方式,满足客户报销直接付款不挂账业务模式，生成会计凭证。
        """,
    'author': "jacky@osbzr.com,jason@osbzr.com",
    'website': "http://www.osbzr.com",

    "category": "osbzr",
    "version": "1.0",
    "depends": [
                'hr_expense','base'
                ],
    "data" : [
              'osbzr_expense.xml'
        ],
    'installable': True,
    'application': False,
}