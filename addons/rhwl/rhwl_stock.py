# coding=utf-8

from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
import datetime


class rhwl_stock_location(osv.osv):
    _inherit = "stock.location"

    def _fun_get_warehouse(self, cr, uid, ids, prop, arg, context=None):
        locals = self.browse(cr, uid, ids, context=context)
        res = []
        for l in locals:
            wid = super(rhwl_stock_location, self).get_warehouse(cr, uid, l, context=context)
            if wid:
                wh = self.pool.get("stock.warehouse").browse(cr, uid, wid, context=context)
                res.append((l.id, wh and wh.name or False))
            else:
                res.append((l.id, False))

        return dict(res)


    _columns = {
        "warehouse_id": fields.function(_fun_get_warehouse, type="char", string="WareHouse Name"),
    }

