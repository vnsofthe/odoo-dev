# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp import tools, api
import datetime

class rhwl_product_product(osv.osv):
    _inherit = "product.product"
    _columns = {
        "brand":fields.char(u"品牌",size=20),
        "product_no":fields.char(u"物品编码",size=20),
        "project_ids":fields.one2many("rhwl.product.project","product_id",u"项目耗用量"),
        'uol_id': fields.many2one('product.uom', 'Unit of Library',),
    }

    _default = {
        "sample_count":0
    }

class rhwl_product_project(osv.osv):
    _name = "rhwl.product.project"
    _columns={
        "product_id":fields.many2one("product.product","Product",ondelete="cascade"),
        "project_id":fields.many2one("res.company.project","Project",ondelete="restrict"),
        "sample_count":fields.float(u"可做样品数",digits_compute=dp.get_precision('Product Price')),
    }
    _sql_constraints = [
        ('rhwl_product_project_uniq', 'unique(product_id,project_id)', u'同产品下不能设置两个相同项目!'),
    ]

    def create(self,cr,uid,val,context=None):
        id = super(rhwl_product_project,self).create(cr,uid,val,context)
        obj = self.browse(cr,uid,id,context=context)
        self.pool.get("stock.warehouse.orderpoint").compute_product_orderpoint(cr,uid,obj.product_id.id,context=context)
        return id

    def write(self, cr, uid, ids, vals, context=None):
        id= super(rhwl_product_project,self).write(cr,uid,ids,vals,context)
        obj = self.browse(cr,uid,ids,context=context)
        self.pool.get("stock.warehouse.orderpoint").compute_product_orderpoint(cr,uid,obj.product_id.id,context=context)
        return id

    def unlink(self, cr, uid, ids, context=None):
        obj = self.browse(cr,uid,ids,context=context)
        pid=obj.product_id.id
        id = super(rhwl_product_project,self).unlink(cr,uid,ids,context)
        self.pool.get("stock.warehouse.orderpoint").compute_product_orderpoint(cr,uid,pid,context=context)
        return id

class rhwl_product_template(osv.osv):
    _inherit = "product.template"

    _columns = {
        "brand":fields.related("product_variant_ids","brand",type="char",string=u"品牌",size=20),
        "product_no":fields.related("product_variant_ids","product_no",type="char",string=u"物品编码"),
        "cost_allocation":fields.boolean(u"可跨月分摊"),
        "project_ids":fields.related("product_variant_ids","project_ids",type="one2many",relation="rhwl.product.project",string=u"项目耗用量"),
        'uol_id': fields.many2one('product.uom', 'Unit of Library',),
        "project_allocation":fields.boolean(u"依项目人份数分摊"),
        "is_web":fields.boolean(u"可在线领用"),
    }
    _defaults={
        'purchase_requisition':True,
        "cost_allocation":False,
        "project_allocation":False,
        "is_web":False
    }

    def init(self,cr):
        ids = self.search(cr,SUPERUSER_ID,[("purchase_ok","=",True),("purchase_requisition","=",False)])
        self.write(cr,SUPERUSER_ID,ids,{"purchase_requisition":True})

    def create(self, cr, uid, vals, context=None):
        ''' Store the initial standard price in order to be able to retrieve the cost of a product template for a given date'''
        product_template_id = super(rhwl_product_template, self).create(cr, uid, vals, context=context)

        related_vals = {}
        if vals.get("brand"):
            related_vals['brand'] = vals['brand']
        if vals.get('product_no'):
            related_vals['product_no'] = vals['product_no']
        if vals.get("project_ids"):
            related_vals['project_ids'] = vals['project_ids']
        if vals.get("cost_allocation"):
            related_vals["cost_allocation"] = vals["cost_allocation"]
        if vals.get("uol_id"):
            related_vals["uol_id"] = vals["uol_id"]
        if related_vals:
            self.write(cr, uid, product_template_id, related_vals, context=context)

        return product_template_id
