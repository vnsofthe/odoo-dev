# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp import tools, api
import datetime
import base64
class purchase_apply(osv.osv):
    _name = "purchase.order.apply"
    _describe = "Purchase Apply"

    def _get_dept(self,cr,uid,context=None):
        id = self.pool.get("hr.employee").search(cr,uid,[('user_id.id','=',uid)],context=context)
        if not id:
            return False
        obj=self.pool.get("hr.employee").browse(cr,uid,id,context=context)
        return obj.department_id.id

    def _get_state(self,cr,uid,ids,field_names,arg,context=None):
        res = dict.fromkeys(ids,{})
        for i in self.browse(cr,uid,ids,context=context):
            res[i.id] = dict.fromkeys(field_names,False)
            if i.state!="confirm":continue
            p_state='done'
            p_uid = i.user_id.id
            for p in i.person:
                if p_state=="done" and p_uid==uid and p.state=="draft":
                    res[i.id]["is_cancel"]=True

                if p_state=='done' and p.user_id.id == uid and p.state=="draft":
                    res[i.id]["is_confirm"]=True
                    res[i.id]["is_cancel"]=True
                    continue

                p_state = p.state
                p_uid = p.user_id.id

        return res


    _columns = {
        "name":fields.char(u"申请单号",size=20,readonly=True),
        "date":fields.date(u"申请日期",required=True,),
        "dept":fields.many2one("hr.department",u"部门"),
        "user_id":fields.many2one("res.users",u"申请人",required=True,readonly=True),
        "need_date":fields.date(u"需求日期"),
        "reason":fields.char(u"申请事由"),
        "state":fields.selection([("draft",u"草稿"),("confirm",u"确认"),("refuse",u"退回"),("done",u"完成")],u"状态"),
        "note":fields.text(u"备注"),
        "is_confirm":fields.function(_get_state,type="boolean",multi="getstate"),
        "is_cancel":fields.function(_get_state,type="boolean",multi="getstate"),
        "attachment_id":fields.many2one("ir.attachment","Excel"),
        "person":fields.one2many("purchase.order.apply.person","app_id",u"审核人员"),
        "line":fields.one2many("purchase.order.apply.line","name","Detail"),
        "log":fields.one2many("purchase.order.apply.log","app_id","Log",readonly=True),
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
        vals["log"] = [[0, 0, {"note": u"新增", "data": "create"}]]
        return super(purchase_apply,self).create(cr,uid,vals,context)

    def write(self, cr, uid, id, val, context=None):
        if not context:
            context={}
        if val.has_key("state"):
            sel = dict(fields.selection.reify(cr,uid,self,self._columns['state'],context=context))
            val["log"] = [
                [0, 0, {"note": u"状态变更为:" + sel.get(val.get("state")), "data": val.get("state"),"user_id":context.get("user_id",uid)}]]
        return super(purchase_apply, self).write(cr, uid, id, val, context=context)

    def action_confirm(self, cr, uid, ids, context=None):
        obj = self.browse(cr,uid,ids,context=context)
        if not (obj.dept and obj.need_date and obj.reason):
            raise osv.except_osv("错误","申请部门、需求日期、申请事由内容不能为空。")
        if not obj.line:
            raise osv.except_osv("错误","申请单明细不能为空。")
        if obj.need_date <= obj.date:
            raise osv.except_osv("错误","计划需求日期必须大于申请单日期。")
        if not obj.person:
            raise osv.except_osv("错误","请设置申请单审核人员。")
        for i in obj.line:
            if i.qty<=0:
                raise osv.except_osv("错误",u"产品[%s]的申请数量必须大于0"%(i.product_id.name,))

        pid = self.pool.get("purchase.order.apply.person").search(cr,uid,[("app_id","=",obj.id)])
        if pid:
            user = self.pool.get("res.users")
            is_purchase=False
            user_ids=[]
            for i in self.pool.get("purchase.order.apply.person").browse(cr,uid,pid,context=context):
                if user_ids.count(i.user_id.id)>0:
                    raise osv.except_osv("错误","审批人员中，相同人员不可以重复设置。")
                user_ids.append(i.user_id.id)
                if user.has_group(cr,i.user_id.id,"purchase_requisition.group_purchase_requisition_user"):
                    is_purchase=True
                    break
            if not is_purchase:
                raise osv.except_osv("错误","审核人员中不包含采购招标人员，不可以确认。")
            self.pool.get("purchase.order.apply.person").write(cr,uid,pid,{"state":"draft","time":None,"note":None})
        if obj.attachment_id:
            self.pool.get('ir.attachment').unlink(cr,SUPERUSER_ID,obj.attachment_id.id)
        self.write(cr, uid, ids, {'state': 'confirm',"attachment_id":None}, context=context)

    def action_create_quotation(self, cr, uid, ids, context=None):
        obj = self.browse(cr,uid,ids,context=context)
        req_id = self.pool.get("purchase.requisition").search(cr,uid,[('origin','=',obj.name),('state','!=','cancel')],context=context)
        if req_id:
            raise osv.except_osv("错误","该申请单已经有生成招标询价单，不能重复生成。")
        line=[]
        sup={}
        for i in obj.line:#循环申请明细产品,如果产品有指定采购供应商，
            for j in i.product_id.seller_ids:
                if j.min_qty>i.qty:continue
                if sup.has_key(j.name.id):
                    sup[j.name.id].append((i.product_id.id,i.qty,i.uom_po_id.id))
                else:
                    sup[j.name.id]=[(i.product_id.id,i.qty,i.uom_po_id.id)]
            val={'product_id':i.product_id.id,"product_qty":i.qty,"product_uom_id":i.uom_id.id,"apply_id":i.id}
            line.append(self.pool.get("purchase.requisition.line").create(cr,uid,val,context=context))
        req_id = self.pool.get("purchase.requisition").create(cr,uid,{"scheduled_date":obj.need_date,"origin":obj.name,"line_ids":[[6,False,line]]},context=context)

    def action_quotation(self, cr, uid, ids, context=None):
        obj = self.browse(cr,uid,ids,context=context)
        req_id = self.pool.get("purchase.requisition").search(cr,uid,[('origin','=',obj.name),('state','=','open')],context=context)
        if not req_id:
            raise osv.except_osv("错误","该申请单对应的招标询价单没有关闭，不能确认。")

        self.write(cr, uid, ids, {'state': 'quotation'}, context=context)

    def action_refuse(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'res_model': 'purchase.order.apply.popup',
            'view_mode': 'form',
            'name': u"退回说明",
            'target': 'new',
            'context': {'button': 'cancel'},
            'flags': {'form': {'action_buttons': False}}}

    def action_next(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        pid = self.pool.get("purchase.order.apply.person").search(cr,uid,[("app_id","=",ids),("user_id","=",uid)])
        obj = self.pool.get("purchase.order.apply.person").browse(cr,uid,pid,context=context)
        is_create_excel=False
        if self.pool.get("res.users").has_group(cr,obj.user_id.id,"purchase_requisition.group_purchase_requisition_user"):
            is_create_excel=True
            req_id = self.pool.get("purchase.requisition").search(cr,uid,[('origin','=',obj.app_id.name),('state','=','open')],context=context)
            if not req_id:
                raise osv.except_osv("错误","该申请单对应的招标询价单没有关闭，不能进行审批。")

        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'res_model': 'purchase.order.apply.popup',
            'view_mode': 'form',
            'name': u"审批说明(可选）",
            'target': 'new',
            'context': {'button': 'done',"is_create_excel":is_create_excel},
            'flags': {'form': {'action_buttons': False}}}

    def action_reset(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'}, context=context)

    def create_excel_attachment(self,cr,uid,ids,context=None):
        this = self.browse(cr,uid,ids,context=context)
        if this.attachment_id:return

        if not context:
            context={}
        if not isinstance(ids,(list,tuple)):
            ids = [ids]
        context["active_ids"]=ids
        res = self.pool.get("sale.sample.export.excel").action_excel_apply(cr,uid,ids,context=context)
        if not res.has_key("res_id"):raise osv.except_osv("error","Create Excel Error.")
        obj = self.pool.get("sale.sample.export.excel").browse(cr,uid,res.has_key("res_id"),context=context)

        vals={
                "name":this.name,
                "datas_fname":obj.name,
                "description":obj.name,
                "res_model":"purchase.order.apply",
                "res_id":this.id,
                "create_date":fields.datetime.now,
                "create_uid":SUPERUSER_ID,
                "datas":base64.decodestring(obj.file),
            }
        atta_obj = self.pool.get('ir.attachment')
        if this.attachment_id:
            atta_obj.unlink(cr,SUPERUSER_ID,this.attachment_id.id)
        atta_id = atta_obj.create(cr,SUPERUSER_ID,vals)
        self.write(cr,uid,this.id,{"attachment_id":atta_id})


class purchase_apply_line(osv.osv):
    _name = "purchase.order.apply.line"
    _columns={
        "name":fields.many2one("purchase.order.apply",u"申请单号"),
        "product_id":fields.many2one("product.product",u"产品",required=True,domain=[('purchase_ok','=',True)]),
        "brand":fields.related("product_id","brand",type="char",string=u"品牌",readonly=True),
        "default_code":fields.related("product_id","default_code",type="char",string=u"货号",readonly=True),
        "uom_id":fields.related("product_id","uom_id",type="many2one",obj="product.uom",string=u"计量单位",readonly=True),
        "attribute":fields.related("product_id","attribute_value_ids",obj="product.attribute.value", type="many2many",string=u"规格",readonly=True),
        "qty":fields.float(u"数量",digits_compute=dp.get_precision('Product Unit of Measure'),required=True),
        "price":fields.float(u"单价",digits_compute=dp.get_precision('Product Price'),readonly=True),
        "price_purchase":fields.float(u"确认单价",digits_compute=dp.get_precision('Product Price'),readonly=True),
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
            self.uom_id = obj.uom_id

class purchase_apply_log(osv.osv):
    _name = "purchase.order.apply.log"
    _order = "date desc"
    _columns = {
        "app_id": fields.many2one("purchase.order.apply", "Apply ID",select=True),
        "date": fields.datetime(u"时间"),
        "user_id": fields.many2one("res.users", u"操作人员"),
        "note": fields.text(u"作业说明"),
        "data": fields.char("Data")
    }

    _defaults = {
        "date": fields.datetime.now,
        "user_id": lambda obj, cr, uid, context: uid,
    }

class purchase_apply_person(osv.osv):
    _name = "purchase.order.apply.person"

    _columns={
        "app_id": fields.many2one("purchase.order.apply", "Apply ID",select=True),
        "sequence": fields.integer('Sequence'),
        "user_id":fields.many2one("res.users", u"审核人员"),
        "time":fields.datetime(u"时间",readonly=True),
        "state":fields.selection([('draft',u'待处理'),('done',u'已审批'),('cancel',u'已退回')],"State",readonly=True),
        "note":fields.char(u"备注",readonly=True)
    }
    _defaults={
        "state":'draft',
    }

    def write(self,cr,uid,ids,val,context=None):
        super(purchase_apply_person,self).write(cr,uid,ids,val,context=context)
        obj = self.browse(cr,uid,ids,context=context)
        if val.get("state")=="cancel":
            self.pool.get("purchase.order.apply").write(cr,uid,obj.app_id.id,{"state":"refuse"})
        elif val.get("state")=="done":
            id = self.search(cr,uid,[("app_id","=",obj.app_id.id),("state","=","draft")])
            if not id:
                self.pool.get("purchase.order.apply").write(cr,uid,obj.app_id.id,{"state":"done"})

class purchase_order(osv.osv):
    _inherit = "purchase.order"

    def wkf_confirm_order(self, cr, uid, ids, context=None):
        if isinstance(ids,(long,int)):
            ids = [ids]
        for o in self.browse(cr,uid,ids,context=context):
            if o.requisition_id:
                no=o.requisition_id.origin
                if no:
                    apply_id = self.pool.get("purchase.order.apply").search(cr,uid,[("name","=",no)])
                    if apply_id:
                        apply_id = self.pool.get("purchase.order.apply").search(cr,uid,[("name","=",no),("state","=","done")])
                        if not apply_id:
                            raise osv.except_osv("Error",u"该询价单由采购申请单产生，需要先审批采购申请单才可以确认询价单。")

        return super(purchase_order,self).wkf_confirm_order(cr,uid,ids,context=context)

class purchase_apply_popup(osv.osv_memory):
    _name = "purchase.order.apply.popup"
    _columns = {
        "note": fields.text(u"说明")
    }

    def action_ok(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids, context)
        if not context:
            context={}
        if context.get("button")=="cancel" and not obj.note:
            raise osv.except_osv("错误","退回时，必须说明原因。")
        if context.get("is_create_excel"):
            self.pool.get("purchase.order.apply").create_excel_attachment(cr,uid,context.get("active_id",0))
        ids = self.pool.get("purchase.order.apply.person").search(cr,uid,[("app_id","=",context.get("active_id",0)),("user_id.id","=",uid)])
        if ids:
            self.pool.get("purchase.order.apply.person").write(cr,uid,ids,{"state":context.get("button"),"note":obj.note,"time":fields.datetime.now()})