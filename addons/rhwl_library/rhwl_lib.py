# coding=utf-8

from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
import datetime
import openerp
import logging

class rhwl_lib(osv.osv):
    _name="rhwl.library.request"
    _columns={
        "name":fields.char("Name",size=15),
        "date":fields.date("Date"),
        "user_id":fields.many2one("res.users","User"),
        "location_id":fields.many2one("stock.location","Location",required=True,domain=[('usage', '=', 'internal')],readonly=True,states={'draft':[('readonly',False)]}),
        "state":fields.selection([("draft","Draft"),("confirm","Confirm"),("done","Done"),("cancel","Cancel")],"State"),
        "line":fields.one2many("rhwl.library.request.line","name","Line")
    }

    _defaults={
        "state":'draft',
        "user_id":lambda obj,cr,uid,context=None:uid,
        "date":fields.date.today
    }

class rhwl_lib_line(osv.osv):
    _name="rhwl.library.request.line"
    _columns={
        "name":fields.many2one("rhwl.library.request","Name"),
        "product_id":fields.many2one("product.product","Product",required=True),
        "qty":fields.float("Qty",digits_compute=dp.get_precision('Product Unit of Measure'),required=True,readonly=True,states={'draft':[('readonly',False)]}),
    }
    _sql_constraints = [
        ('rhwl_lib_request_line_uniq', 'unique(name,product_id)', u'明细清单中相同产品不能重复!'),
    ]