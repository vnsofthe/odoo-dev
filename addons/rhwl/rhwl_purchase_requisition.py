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
        product=[]
        for o in obj.purchase_ids:
            if o.state=='cancel':continue
            for l in o.order_line:
                product.append(l.product_id.id)
        for p in obj.line_ids:
            if product.count(p.product_id.id)==0:
                raise osv.except_osv("错误",u"产品[%s]未进行询价，不可以关闭"%(p.product_id.name))
        return super(purchase_requisition,self).tender_open(cr,uid,ids,context=context)

class purchase_requisition_line(osv.osv):
    _inherit = "purchase.requisition.line"

    def _get_min_price(self,cr,uid,ids,name,context=None):
        val = dict.fromkeys(ids,0)
        for i in ids:
            min_price=999999999.0
            obj = self.browse(cr,uid,i,context=context)
            for p in obj.requisition_id.purchase_ids:
                for o in p.order_line:
                    min_price = o.price_unit if o.price_unit<min_price else min_price

    _columns={
        "min_price":fields.function(_get_min_price,type="float",string=u"最低单价")
    }