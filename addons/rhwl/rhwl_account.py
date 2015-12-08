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

    def _get_line_count(self,cr,uid,ids,fields_name,args,context=None):
        res={}
        for i in ids:
            res[i] = self.pool.get("account.invoice.line").search_count(cr,uid,[("invoice_id","=",i)])

        return res

    _columns={
        "page_inv_no":fields.char(u"纸质发票号"),
        "line_count":fields.function(_get_line_count,type="integer",string=u"明细笔数"),
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
        "line":fields.one2many("rhwl.material.cost.line","parent_id",string="Detail"),
        "invoice":fields.boolean(u"统计未到票数据"),
        "inventory":fields.boolean(u"统计盘盈亏数据"),
    }
    _defaults={
        "user_id":lambda obj,cr,uid,context:uid,
        "state":"draft",
        "invoice":True,
        "inventory":False,
    }
    _sql_constraints = [
        ('rhwl_material_cost_uniq', 'unique(date)', u'成本日期不能重复!'),
    ]
    _constraints = [
        (_check_date, u'成本日期只能是每月的1号。', ['date']),
    ]
    month_project={}
    product_project={}
    def action_done(self,cr,uid,ids,context=None):
        self.write(cr,uid,ids,{'state':'done'})

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
        begin_id = self.search(cr,uid,[("date","<",obj.date),("state","in",["done",])],order="date desc",limit=1,context=context)
        if begin_id:
            begin_obj = self.browse(cr,uid,begin_id,context=context)
            val_dict={}
            for d in begin_obj.line:
                if d.data_kind != "end" or (d.qty==0 or d.qty<0):continue
                if val_dict.has_key(d.product_id.id):
                    if val_dict[d.product_id.id].has_key(d.price):
                        val_dict[d.product_id.id][d.price]['qty'] = val_dict[d.product_id.id][d.price]['qty'] + d.qty
                        val_dict[d.product_id.id][d.price]['amount'] = val_dict[d.product_id.id][d.price]['amount'] + d.amount
                    else:
                        val_dict[d.product_id.id][d.price]={
                            "qty":d.qty,
                            "amount":d.amount
                        }
                else:
                    val_dict[d.product_id.id]={}
                    val_dict[d.product_id.id][d.price]={
                        "qty":d.qty,
                        "amount":d.amount
                    }

            for k,v in val_dict.items():
                for k1,v1 in v.items():
                    val={
                        "parent_id":obj.id,
                        "data_kind":"begin",
                        "product_id":k,
                        "qty":v1["qty"],
                        "price":k1,
                        "amount":v1["amount"]
                    }
                    self.pool.get("rhwl.material.cost.line").create(cr,uid,val,context=context)
        #处理本期采购入库
        supplier_location_id = self.pool.get("stock.location").search(cr,SUPERUSER_ID,[("usage","=","supplier")],context=context)
        production_location_id = self.pool.get("stock.location").search(cr,SUPERUSER_ID,[("usage","=","production")],context=context)
        period_ids = self.pool.get("account.period").search(cr,SUPERUSER_ID,[("date_stop",">=",obj.date),("date_start","<=",obj.date),("special","=",False)],context=context)
        period_obj = self.pool.get("account.period").browse(cr,SUPERUSER_ID,period_ids,context=context)
        #取得会计期间所有已收到的供应商发票资料。
        if obj.invoice:
            invoice_ids = self.pool.get("account.invoice").search(cr,SUPERUSER_ID,[("period_id","in",period_ids),('type','=','in_invoice')],context=context)
        else:
            invoice_ids = self.pool.get("account.invoice").search(cr,SUPERUSER_ID,[("state","not in",["draft","cancel"]),("period_id","in",period_ids),('type','=','in_invoice')],context=context)
        invoice_line_ids = self.pool.get("account.invoice.line").search(cr,SUPERUSER_ID,[("invoice_id","in",invoice_ids)],context=context)
        purchase_line_ids = self.pool.get("purchase.order.line").search(cr,SUPERUSER_ID,[("invoice_lines","in",invoice_line_ids),("order_id.state","not in",["draft","cancel","sent","bid","confirmed"])],context=context)
        move_ids = self.pool.get("stock.move").search(cr,SUPERUSER_ID,[("location_id","=",supplier_location_id[0]),("purchase_line_id","in",purchase_line_ids),("cost_mark","=",0),("state","=","done")],context=context)

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

        #处理上月已经接收发票，但本月才入库的库存移动
        move_ids = self.pool.get("stock.move").search(cr,SUPERUSER_ID,[("location_id","=",supplier_location_id[0]),("cost_mark","=",0),("purchase_line_id","!=",False),("date",">=",period_obj.date_start),("date","<=",period_obj.date_stop),("state","=","done")],context=context)
        if move_ids:
            for i in self.pool.get("stock.move").browse(cr,SUPERUSER_ID,move_ids,context=context):
                if not i.purchase_line_id.invoice_lines:continue
                for inv in i.purchase_line_id.invoice_lines:
                    if inv.invoice_id.type=="in_invoice" and inv.invoice_id.state not in ("cancel") and (obj.invoice or (not inv.invoice_id.state in ("draft","cancel"))):
                        if obj.invoice or inv.invoice_id.period_id.date_stop < period_obj.date_start:
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
                            self.pool.get("stock.move").write(cr,SUPERUSER_ID,i.id,{"cost_mark":obj.id},context=context)
                            break

        #处理本期发生的退料，当作本期入库处理
        move_ids = self.pool.get("stock.move").search(cr,SUPERUSER_ID,[("location_id","=",production_location_id[0]),("cost_mark","=",0),("date",">=",period_obj.date_start),("date","<=",period_obj.date_stop),("state","=","done")],context=context)
        if move_ids:
            for i in self.pool.get("stock.move").browse(cr,SUPERUSER_ID,move_ids,context=context):
                if not i.origin_returned_move_id.id:continue
                origin_move = self.pool.get("stock.move").browse(cr,SUPERUSER_ID,i.origin_returned_move_id.id,context=context)
                if origin_move.cost_mark==0:continue
                for mq in i.quant_ids:
                    if mq.qty<0:continue
                    val={
                        "parent_id":obj.id,
                        "data_kind":"this",
                        "product_id":mq.product_id.id,
                        "qty":mq.qty,
                        "price":mq.cost,
                        "amount":mq.qty *mq.cost ,
                        "move_type":"in"
                    }

                    self.pool.get("rhwl.material.cost.line").create(cr,uid,val,context=context)
                    self.pool.get("stock.move").write(cr,SUPERUSER_ID,i.id,{"cost_mark":obj.id},context=context)


        #领料统计
        picking_ids=[]
        request_ids = self.pool.get("rhwl.library.request").search(cr,SUPERUSER_ID,[("date","<=",period_obj.date_stop),("state","=","done")],context=context)
        for i in request_ids:
            request_obj = self.pool.get("rhwl.library.request").browse(cr,SUPERUSER_ID,i,context=context)
            picking_ids_1 = self.pool.get("stock.picking").search(cr,SUPERUSER_ID,[("origin","=",request_obj.name),("state","=","done")],context=context)
            for p in picking_ids_1:
                picking_moves = self.pool.get("stock.move").search_count(cr,SUPERUSER_ID,[("picking_id","=",p),("state","=","done"),("cost_mark","=",0)],context=context)
                if picking_moves>0:
                    picking_ids.append(p)

        consump_ids = self.pool.get("rhwl.library.consump").search(cr,SUPERUSER_ID,[("date","<=",period_obj.date_stop),("state","=","done")],context=context)
        for i in consump_ids:
            consump_obj = self.pool.get("rhwl.library.consump").browse(cr,SUPERUSER_ID,i,context=context)
            picking_ids_2 = self.pool.get("stock.picking").search(cr,SUPERUSER_ID,[("origin","=",consump_obj.name),("state","=","done")],context=context)
            for p in picking_ids_2:
                picking_moves = self.pool.get("stock.move").search_count(cr,SUPERUSER_ID,[("picking_id","=",p),("state","=","done"),("cost_mark","=",0)],context=context)
                if picking_moves>0:
                    picking_ids.append(p)
        _logger.error(picking_ids)
        for p in self.pool.get("stock.picking").browse(cr,SUPERUSER_ID,picking_ids,context=context):
            move_ids = self.pool.get("stock.move").search(cr,SUPERUSER_ID,[("location_dest_id","in",production_location_id),("picking_id","=",p.id),("state","=","done"),("cost_mark","=",0)],context=context)

            #处理每笔出库单对象的未完结的库存移动.
            for m in self.pool.get("stock.move").browse(cr,SUPERUSER_ID,move_ids,context=context):
                is_computer=False
                #检查是否有退货
                back_move_ids = self.pool.get("stock.move").search(cr,SUPERUSER_ID,[("origin_returned_move_id","=",m.id),("location_id","=",m.location_dest_id.id),("location_dest_id","=",m.location_id.id),("state","=","done"),("product_qty","=",m.product_qty)])
                if back_move_ids:continue
                #检查领用出库单对应的采购是否已经确认发票
                #p_ids=[]
                #for q in m.quant_ids:
                #    for h in q.history_ids:
                #        if h.location_id.id==supplier_location_id[0] and h.purchase_line_id != False and h.state=="done":
                #            p_ids.append(h.purchase_line_id.id)
                #获取跟此笔移库相关的采购明细ID
                p_ids = self.pool.get("stock.move")._get_purchase_order_line(cr,SUPERUSER_ID,m.id,context=context)
                p_ids = [i for i in p_ids if i]
                _logger.debug("move_id is %s,and purchase_order_line_id is %s"%(m.id,p_ids))
                if p_ids:
                    il_ids=[]

                    for l in self.pool.get("purchase.order.line").browse(cr,SUPERUSER_ID,p_ids,context=context):
                        if not l.invoice_lines:
                            il_ids=[]
                            break
                        for il in l.invoice_lines:
                            il_ids.append(il.id)
                    _logger.debug("invoice ids is %s"%(il_ids))
                    if il_ids:
                        if obj.invoice:
                            if self.pool.get("account.invoice.line").search_count(cr,SUPERUSER_ID,[("id","in",il_ids),("invoice_id.state","not in",["cancel"])],context=context)==0:
                                continue
                        else:
                            if self.pool.get("account.invoice.line").search_count(cr,SUPERUSER_ID,[("id","in",il_ids),'|',("invoice_id.state","in",["draft","cancel"]),("invoice_id.period_id.date_start",">",period_obj.date_stop)],context=context)>0:
                                continue
                    else:
                        continue

                for mq in m.quant_ids:
                    if mq.qty<0:continue
                    if obj.inventory:
                        is_purchase=True
                    else:
                        is_purchase=False
                        if p_ids:is_purchase=True
                    if not is_purchase:continue
                    #处理项目分摊数量
                    if m.product_id.project_allocation:
                        if not m.product_id.project_ids:
                            raise osv.except_osv("Error",u"产品[%s]设定为依每月项目人份分摊，但产品基本资料未设定每个项目的可做样本数。"%(m.product_id.name,))
                        if not self.month_project:
                            persons_ids = self.pool.get("rhwl.project.persons").search(cr,uid,[("date","=",obj.date),("state","=","done")],context=context)
                            if not persons_ids:
                                raise osv.except_osv("Error",u"当月未设定各项目人份数。")
                            persons_obj = self.pool.get("rhwl.project.persons").browse(cr,uid,persons_ids,context=context)
                            for ps in persons_obj.line:
                                self.month_project[ps.project_id.id] = ps.sample_count
                        if not self.product_project.get(m.product_id.id,None):
                            self.product_project[m.product_id.id]={}
                            for ps in m.product_id.project_ids:
                                self.product_project[m.product_id.id][ps.project_id.id]=ps.sample_count
                        temp_number={}
                        for k1,v1 in self.month_project.items():
                            if self.product_project[m.product_id.id].get(k1):
                                temp_number[k1] = (v1*1.0)/self.product_project[m.product_id.id].get(k1)
                        if not temp_number:
                            temp_number[p.project.id] = 1
                        old_qty = mq.qty
                        sum_rate = sum(temp_number.values())

                        for k1 in temp_number.keys():
                            temp_number[k1] = round(mq.qty * temp_number[k1]/sum_rate,6)
                            old_qty -= temp_number[k1]
                        if old_qty !=0:
                            temp_number[temp_number.keys()[-1]] += old_qty
                        for k1,v1 in temp_number.items():
                            val={
                                "parent_id":obj.id,
                                "data_kind":"this",
                                "product_id":mq.product_id.id,
                                "qty":v1,
                                "price":mq.cost,
                                "amount":round(v1 *mq.cost,2) ,
                                "move_type":"out",
                                "project":k1,
                                "is_rd":p.is_rd
                            }

                            self.pool.get("rhwl.material.cost.line").create(cr,uid,val,context=context)
                            is_computer = True
                    else:
                        val={
                            "parent_id":obj.id,
                            "data_kind":"this",
                            "product_id":mq.product_id.id,
                            "qty":mq.qty,
                            "price":mq.cost,
                            "amount":round(mq.qty *mq.cost,2) ,
                            "move_type":"out",
                            "project":p.project.id,
                            "is_rd":p.is_rd
                        }
                        self.pool.get("rhwl.material.cost.line").create(cr,uid,val,context=context)
                        is_computer = True
                if is_computer:self.pool.get("stock.move").write(cr,SUPERUSER_ID,m.id,{"cost_mark":obj.id},context=context)

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
                if this_detail_ids.count(t.id)>0:
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

        #调整数量为0，但有金额的期末
        end_ids = self.pool.get("rhwl.material.cost.line").search(cr,uid,[("parent_id","=",obj.id),("data_kind","=","end"),("qty","=",0),("amount","!=",0)])
        for i in self.pool.get("rhwl.material.cost.line").browse(cr,uid,end_ids,context=context):
            max_product_id = self.pool.get("rhwl.material.cost.line").search(cr,uid,[("parent_id","=",obj.id),("data_kind","=","this"),("move_type","=","out"),("product_id","=",i.product_id.id),("price","=",i.price)],order="amount desc",context=context)
            if max_product_id:
                cr.execute("update rhwl_material_cost_line set amount = amount+(%s) where id=%s"%(i.amount,max_product_id[0]))
                cr.execute("update rhwl_material_cost_line set amount=0 where id=%s"%(i.id))
        cr.commit()
        #更新计算时间
        self.write(cr,uid,obj.id,{"compute_date":fields.datetime.now()},context=context)
        pass

    def _get_data_dict(self,cr,uid,id,context=None):
        data={}
        """{
            大类别：{
                        小类别：{
                                    产品：{
                                            单价：{
                                                    类别：[]
                                                   }
                                            }
                                    }
                        }
            }"""
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