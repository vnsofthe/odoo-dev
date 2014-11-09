# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
import datetime


class rhwl_sample_info(osv.osv):
    _name = "sale.sampleone"
    _description = "样品信息表"
    #_inherit = "sale.order"

    SELECTION_TYPE = [
        (u'全血', u'全血'),
        (u'血浆', u'血浆'),
        (u'其它', u'其它')
    ]
    _columns = {
        "name": fields.char(u"样品编号", required=True, size=20),
        "sampletype": fields.selection(SELECTION_TYPE, u"样品类型"),
        "cx_date": fields.datetime(u'采血时间'),
        "receiv_user": fields.many2one('res.users', string=u'收样人员'),
        "state_id": fields.many2one('res.country.state', string=u'样品区域（省）'),
        "city": fields.char(u"样品区域（市)"),
        "lyyy": fields.many2one('res.partner', string=u'来源医院',
                                domain=[('is_company', '=', True), ('customer', '=', True)]),
        "cxyy": fields.many2one('res.partner', string=u'采血医院',
                                domain=[('is_company', '=', True), ('customer', '=', True)]),
        "lyys": fields.many2one('res.partner', string=u'来源医生',
                                domain=[('is_company', '=', False), ('customer', '=', True)]),
        "cxys": fields.many2one('res.partner', string=u'采血医生',
                                domain=[('is_company', '=', False), ('customer', '=', True)]),
        "fzr": fields.many2one('res.users', string=u'负责人'),
        # "state": fields.selection([('draf','draf')], u'状态'),
        "is_reused": fields.selection([(u'首次', u'首次'), (u'重采血', u'重采血')], u'是否重采血', required=True),
        "reuse_name": fields.many2one( "sale.sampleone",u"重采血编号"),
        "reuse_type": fields.selection(SELECTION_TYPE, u"重采血类型"),
        "is_free": fields.selection([(u'是', u'是'), (u'否', u'否')], u'是否免费'),
        "state":fields.selection([('draft',u'草稿'),('done',u'完成'),('cance',u'取消')],u'状态'),
    }
    _sql_constraints = [
        ('sample_number_uniq', 'unique(name)', u'样品编号不能重复!'),
    ]
