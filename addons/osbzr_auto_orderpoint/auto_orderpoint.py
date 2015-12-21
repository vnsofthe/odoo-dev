# -*- encoding: utf-8 -*-
# __author__ = jeff@osbzr.com
from openerp.osv import osv, fields

class product_product(osv.osv):

    _inherit = 'product.product'

    def create(self, cr, uid, vals, context=None):
        res = super(product_product, self).create(cr, uid, vals, context=context)
        self.pool.get('stock.warehouse.orderpoint').create(cr, uid, {'product_id': res, 
                                                                     'product_min_qty': 0, 
                                                                     'product_max_qty': 0,})
        return res
