# coding=utf-8

from openerp import SUPERUSER_ID,api
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
import datetime
import openerp
import logging

class web_material(osv.osv):
    _name = "rhwl.web.material"

    _columns={
        "name":fields.char(u"申请单号",size=10),
        "date":fields.date(u"申请日期"),
        "user_id":fields.many2one("res.users",string=u"申请人"),
        "hospital":fields.many2one("res.partner",string=u"申请医院(机构)",domain="[('is_company', '=', True), ('customer', '=', True),'|',('sjjysj','!=',False),'|',('yg_sjjysj','!=',False),'|',('ys_sjjysj','!=',False),('el_sjjysj','!=',False)]"),
        "wh_level":fields.selection([("hospital",u"医院级"),("proxy",u"代理级"),("person",u"销售员级")],string=u"库存归属"),
        "address_id":fields.many2one("res.partner",string="Address ID"),
        "receiver_user":fields.char(u"收件人",size=10),
        "receiver_address":fields.char(u"收件地址",size=100),
        "receiver_tel":fields.char(u"收件人电话",size=20),
        "state":fields.selection([("draft",u"草稿"),("confirm",u"确认"),("approve1",u"核准1"),("approve2",u"核准2"),("done",u"完成")],string=u"状态"),
        "line":fields.one2many("rhwl.web.material.line","parent_id",string="Line"),
        "express_partner":fields.selection([("sf",u"顺丰"),("sto",u"申通"),("yto",u"圆通"),("yunda",u"韵达")],u"快递公司"),
        "express_no":fields.char(u"快递单号",size=20),
        "note":fields.text(u"备注"),
        "approve1_user":fields.many2one("res.users",string=u"核准人1"),
        "approve2_user":fields.many2one("res.users",string=u"核准人2"),
        "approve1_date":fields.datetime(u"核准时间"),
        "approve2_date":fields.datetime(u"核准时间"),
        "done_date":fields.datetime(u"完成时间"),
    }
    _defaults={
        "date":fields.date.today,
        "user_id":lambda obj,cr,uid,context:uid,
        "state":"draft",
        "wh_level":"person"
    }

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if vals.get('name', '/') == '/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'rhwl.web.material') or '/'
        return super(web_material,self).create(cr,uid,vals,context)

    def action_state_approve1(self,cr,uid,ids,context=None):
        self.write(cr,uid,ids,{"state":"approve1","approve1_user":uid,"approve1_date":fields.datetime.now()},context=context)

    def action_state_approve2(self,cr,uid,ids,context=None):
        self.write(cr,uid,ids,{"state":"approve2","approve2_user":uid,"approve2_date":fields.datetime.now()},context=context)

    def action_state_done(self,cr,uid,ids,context=None):
        for i in self.browse(cr,uid,ids,context=context):
            if not (i.express_partner and i.express_no):
                raise osv.except_osv("Error",u"确认完成时，请输入快递公司和快递单号。")
        self.write(cr,uid,ids,{"state":"done","done_date":fields.datetime.now()},context=context)

class web_material_line(osv.osv):
    _name="rhwl.web.material.line"
    _columns={
        "parent_id":fields.many2one("rhwl.web.material",string="Parent"),
        "product_id":fields.many2one("product.product","Product",required=True,domain=[("is_web","=",True)]),
        "uom_id":fields.related("product_id","uom_id",type="many2one",obj="product.uom",string="Unit",readonly=True),
        "qty":fields.float("Qty",digits_compute=dp.get_precision('Product Unit of Measure'),required=True,),
    }