# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
import datetime


class rhwl_hr(osv.osv):
    _name = "hr.employee"
    _description = "Employee"
    _inherit = "hr.employee"

    _columns = {
        "work_number": fields.char(u"工号", required=True),
    }
    _sql_constraints = [
        ('work_number_uniq', 'unique(work_number)', u'工号必须唯一!'),
    ]

