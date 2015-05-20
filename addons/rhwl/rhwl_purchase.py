# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp import tools, api
import datetime

class purchase_apply(osv.osv):
    _name = "purchase.order.apply"
    _describe = "Purchase Apply"

    def _get_dept(self,cr,uid,context=None):
        id = self.pool.get("hr.employee").search(cr,uid,[('user_id.id','=',uid)],context=context)
        if not id:
            return False
        obj=self.pool.get("hr.employee").browse(cr,uid,id,context=context)
        return obj.department_id.id

    _columns = {
        "name":fields.char(u"申请单号",size=20,readonly=True),
        "date":fields.date(u"申请日期",required=True,),
        "dept":fields.many2one("hr.department",u"部门"),
        "user_id":fields.many2one("res.users",u"申请人",required=True,readonly=True),
        "need_date":fields.date(u"需求日期"),
        "reason":fields.char(u"申请事由"),
        "state":fields.selection([("draft",u"草稿"),("confirm",u"确认"),("refuse",u"退回"),("done",u"完成"),("dept",u"部门批准"),("inspector",u"总监批准"),("quotation",u"询价确认"),("account",u"财务核准"),("chief",u"总裁批准")],u"状态"),
        "note":fields.text(u"备注"),
        "line":fields.one2many("purchase.order.apply.line","name","Detail"),
    }
    _defaults={
        "date":fields.date.today,
        "user_id":lambda obj,cr,uid,context:uid,
        "dept":_get_dept,
        "state":"draft"
    }

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if vals.get('name', '/') == '/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'purchase.apply') or '/'
        return super(purchase_apply,self).create(cr,uid,vals,context)


    def action_confirm(self, cr, uid, ids, context=None):
        obj = self.browse(cr,uid,ids,context=context)
        if not (obj.dept and obj.need_date and obj.reason):
            raise osv.except_osv("错误","申请部门、需求日期、申请事由内容不能为空。")
        if not obj.line:
            raise osv.except_osv("错误","申请单明细不能为空。")
        if obj.need_date <= obj.date:
            raise osv.except_osv("错误","计划需求日期必须大于申请单日期。")
        for i in obj.line:
            if i.qty<=0:
                raise osv.except_osv("错误",u"产品[%s]的申请数量必须大于0"%(i.product_id.name,))
        self.write(cr, uid, ids, {'state': 'confirm'}, context=context)

    def action_create_quotation(self, cr, uid, ids, context=None):
        obj = self.browse(cr,uid,ids,context=context)
        req_id = self.pool.get("purchase.requisition").search(cr,uid,[('origin','=',obj.name),('state','!=','cancel')],context=context)
        if req_id:
            raise osv.except_osv("错误","该申请单已经有生成招标询价单，不能重复生成。")
        line=[]
        sup={}
        for i in obj.line:
            for j in i.product_id.seller_ids:
                if j.min_qty>i.qty:continue
                if sup.has_key(j.name.id):
                    sup[j.name.id].append((i.product_id.id,i.qty,i.uom_po_id.id))
                else:
                    sup[j.name.id]=[(i.product_id.id,i.qty,i.uom_po_id.id)]
            val={'product_id':i.product_id.id,"product_qty":i.qty,"product_uom_id":i.uom_po_id.id,"apply_id":i.id}
            line.append(self.pool.get("purchase.requisition.line").create(cr,uid,val,context=context))
        req_id = self.pool.get("purchase.requisition").create(cr,uid,{"scheduled_date":obj.need_date,"origin":obj.name,"line_ids":[[6,False,line]]},context=context)
        req_obj = self.pool.get("purchase.requisition").browse(cr,uid,req_id,context=context)
        if sup:
            line=[]
            for k,v in sup.items():
                pline=[]
                pick = self.pool.get("purchase.order")._get_picking_in(cr,uid)
                local = self.pool.get("purchase.order").onchange_picking_type_id(cr,uid,0,pick,context=context)
                val = self.pool.get("purchase.order").onchange_partner_id(cr,uid,0,k,context=context).get("value")
                val.update(local.get('value'))
                val.update({'picking_type_id':pick,'partner_id':k,'origin':req_obj.name})
                for j in v:
                    detail_val = self.pool.get("purchase.order.line").onchange_product_id(cr, uid, 0, val.get("pricelist_id"),j[0], j[1], False, k,val.get("date_order"),val.get("fiscal_position"),val.get("date_planned"),False,False,'draft',context=context).get("value")
                    detail_val.update({'product_id':j[0],'product_qty':j[1],'product_uom':j[2]})
                    pline.append([0,0,detail_val])

                val.update({'company_id':1,'order_line':pline})
                line.append(self.pool.get("purchase.order").create(cr,uid,val,context=context))
            self.pool.get("purchase.requisition").write(cr,uid,req_id,{'purchase_ids':[[6,False,line]]})

    def action_quotation(self, cr, uid, ids, context=None):
        obj = self.browse(cr,uid,ids,context=context)
        req_id = self.pool.get("purchase.requisition").search(cr,uid,[('origin','=',obj.name),('state','=','open')],context=context)
        if not req_id:
            raise osv.except_osv("错误","该申请单对应的招标询价单没有关闭，不能确认。")
        self.write(cr, uid, ids, {'state': 'quotation'}, context=context)

    def action_dept(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'dept'}, context=context)
    def action_inspector(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'inspector'}, context=context)
    def action_account(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'account'}, context=context)
    def action_chief(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'chief'}, context=context)
    def action_refuse(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'refuse'}, context=context)
    def action_reset(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'}, context=context)

class purchase_apply_line(osv.osv):
    _name = "purchase.order.apply.line"
    _columns={
        "name":fields.many2one("purchase.order.apply",u"申请单号"),
        "product_id":fields.many2one("product.product",u"产品",required=True,domain=[('purchase_ok','=',True)]),
        "brand":fields.related("product_id","brand",type="char",string=u"品牌",readonly=True),
        "default_code":fields.related("product_id","default_code",type="char",string=u"货号",readonly=True),
        "uom_po_id":fields.related("product_id","uom_po_id",type="many2one",obj="product.uom",string=u"采购单位",readonly=True),
        "attribute":fields.related("product_id","attribute_value_ids",obj="product.attribute.value", type="many2many",string=u"规格",readonly=True),
        "qty":fields.float(u"数量",digits_compute=dp.get_precision('Product Unit of Measure'),required=True),
        "price":fields.float(u"单价",digits_compute=dp.get_precision('Product Price')),
        "price_purchase":fields.float(u"确认单价",digits_compute=dp.get_precision('Product Price')),
        "partner_id":fields.many2one("res.partner",u"供应商"),
        "note":fields.char(u"备注")
    }

    @api.onchange("product_id")
    def _onchange_product(self):
        if self.product_id:
            obj = self.env["product.product"].browse(self.product_id.id)
            self.brand = obj.brand
            self.default_code = obj.default_code
            self.attribute = obj.attribute_value_ids
            self.uom_po_id = obj.uom_po_id

