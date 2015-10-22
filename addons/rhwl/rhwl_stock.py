# coding=utf-8

from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
import datetime
import openerp
import logging

_logger = logging.getLogger(__name__)
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
        "cost_mark":fields.integer("Cost Mark"),
    }
    _defaults={
        "cost_mark":0
    }

    def force_assign(self, cr, uid, ids, context=None):
        if uid==SUPERUSER_ID:
            return super(rhwl_move,self).force_assign(cr,uid,ids,context=context)
        else:
            raise osv.except_osv("Waring",u"当前作业帐号不允许强制可用功能。")

class rhwl_warehouse_orderpoint(osv.osv):
    _inherit = "stock.warehouse.orderpoint"
    _columns={
        "min_work_days":fields.integer(u"安全用量天数"),
    }

    def compute_all_orderpoint(self,cr,uid,context=None):
        ids = self.search(cr,uid,[("min_work_days",">",0)],context=context)
        self.compute_orderpoint(cr,uid,ids,context=context)

    def compute_product_orderpoint(self,cr,uid,id,context=None):
        ids = self.search(cr,uid,[("product_id","=",id)],context=context)
        self.compute_orderpoint(cr,uid,ids,context=context)

    def compute_orderpoint(self,cr,uid,id,context=None):
        if isinstance(id,(long,int)):
            id=[id,]
        for o in self.browse(cr,uid,id,context=context):
            res=self.onchange_min_work_days(cr,uid,o.id,o.min_work_days,o.product_id.id,context=context)
            if res['value'].has_key("product_min_qty"):
                self.write(cr,uid,o.id,res['value'],context=context)

    def onchange_min_work_days(self, cr, uid, ids, days,product_id, context=None):
        if (not days) or days==0:return {"value":{}}
        if not product_id:return {"value":{}}

        comp = self.pool.get("res.company").browse(cr,uid,[1,],context=context)

        if not comp.project_id:
            return {"value":{}}
        #统计每个项目的月检测数量
        comp_qty={}
        for c in comp.project_id:
            comp_qty[c.id]=c.month_qty

        obj = self.pool.get("product.product").browse(cr,uid,product_id,context)
        if not obj.project_ids:
            return {"value":{}} #产品没有针对项目的耗用量，则不能计算安全库存

        #统计产品针对每个项目的耗用量
        pro_qty={}
        for p in obj.project_ids:
            pro_qty[p.project_id.id]=p.sample_count

        vals={"product_min_qty":0,"product_max_qty":0}
        for i in pro_qty.keys():
            if not comp_qty.has_key(i):continue
            vals={
               "product_min_qty": comp_qty[i]/30.0 * days / pro_qty[i] + vals["product_min_qty"],
             }
        vals["product_min_qty"] = round(vals["product_min_qty"])
        vals["product_max_qty"] = round(vals["product_min_qty"]/days * (days+15))

        return {"value":vals}

class rhwl_order(osv.osv):
    _inherit = "procurement.order"

    def run_scheduler(self, cr, uid, use_new_cursor=False, company_id=False, context=None):
        super(rhwl_order,self).run_scheduler(cr,uid,use_new_cursor,company_id,context)
        try:
            if use_new_cursor:
                cr = openerp.registry(cr.dbname).cursor()
            move_obj = self.pool.get("stock.move")#('warehouse_id','=',1),('rule_id','>',0),
            move_ids = move_obj.search(cr,uid,[('state','not in',['done','cancel']),('express_no','=',False)],context=context)
            _logger.info(move_ids)
            for i in move_obj.browse(cr,uid,move_ids,context=context):
                _logger.info(i.product_id.default_code)
                if not (i.product_id.default_code and i.product_id.default_code==u"P001"):continue
                if not i.move_dest_id:continue
                dest = move_obj.browse(cr,uid,i.move_dest_id.id,context=context)

                if dest.procurement_id and dest.procurement_id.warehouse_id and dest.procurement_id.warehouse_id.id>1 and dest.rule_id:
                    data = {
                        "receiv_real_qty":i.product_uos_qty,
                        "product_qty":i.product_uos_qty,
                        "deliver_user":self.pool.get("res.partner").get_Contact_person_user(cr,SUPERUSER_ID,1,context),
                        "deliver_addr":self.pool.get("res.partner").get_detail_address(cr,SUPERUSER_ID,1,context),
                        "deliver_partner":1,
                        "receiv_partner":dest.procurement_id.warehouse_id.partner_id.id,
                        "product_id":i.product_id.id,
                        "receiv_user":self.pool.get("res.partner").get_Contact_person_user(cr,SUPERUSER_ID,dest.procurement_id.warehouse_id.partner_id.id,context),
                        "receiv_addr":self.pool.get("res.partner").get_detail_address(cr,SUPERUSER_ID,dest.procurement_id.warehouse_id.partner_id.id,context),
                    }
                    _logger.info(data)
                    expressID = self.pool.get("stock.picking.express").create(cr,uid,data,context=context)
                    move_obj.write(cr,uid,[i.id,dest.id],{'express_no':expressID})
            if use_new_cursor:
                cr.commit()
        finally:
            if use_new_cursor:
                try:
                    cr.close()
                except Exception:
                    pass
        return {}

class stock_quant(osv.osv):
    _inherit="stock.quant"

    def write(self,cr,uid,ids,val,context=None):
        res = super(stock_quant,self).write(cr,uid,ids,val,context=context)
        if val.has_key("cost"):
            move_ids = []
            for i in self.browse(cr,SUPERUSER_ID,ids,context=context):
                for j in i.history_ids:
                    move_ids.append(j.id)
            move_ids = self.pool.get("stock.move").search(cr,SUPERUSER_ID,[("id","in",move_ids)])
            self.pool.get("stock.move").write(cr,SUPERUSER_ID,move_ids,{"price_unit":val.get("cost")},context=context)
        return res

class stock_picking(osv.osv):
    _inherit="stock.picking"
    _columns={
        "cost_mark":fields.integer("Cost Mark"),
    }
    _defaults={
        "cost_mark":0,
    }