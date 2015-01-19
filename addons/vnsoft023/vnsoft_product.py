# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp import tools, api
import datetime

class rhwl_product_template(osv.osv):
    _inherit = "product.template"

    _columns = {
        "brand":fields.char(u"品牌",size=20),
        "name2":fields.char(u"名称"),
    }
    def create(self, cr, uid, vals, context=None):
        ''' Store the initial standard price in order to be able to retrieve the cost of a product template for a given date'''
        product_template_id = super(rhwl_product_template, self).create(cr, uid, vals, context=context)

        related_vals = {}
        if vals.get('brand'):
            related_vals['brand'] = vals['brand']
        if vals.get('name2'):
            related_vals['name2'] = vals['name2']
        if related_vals:
            self.write(cr, uid, product_template_id, related_vals, context=context)

        return product_template_id

class vnsoft_sale_order(osv.osv):
    _inherit = "sale.order"
    _columns={
        "vn_delay":fields.char(u"货期",size=100),
    }

class vnsoft_saleorderline(osv.osv):
     _inherit = "sale.order.line"
     _columns = {
         "brand":fields.related('product_id', 'brand', type='char', string=u'品牌', readonly=1),
     }

     def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        vals = super(vnsoft_saleorderline,self).product_id_change(cr,uid,ids,pricelist,product,qty,uom,qty_uos,uos,name,partner_id,
                                                                  lang,update_tax,date_order,packaging,fiscal_position,flag,context)
        if product:
            pobj = self.pool.get('product.product').browse(cr,uid,product,context)
            vals['value']['brand'] = pobj.brand
        return vals

class vnsoft_purchase_order_line(osv.osv):
     _inherit = "purchase.order.line"
     _columns = {
         "brand":fields.related('product_id', 'brand', type='char', string=u'品牌', readonly=1),
     }
     def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order=False, fiscal_position_id=False, date_planned=False,
            name=False, price_unit=False, state='draft', context=None):
         vals= super(vnsoft_purchase_order_line,self).onchange_product_id(cr,uid,ids,pricelist_id,product_id,qty,uom_id,partner_id,date_order,fiscal_position_id,date_planned,name,price_unit,state,context)
         if product_id:
             pobj = self.pool.get('product.product').browse(cr,uid,product_id,context)
             vals['value']['brand'] = pobj.brand
         return vals

class vnsoft_stock_move(osv.osv):
     _inherit = "stock.move"
     _columns = {
         "brand":fields.related('product_id', 'brand', type='char', string=u'品牌', readonly=1),
     }

class vnsoft_partner(osv.osv):
    _inherit  = "res.partner"
    _columns = {
        "tax_no":fields.char(u"税号",size=30)
    }