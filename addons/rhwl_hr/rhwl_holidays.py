# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
import datetime


class rhwl_holidays(osv.osv):
    _inherit = "hr.holidays"

    def get_select_state(self,cr,uid,context):
        return dict(fields.selection.reify(cr,uid,self,self._columns['state'],context=context))
