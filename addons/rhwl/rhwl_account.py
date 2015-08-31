# -*- coding: utf-8 -*-
from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp import tools, api
import datetime
import logging

_logger = logging.getLogger(__name__)
class vnsoft_account(osv.osv):
    _inherit = "account.invoice"

    _columns={
        "page_inv_no":fields.char(u"纸质发票号"),
    }

class rhwl_material(osv.osv):
    _name = "rhwl.material.cost"
    _rec_name = "date"

    def _check_date(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context=context)
        if obj.date.split("-")[-1]!='01':
            return False
        return True

    _columns={
        "date":fields.date("Cost Date",required=True),
        "user_id":fields.many2one("res.users",string="User",readonly=True),
        "compute_date":fields.datetime("Compute Time",readonly=True),
        "state":fields.selection([("draft","Draft"),("done","Done")],string="State"),
        "line":fields.one2many("rhwl.material.cost.line","parent_id",string="Detail")
    }
    _defaults={
        "user_id":lambda obj,cr,uid,context:uid,
        "state":"draft"
    }
    _sql_constraints = [
        ('rhwl_material_cost_uniq', 'unique(date)', u'成本日期不能重复!'),
    ]
    _constraints = [
        (_check_date, u'成本日期只能是每月的1号。', ['date']),
    ]

    def action_confirm(self,cr,uid,ids,context=None):
        obj = self.browse(cr,uid,ids,context=context)

        #删除原有的期初数据
        old_ids = self.pool.get("rhwl.material.cost.line").search(cr,uid,[("parent_id","=",obj.id)],context=context)
        if old_ids:
            self.pool.get("rhwl.material.cost.line").unlink(cr,uid,old_ids)
        #删除原有的出入库数据
        old_ids = self.pool.get("stock.move").search(cr,SUPERUSER_ID,[("cost_mark","=",obj.id)])
        if old_ids:
            self.pool.get("stock.move").write(cr,SUPERUSER_ID,old_ids,{"cost_mark":0})

        #处理期初
        begin_id = self.search(cr,uid,[("date","<",obj.date),("state","in",["done","draft"])],order="date desc",limit=1,context=context)
        if begin_id:
            begin_obj = self.browse(cr,uid,begin_id,context=context)
            for d in begin_obj.line:
                if d.data_kind != "end" or (d.qty==0 and d.amount==0):continue
                val={
                    "parent_id":obj.id,
                    "data_kind":"begin",
                    "product_id":d.product_id.id,
                    "qty":d.qty,
                    "price":d.price,
                    "amount":d.amount
                }
                self.pool.get("rhwl.material.cost.line").create(cr,uid,val,context=context)
        #处理本期采购入库
        supplier_location_id = self.pool.get("stock.location").search(cr,SUPERUSER_ID,[("usage","=","supplier")],context=context)
        production_location_id = self.pool.get("stock.location").search(cr,SUPERUSER_ID,[("usage","=","production")],context=context)
        period_ids = self.pool.get("account.period").search(cr,SUPERUSER_ID,[("date_stop",">=",obj.date),("date_start","<=",obj.date),("special","=",False)],context=context)
        period_obj = self.pool.get("account.period").browse(cr,SUPERUSER_ID,period_ids,context=context)
        #取得会计期间所有已收到的供应商发票资料。
        invoice_ids = self.pool.get("account.invoice").search(cr,SUPERUSER_ID,[("state","not in",["draft","cancel"]),("period_id","in",period_ids),('type','=','in_invoice')],context=context)
        invoice_line_ids = self.pool.get("account.invoice.line").search(cr,SUPERUSER_ID,[("invoice_id","in",invoice_ids)],context=context)
        purchase_line_ids = self.pool.get("purchase.order.line").search(cr,SUPERUSER_ID,[("invoice_lines","in",invoice_line_ids)],context=context)
        move_ids = self.pool.get("stock.move").search(cr,SUPERUSER_ID,[("location_id","=",supplier_location_id[0]),("purchase_line_id","in",purchase_line_ids),("cost_mark","=",0)],context=context)

        if move_ids:
            for i in self.pool.get("stock.move").browse(cr,SUPERUSER_ID,move_ids,context=context):
                val={
                    "parent_id":obj.id,
                    "data_kind":"this",
                    "product_id":i.product_id.id,
                    "qty":i.product_qty,
                    "price":i.price_unit,
                    "amount":i.product_qty *i.price_unit ,
                    "move_type":"in"
                }
                self.pool.get("rhwl.material.cost.line").create(cr,uid,val,context=context)
            #已经作过入库的资料进行标识
            self.pool.get("stock.move").write(cr,SUPERUSER_ID,move_ids,{"cost_mark":obj.id},context=context)
        #领料统计
        picking_ids=[]
        request_ids = self.pool.get("rhwl.library.request").search(cr,SUPERUSER_ID,[("date","<=",period_obj.date_stop),("state","=","done")],context=context)
        for i in request_ids:
            request_obj = self.pool.get("rhwl.library.request").browse(cr,SUPERUSER_ID,i,context=context)
            picking_ids_1 = self.pool.get("stock.picking").search(cr,SUPERUSER_ID,[("origin","=",request_obj.name)],context=context)
            if picking_ids_1:
                picking_ids = picking_ids + picking_ids_1

        consump_ids = self.pool.get("rhwl.library.consump").search(cr,SUPERUSER_ID,[("date","<=",period_obj.date_stop),("state","=","done")],context=context)
        for i in consump_ids:
            consump_obj = self.pool.get("rhwl.library.consump").browse(cr,SUPERUSER_ID,i,context=context)
            picking_ids_2 = self.pool.get("stock.picking").search(cr,SUPERUSER_ID,[("origin","=",consump_obj.name)],context=context)
            if picking_ids_2:
                picking_ids = picking_ids + picking_ids_2

        for p in self.pool.get("stock.picking").browse(cr,SUPERUSER_ID,picking_ids,context=context):
            move_ids = self.pool.get("stock.move").search(cr,SUPERUSER_ID,[("location_dest_id","in",production_location_id),("picking_id","=",p.id),("state","=","done"),("cost_mark","=",0)],context=context)

            for m in self.pool.get("stock.move").browse(cr,SUPERUSER_ID,move_ids,context=context):
                #检查领用出库单对应的采购是否已经确认发票
                p_ids=[]
                for q in m.quant_ids:
                    for h in q.history_ids:
                        if h.location_id.id==supplier_location_id[0] and h.purchase_line_id != False and h.state=="done":
                            p_ids.append(h.purchase_line_id.id)
                if p_ids:
                    il_ids=[]

                    for l in self.pool.get("purchase.order.line").browse(cr,SUPERUSER_ID,p_ids,context=context):
                        if not l.invoice_lines.id:
                            il_ids=[]
                            break
                        for il in l.invoice_lines:
                            il_ids.append(il.id)
                    if il_ids:
                        if self.pool.get("account.invoice.line").search_count(cr,SUPERUSER_ID,[("id","in",il_ids),("invoice_id.state","in",["draft","cancel"])],context=context)>0:
                            continue
                    else:
                        continue

                for mq in m.quant_ids:
                    val={
                        "parent_id":obj.id,
                        "data_kind":"this",
                        "product_id":mq.product_id.id,
                        "qty":mq.qty,
                        "price":mq.cost,
                        "amount":mq.qty *mq.cost ,
                        "move_type":"out",
                        "project":p.project.id,
                        "is_rd":p.is_rd
                    }
                    self.pool.get("rhwl.material.cost.line").create(cr,uid,val,context=context)
                self.pool.get("stock.move").write(cr,SUPERUSER_ID,m.id,{"cost_mark":obj.id},context=context)

        #期末结算
        begin_detail_ids = self.pool.get("rhwl.material.cost.line").search(cr,uid,[("parent_id","=",obj.id),("data_kind","=","begin")],context=context)
        this_detail_ids = self.pool.get("rhwl.material.cost.line").search(cr,uid,[("parent_id","=",obj.id),("data_kind","=","this")],context=context)
        for b in self.pool.get("rhwl.material.cost.line").browse(cr,uid,begin_detail_ids,context=context):
            temp_ids = self.pool.get("rhwl.material.cost.line").search(cr,uid,[("parent_id","=",obj.id),("data_kind","=","this"),("product_id","=",b.product_id.id),("price","=",b.price)],context=context)
            v={"qty":0,"amt":0}
            for t in self.pool.get("rhwl.material.cost.line").browse(cr,uid,temp_ids,context=context):
                if t.move_type=="in":
                    v["qty"] += t.qty
                    v["amt"] += t.amount
                elif t.move_type=="out":
                    v["qty"] -= t.qty
                    v["amt"] -= t.amount
                this_detail_ids.remove(t.id)
            val={
                "parent_id":obj.id,
                "data_kind":"end",
                "product_id":b.product_id.id,
                "qty":b.qty + v["qty"],
                "price":b.price,
                "amount":b.amount + v["amt"]
            }
            self.pool.get("rhwl.material.cost.line").create(cr,uid,val,context=context)
        #处理有本期，没有期初的资料。
        if this_detail_ids:
            v={}
            for t in self.pool.get("rhwl.material.cost.line").browse(cr,uid,this_detail_ids,context=context):
                if not v.has_key(t.product_id.id):
                    v[t.product_id.id]={}
                if not v[t.product_id.id].has_key(t.price):
                    v[t.product_id.id][t.price]={"qty":0,"amt":0}
                if t.move_type=="in":
                    v[t.product_id.id][t.price]["qty"] = v[t.product_id.id][t.price]["qty"] + t.qty
                    v[t.product_id.id][t.price]["amt"] = v[t.product_id.id][t.price]["amt"] + t.amount
                elif t.move_type=="out":
                    v[t.product_id.id][t.price]["qty"] = v[t.product_id.id][t.price]["qty"] - t.qty
                    v[t.product_id.id][t.price]["amt"] = v[t.product_id.id][t.price]["amt"] - t.amount
            for k1,v1 in v.items():
                for k2,v2 in v1.items():
                    val={
                        "parent_id":obj.id,
                        "data_kind":"end",
                        "product_id":k1,
                        "qty":v2["qty"],
                        "price":k2,
                        "amount":v2["amt"]
                    }
                    self.pool.get("rhwl.material.cost.line").create(cr,uid,val,context=context)

        #更新计算时间
        self.write(cr,uid,obj.id,{"compute_date":fields.datetime.now()},context=context)
        pass

    def _get_data_dict(self,cr,uid,id,context=None):
        data={}
        project_count = []
        obj = self.browse(cr,uid,id,context=context)
        for i in obj.line:
            project_id = i.project and i.project.id or 0
            if not data.has_key(i.product_id.categ_id.parent_id.id):
                data[i.product_id.categ_id.parent_id.id]={}
            if not data[i.product_id.categ_id.parent_id.id].has_key(i.product_id.categ_id.id):
                data[i.product_id.categ_id.parent_id.id][i.product_id.categ_id.id]={}
            if not data[i.product_id.categ_id.parent_id.id][i.product_id.categ_id.id].has_key(i.product_id.id):
                data[i.product_id.categ_id.parent_id.id][i.product_id.categ_id.id][i.product_id.id]={}
            if not data[i.product_id.categ_id.parent_id.id][i.product_id.categ_id.id][i.product_id.id].has_key(i.price):
                data[i.product_id.categ_id.parent_id.id][i.product_id.categ_id.id][i.product_id.id][i.price]={}
            if not data[i.product_id.categ_id.parent_id.id][i.product_id.categ_id.id][i.product_id.id][i.price].has_key("begin"):
                data[i.product_id.categ_id.parent_id.id][i.product_id.categ_id.id][i.product_id.id][i.price]["begin"]=[]
            if not data[i.product_id.categ_id.parent_id.id][i.product_id.categ_id.id][i.product_id.id][i.price].has_key("end"):
                data[i.product_id.categ_id.parent_id.id][i.product_id.categ_id.id][i.product_id.id][i.price]["end"]=[]
            if not data[i.product_id.categ_id.parent_id.id][i.product_id.categ_id.id][i.product_id.id][i.price].has_key("this"):
                data[i.product_id.categ_id.parent_id.id][i.product_id.categ_id.id][i.product_id.id][i.price]["this"]={"in":[],"out":{}}

            if i.data_kind in ("begin","end"):
                data[i.product_id.categ_id.parent_id.id][i.product_id.categ_id.id][i.product_id.id][i.price][i.data_kind].append(i.id)
            if i.data_kind=="this" and i.move_type=="in":
                data[i.product_id.categ_id.parent_id.id][i.product_id.categ_id.id][i.product_id.id][i.price]["this"]["in"].append(i.id)
            if i.data_kind=="this" and i.move_type=="out":
                if not data[i.product_id.categ_id.parent_id.id][i.product_id.categ_id.id][i.product_id.id][i.price]["this"]["out"].has_key(project_id):
                    data[i.product_id.categ_id.parent_id.id][i.product_id.categ_id.id][i.product_id.id][i.price]["this"]["out"][project_id]=[]
                if project_count.count(project_id) == 0:project_count.append(project_id)
                data[i.product_id.categ_id.parent_id.id][i.product_id.categ_id.id][i.product_id.id][i.price]["this"]["out"][project_id].append(i.id)
        return len(project_count),data

