# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
import datetime
import re

class rhwl_company(osv.osv):
    _inherit = "res.company"

    _columns = {
        "sample_count":fields.float(u"每月预估样品数",digits_compute=dp.get_precision('Product Unit of Measure')),
    }

