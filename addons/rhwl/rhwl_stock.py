# coding=utf-8

from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
import datetime


class rhwl_stock(osv.osv):
    _inherit = "stock.warehouse"

    def _get_warehouse_qty(self, cr, uid, ids, prop, arg, context=None):
        if isinstance(ids, (list, tuple)) and not len(ids):
            return {}
        if isinstance(ids, (long, int)):
            ids = [ids]
        res = []
        stock_obj = self.browse(cr, uid, ids, context=context)
        for i in stock_obj:
            cr.execute("select sum(qty) from stock_quant where location_id = %s", (i.lot_stock_id.id,))
            qty = 0
            for j in cr.fetchall():
                qty += j[0] and j[0] or 0
            res.append((i.id, qty))

        return dict(res)

    _columns = {
        "qty": fields.function(_get_warehouse_qty, type="float", string=u"库存数量"),
    }