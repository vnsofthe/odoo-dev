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
        "state":fields.selection([("draft","Draft"),("done","Done")]),
        "line":fields.one2many("rhwl.material.cost.line","parent_id",string="Detail",readonly=True)
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
        old_ids = self.pool.get("rhwl.material.cost.line").search(cr,uid,[("parent_id","=",obj.id),("data_kind","=","begin")],context=context)
        if old_ids:
            self.pool.get("rhwl.material.cost.line").unlink(cr,uid,old_ids)
        #处理期初
        begin_id = self.search(cr,uid,[("date","<",obj.date),("state","=","done")],context=context)
        if begin_id:
            begin_obj = self.browse(cr,uid,begin_id,context=context)
            for d in begin_obj.line:
                if d.data_kind != "end":continue
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
        period_ids = self.pool.get("account.period").search(cr,SUPERUSER_ID,[("date_stop",">=",obj.date),("date_start","<=",obj.date)],context=context)
        #取得会计期间所有已收到的供应商发票资料。

        invoice_ids = self.pool.get("account.invoice").search(cr,SUPERUSER_ID,[("state","not in",["draft","cancel"]),("period_id","in",period_ids),('type','=','in_invoice')],context=context)
        invoice_line_ids = self.pool.get("account.invoice.line").search(cr,SUPERUSER_ID,[("invoice_id","in",invoice_ids)],context=context)
        purchase_line_ids = self.pool.get("purchase.order.line").search(cr,SUPERUSER_ID,[("invoice_lines","in",invoice_line_ids)],context=context)
        move_ids = self.pool.get("stock.move").search(cr,SUPERUSER_ID,[("location_id","=",supplier_location_id[0]),("purchase_line_id","in",purchase_line_ids)],context=context)

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

        #更新计算时间
        self.write(cr,uid,obj.id,{"compute_date":fields.datetime.now()},context=context)
        pass

class rhwl_material_line(osv.osv):
    _name="rhwl.material.cost.line"
    _columns={
        "parent_id":fields.many2one("rhwl.material.cost","Parent"),
        "data_kind":fields.selection([("begin","Begin"),("this","This"),("end","End")],string="Data Kind"),
        "product_id":fields.many2one("product.product","Product",required=True),
        "brand":fields.related("product_id","brand",type="char",string=u"品牌",readonly=True),
        "default_code":fields.related("product_id","default_code",type="char",string=u"货号",readonly=True),
        "attribute":fields.related("product_id","attribute_value_ids",obj="product.attribute.value", type="many2many",string=u"规格",readonly=True),
        "uom_id":fields.related("product_id","uom_id",type="many2one",obj="product.uom",string="Unit",readonly=True),
        "qty":fields.float("Qty",digits_compute=dp.get_precision('Product Unit of Measure'),required=True,),
        'price': fields.float('Price',digits_compute= dp.get_precision('Product Price'), readonly=True,),
        "project":fields.many2one("res.company.project","Project"),
        "is_rd":fields.boolean("R&D"),
        'amount': fields.float("Amt", digits_compute=dp.get_precision('Account')),
        "move_type":fields.selection([('in','in'),('out','out')],string="Move Type")
    }