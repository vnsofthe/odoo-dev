# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
import datetime
import re

class rhwl_import(osv.osv):
    _name = "rhwl.import.temp"

    _columns = {
        "col1":fields.char("col1",size=50),
        "col2":fields.char("col2",size=50),
        "col3":fields.char("col3",size=50),
        "col4":fields.char("col4",size=50),
        "col5":fields.char("col5",size=50),
    }