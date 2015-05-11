# coding=utf-8

from openerp import SUPERUSER_ID,api
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
import datetime
import openerp
import logging

class rhwl_lib(osv.osv):
    _name="rhwl.library.request"
    _columns={
        "name":fields.char("Name",size=15,readonly=True),
        "date":fields.date("Date"),
        "user_id":fields.many2one("res.users","User"),
        "location_id":fields.many2one("stock.location","Location",required=True,domain=[('usage', '=', 'internal')],readonly=True,states={'draft':[('readonly',False)]}),
        "state":fields.selection([("draft","Draft"),("confirm","Confirm"),("done","Done"),("cancel","Cancel")],"State"),
        "line":fields.one2many("rhwl.library.request.line","name","Line",readonly=True,states={'draft':[('readonly',False)]}),
        "note":fields.char("Note",size=200),
    }

    _defaults={
        "state":'draft',
        "user_id":lambda obj,cr,uid,context=None:uid,
        "date":fields.date.today
    }

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if vals.get('name', '/') == '/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'rhwl.library.request') or '/'
        return super(rhwl_lib,self).create(cr,uid,vals,context)

class rhwl_lib_line(osv.osv):
    _name="rhwl.library.request.line"
    _columns={
        "name":fields.many2one("rhwl.library.request","Name"),
        "product_id":fields.many2one("product.product","Product",required=True),
        "brand":fields.related("product_id","brand",type="char",string=u"品牌",readonly=True),
        "default_code":fields.related("product_id","default_code",type="char",string=u"货号",readonly=True),
        "attribute":fields.related("product_id","attribute_value_ids",obj="product.attribute.value", type="many2many",string=u"规格",readonly=True),
        "uom_id":fields.related("product_id","uom_id",type="many2one",obj="product.uom",string="Unit",readonly=True),
        "qty":fields.float("Qty",digits_compute=dp.get_precision('Product Unit of Measure'),required=True,),
    }
    _sql_constraints = [
        ('rhwl_lib_request_line_uniq', 'unique(name,product_id)', u'明细清单中相同产品不能重复!'),
    ]

    @api.onchange("product_id")
    def _onchange_product(self):
        if self.product_id:
            obj = self.env["product.product"].browse(self.product_id.id)
            self.brand = obj.brand
            self.default_code = obj.default_code
            self.attribute = obj.attribute_value_ids
            self.uom_id = obj.uom_id