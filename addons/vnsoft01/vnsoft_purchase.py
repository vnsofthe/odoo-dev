# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
import datetime

class vnsoft_purchase(osv.osv):
    _inherit = "purchase.order"

    _columns={
        "order_kind":fields.selection([("internal",u"国内"),("export",u"进口"),("export_approve",u"进口审批")],string="Order Kind"),
        "tariff":fields.float('Tariff', digits_compute=dp.get_precision('Product Price')),
    }

