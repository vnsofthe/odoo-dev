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

class rhwl_move(osv.osv):
    _inherit = "stock.move"
    _columns={
        "express_no":fields.many2one("stock.picking.express",string=u"快递单"),
    }
class rhwl_order(osv.osv):
    _inherit = "procurement.order"

    def run_scheduler(self, cr, uid, use_new_cursor=False, company_id=False, context=None):
        super(rhwl_order,self).run_scheduler(cr,uid,use_new_cursor,company_id,context)
        move_obj = self.pool.get("stock.move")#('warehouse_id','=',1),('rule_id','>',0),
        move_ids = move_obj.search(cr,uid,[('move_dest_id.id','>',0),('state','not in',['done','cancel']),('express_no','=',False)],context=context)
        print "move_ids:",move_ids
        for i in move_obj.browse(cr,uid,move_ids,context=context):
            dest = move_obj.browse(cr,uid,i.move_dest_id.id,context=context)
            if dest.warehouse_id.id>1 and dest.rule_id:
                data = {
                    "receiv_real_qty":i.product_uos_qty,
                    "product_qty":i.product_uos_qty,
                    "deliver_partner":1,
                    "receiv_partner":dest.warehouse_id.partner_id.id,
                    "product_id":i.product_id.id
                }
                expressID = self.pool.get("stock.picking.express").create(cr,uid,data,context=context)
                move_obj.write(cr,uid,[i.id,dest.id],{'express_no':expressID})
        if use_new_cursor:
            cr.commit()
        return {}