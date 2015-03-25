# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp import tools, api
import datetime

class purchase_requisition(osv.osv):
    _inherit = "purchase.requisition"

    def tender_open(self, cr, uid, ids, context=None):
        obj = self.browse(cr,uid,ids,context=context)
        for p in obj.line_ids:
            if p.min_price==0:
                raise osv.except_osv("错误",u"产品[%s]未进行询价，不可以关闭"%(p.product_id.name))
            self.pool.get("purchase.order.apply.line").write(cr,uid,p.apply_id.id,{'price':p.min_price})
        return super(purchase_requisition,self).tender_open(cr,uid,ids,context=context)

class purchase_requisition_line(osv.osv):
    _inherit = "purchase.requisition.line"

    def _get_min_price(self,cr,uid,ids,name,arg,context=None):
        val = dict.fromkeys(ids,0)

        for i in ids:
            obj = self.browse(cr,uid,i,context=context)
            product_min_price={}
            for p in obj.requisition_id.purchase_ids:
                if p.state=='cancel':continue
                for o in p.order_line:
                    if product_min_price.has_key(o.product_id.id):
                        product_min_price[o.product_id.id] = o.price_unit if o.price_unit<product_min_price[o.product_id.id] else product_min_price[o.product_id.id]
                    else:
                        product_min_price[o.product_id.id]=o.price_unit
            val[i]=product_min_price.get(obj.product_id.id,0)
        return val

    _columns={
        "min_price":fields.function(_get_min_price,type="float",string=u"最低单价"),
        "apply_id":fields.many2one("purchase.order.apply.line",string="Apply ID"),
    }