class rhwl_material_line(osv.osv):
    _name="rhwl.material.cost.line"
    _columns={
        "parent_id":fields.many2one("rhwl.material.cost","Parent",ondelete="cascade"),
        "data_kind":fields.selection([("begin","Begin"),("this","This"),("end","End")],string="Data Kind"),
        "product_id":fields.many2one("product.product","Product",required=True),
        "brand":fields.related("product_id","brand",type="char",string=u"品牌",readonly=True),
        "default_code":fields.related("product_id","default_code",type="char",string=u"货号",readonly=True),
        "attribute":fields.related("product_id","attribute_value_ids",obj="product.attribute.value", type="many2many",string=u"规格",readonly=True),
        "uom_id":fields.related("product_id","uom_id",type="many2one",obj="product.uom",string="Unit",readonly=True),
        "qty":fields.float("Qty",digits_compute=dp.get_precision('Product Unit of Measure'),required=True,),
        'price': fields.float('Price',digits_compute= dp.get_precision('Product Price'),),
        "project":fields.many2one("res.company.project","Project"),
        "is_rd":fields.boolean("R&D"),
        'amount': fields.float("Amt", digits_compute=dp.get_precision('Account')),
        "move_type":fields.selection([('in','in'),('out','out')],string="Move Type")
    }