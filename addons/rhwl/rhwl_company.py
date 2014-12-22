# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
import datetime
import re

class rhwl_company(osv.osv):
    _inherit = "res.company"

    _columns = {
        "sample_count":fields.float(u"每月预估样品数",digits_compute=dp.get_precision('Product Unit of Measure')),
    }

    def write(self, cr, uid, ids, vals, context=None):
        id = super(rhwl_company,self).write(cr,uid,ids,vals,context)
        if vals.get("sample_count"):
            company_count = vals.get("sample_count")
            product_obj = self.pool.get("product.product")
            product_ids = product_obj.search(cr,uid,[('sample_count','>',0),('active','=',True),('purchase_ok','=',True)],context=context)
            for pro_id in product_ids:
                product = product_obj.browse(cr,uid,pro_id,context=context) #取每个产品信息
                delay = 0
                if product.seller_ids:
                    delay = product.seller_ids[0].delay
                else:
                    delay = 1
                point_id = self.pool.get("stock.warehouse.orderpoint").search(cr,uid,[('product_id','=',product.id)])
                if not point_id:
                    point_id = self.pool.get("stock.warehouse.orderpoint").create(cr,uid,{"product_id":product.id,"product_max_qty":0,"product_min_qty":0},context=context)
                delay_month = delay/30 + (delay%30 and 1 or 0)
                min_qty = round(delay_month * company_count / product.sample_count) #采购周期月份乘以每月预估样品数，不够一月的按一月计算
                self.pool.get("stock.warehouse.orderpoint").write(cr,uid,point_id,{"product_min_qty":min_qty,"product_max_qty":(min_qty*2)},context=context)

        return id