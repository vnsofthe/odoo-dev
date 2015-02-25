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

    def onchange_user(self, cr, uid, ids, user_id, context=None):
        work_email = False
        name = False
        if user_id:
            obj=self.pool.get('res.users').browse(cr, uid, user_id, context=context)
            work_email = obj.email
            name = obj.name
        return {'value': {'work_email': work_email,'name':name}}