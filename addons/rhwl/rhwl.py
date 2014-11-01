# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp.osv import fields, osv


class rhwl_hr(osv.osv):
    _name = "hr.employee"
    _description = "Employee"
    _inherit = "hr.employee"


    _columns = {
        "work_number":fields.char(u"工号",required=True),
    }
    _sql_constraints = [
        ('work_number_uniq', 'unique(work_number)',u'工号必须唯一!'),
    ]

class rhwl_partner(osv.osv):
    _name = "res.partner"
    _description="Partner"
    _inherit = "res.partner"

    _columns = {
        "partner_unid":fields.char(u"编号",required=True),
    }

    _sql_constraints=[
        ("partner_unid_uniq","unique(partner_unid)",u"编号必须为唯一!"),
    ]