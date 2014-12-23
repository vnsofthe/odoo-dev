# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
import datetime
import csv
class vnsoft_product(osv.osv):
    _inherit = "product.template"

    _columns={
        "characteristic":fields.char(u"规格",size=64),
        "classify":fields.char("classify",size=64),
        "specification":fields.char("specification",size=128),
        "url":fields.char("URL",size=256),
        "vendor":fields.char("Vendor",size=64),
        "ciq_id":fields.integer("ciq_id"),
        "hs_id":fields.integer("hs_id"),
        "extid":fields.integer("extID")
    }

    def import_csv(self, cr, user, context=None):
        #id,catalog_no,characteristic,classify,description,name_cn,name_en,note,specification,state,storage,url,vendor,ciq_id,hs_id
        reader = csv.reader(open("/home/carbony/item_catalog.csv"))
        for line in reader:
            vals={
                "default_code":line[1],
                "characteristic":line[2],
                "classify":line[3],
                "description":line[4],
                "name":line[5],
                "specification":line[8],
                "url":line[11],
                "vendor":line[12],
                "type":"product",
                "extid":line[0]
            }
            self.create(cr,user,vals,context=context)