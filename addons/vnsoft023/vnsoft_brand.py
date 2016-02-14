# -*- coding: utf-8 -*-
from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp import tools, api
import datetime

class vnsoft_brand(osv.osv):
    _name = "vnsoft.brand"

    _columns={
        "name":fields.char(u"品牌名称",size=20),
        "website":fields.char(u'网址',size=50),
        "content":fields.text(u"品牌介绍"),
        "note":fields.text(u"备注"),
        "brand_partner":fields.many2many("res.partner","vnsoft_brand_partner_ref","brand_id","partner_id",string=u"供应商"),
        "brand_product":fields.many2many("product.product","vnsoft_brand_product_ref","brand_id","product_id",string=u"产品")
    }
    _sql_constraints = [
        ('vnsoft_brand_name_uniq', 'unique(name)', u'品牌名称必须唯一!'),
    ]
