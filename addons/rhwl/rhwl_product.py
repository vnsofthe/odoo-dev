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
        "product_no":fields.char(u"物品编码",size=20),
        "sample_count":fields.float(u"可做样品数",digits_compute=dp.get_precision('Product Price')),
    }

    _default = {
        "sample_count":0
    }

class rhwl_product_template(osv.osv):
    _inherit = "product.template"

    _columns = {
        "brand":fields.char(u"品牌",size=20),
        "product_no":fields.related("product_variant_ids","product_no",type="char",string=u"物品编码"),
        "sample_count":fields.related("product_variant_ids","sample_count",string=u"可做样品数"),
    }
    def create(self, cr, uid, vals, context=None):
        ''' Store the initial standard price in order to be able to retrieve the cost of a product template for a given date'''
        product_template_id = super(rhwl_product_template, self).create(cr, uid, vals, context=context)

        related_vals = {}
        if vals.get('product_no'):
            related_vals['product_no'] = vals['product_no']
        if vals.get("sample_count"):
            related_vals['sample_count'] = vals['sample_count']

        if related_vals:
            self.write(cr, uid, product_template_id, related_vals, context=context)

        return product_template_id
