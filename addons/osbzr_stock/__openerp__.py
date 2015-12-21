# -*- coding: utf-8 -*-

{
    "name": "移动时检查输入的产品、库位、批次、包装、数量是否足够",
    "description":
        """
            原有逻辑是在仓库移动产品时输入任意数量的产品（与移库单数量不符合）都可以正常移动通过，
            此模块增加对移动产品数量的逻辑判断，输入移动的产品数量大于移库数量或者大于库存数量应弹出警告阻止程序继续运行。
        """,
    'author': "jacky@osbzr.com",
    'website': "http://www.osbzr.com",

    "category": "osbzr",
    "version": "1.0",
    "depends": [
                'stock',
                ],
    "data":[
        'osbzr_stock_view.xml'
            ],
    'installable': True,
    'application': False,
}
