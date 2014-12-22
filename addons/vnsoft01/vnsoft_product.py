# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
import datetime

class vnsoft_product(osv.osv):
    _inherit = "product.template"

    _columns={
        "characteristic":fields.char(u"规格",size=64),
        "classify":fields.char("classify",size=64),
        "specification":fields.char("specification",size=128),
        "url":fields.char("URL",size=256),
        "vendor":fields.char("Vendor",size=64),
        "ciq_id":fields.integer("ciq_id"),
        "hs_id":fields.integer("hs_id")
    }