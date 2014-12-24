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
            #如果有变更每月预估样品数量，则重新计算每个产品的最小安全库存
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
                    point_id = self.pool.get("stock.warehouse.orderpoint").create(cr,uid,{"product_id":product.id,"product_max_qty":0,"product_min_qty":0,"min_work_days":round(delay*7*1.5)},context=context)
                res = self.pool.get("stock.warehouse.orderpoint").onchange_min_work_days(cr,uid,point_id,round(delay*7*1.5),context=context)
                if res.get("value"):
                    min_qty = res.get("value").get("product_min_qty")
                    max_qty = res.get("value").get("product_max_qty")
                    self.pool.get("stock.warehouse.orderpoint").write(cr,uid,point_id,{"product_min_qty":min_qty,"product_max_qty":max_qty},context=context)
        return id