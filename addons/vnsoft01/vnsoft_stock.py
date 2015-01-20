# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
import datetime

class vnsof_stock_change(osv.osv):
    _name = "stock.change"
    _description = "库存产品拆分"

    _columns = {
        "product_from":fields.many2one("product.product","Product From",required=True),
        "from_qty":fields.float("Qty of From",digits_compute=dp.get_precision('Product Unit of Measure'),required=True),
        "product_to":fields.many2one("product.product","Product To",required=True),
        "to_qty":fields.float("Qty of To",digits_compute=dp.get_precision('Product Unit of Measure'),required=True),
        "date":fields.date("Date"),
        "user_id":fields.many2one("res.users","User",readonly=True),
        "state":fields.selection([("draft","Draft"),("done","Done"),("cancel","Cancel")],"State"),
    }
    _defaults={
        "state":"draft",
        "date":fields.date.today,
        "user_id":lambda obj,cr,uid,context:uid
    }