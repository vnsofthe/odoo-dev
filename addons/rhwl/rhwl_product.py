# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp import tools, api
import datetime

class rhwl_product(osv.osv):
    _inherit = "product.template"

    _columns = {
        "brand":fields.char(u"品牌",size=20)
    }