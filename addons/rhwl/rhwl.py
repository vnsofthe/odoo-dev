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
        "dev_user_id":fields.many2one('res.users', string=u'开发人员'),
        "cust_level":fields.selection([('AA','AA'),('AB','AB'),('BC','BC'),('CC','CC')],u'客户级别'),
        "hospital_level":fields.selection([(u'二级以下',u'二级以下'),(u'二乙',u'二乙'),(u'二甲',u'二甲'),(u'三甲',u'三甲')],u'医院等级'),
        "cust_type":fields.selection([(u'私立',u'私立'),(u'公立',u'公立')],u'客户性质'),
    }

    _sql_constraints=[
        ("partner_unid_uniq","unique(partner_unid)",u"编号必须为唯一!"),
    ]