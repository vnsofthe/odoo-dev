# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
import datetime
import re

class rhwl_import(osv.osv):
    _name = "rhwl.import.temp"

    _columns = {
        "col1":fields.char("col1",size=150),
        "col2":fields.char("col2",size=150),
        "col3":fields.char("col3",size=150),
        "col4":fields.char("col4",size=150),
        "col5":fields.char("col5",size=150),
        "col6":fields.char("col6",size=150),
        "col7":fields.char("col7",size=150),
        "col8":fields.char("col8",size=150),
        "col9":fields.char("col9",size=150),
        "col10":fields.char("col10",size=150),
        "col11":fields.char("col11",size=150),
        "col12":fields.char("col12",size=150),
        "col13":fields.char("col13",size=150),
        "col14":fields.char("col14",size=150),
    }