# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
import datetime


class rhwl_partner(osv.osv):
    _name = "res.partner"
    _description = "Partner"
    _inherit = "res.partner"

    _columns = {
        "partner_unid": fields.char(u"编号", required=True),
        "dev_user_id": fields.many2one('res.users', string=u'开发人员'),
        "cust_level": fields.selection(
            [('AA', u'省级、地级市产前诊断中心；大型筛查机构(筛查量1万以上)'), ('AB', u'县级市产前诊断中心、一般筛查机构、分娩5000以上的医院、有能力的三甲医院'),
             ('BC', u'年分娩量1500-3000的医院'), ('CC', u'年分娩量1500以下的医院')], u'客户级别'),
        "hospital_level": fields.selection([(u'二级以下', u'二级以下'), (u'二乙', u'二乙'), (u'二甲', u'二甲'), (u'三甲', u'三甲')],
                                           u'医院等级'),
        "cust_type": fields.selection([(u'私立', u'私立'), (u'公立', u'公立')], u'客户性质'),
        "zydb": fields.many2one('res.users', string=u'驻院代表'),
        "amt": fields.float(u'收费金额', required=True, digits_compute=dp.get_precision('Product Price')),
        "sfdw": fields.many2one('res.partner', string=u'收费单位', domain=[('is_company', '=', True)]),
        "sncjrs": fields.float(u'上年产检人数', digits_compute=0),
        "snwcrs": fields.float(u'上年无创人数', digits_compute=0),
        "jnmbrs": fields.float(u'今年目标人数', digits_compute=0),
        "jnsjrs": fields.float(u'今年实际人数', digits_compute=0, readonly=True),
        "qyks": fields.char(u"签约科室", size=50),
        "jzds": fields.selection([(u'贝瑞', u'贝瑞'), (u'华大', u'华大'), ], u"竞争对手"),
        "mbjysj": fields.date(u'目标进院时间'),
        "sjjysj": fields.date(u'实际进院时间'),
        "eduction":fields.selection([(u'中专',u'中专'),(u'专科',u'专科'),(u'本科',u'本科'),(u'硕士',u'硕士'),(u'博士',u'博士')],string=u'学历'),
        "yjfx":fields.char(u"研究方向",size=100),
        "cprz":fields.selection([("1",u"初识"),("2",u"认可"),("3",u"推荐")],string=u"产品认知"),
    }

    _defaults = {
        "date": fields.date.today,
    }
    _sql_constraints = [
        ("partner_unid_uniq", "unique(partner_unid)", u"编号必须为唯一!"),
    ]

