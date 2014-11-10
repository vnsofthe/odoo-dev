# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
import datetime


class rhwl_sale(osv.osv):
    _inherit = "sale.order"
    _columns = {
        "sample_name": fields.many2one("sale.sampleone", u"样品单号"),
    }


class rhwl_sample_info(osv.osv):
    _name = "sale.sampleone"
    _description = "样品信息表"
    # _inherit = "sale.order"

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
        "reuse_name": fields.many2one("sale.sampleone", u"重采血编号"),
        "reuse_type": fields.selection(SELECTION_TYPE, u"重采血类型"),
        "is_free": fields.selection([(u'是', u'是'), (u'否', u'否')], u'是否免费'),
        "yfxm": fields.char(u"孕妇姓名", size=20),
        "yfyzweek": fields.integer(u"孕周_周"),
        "yfyzday": fields.integer(u"孕周_天"),
        "yfzjmc": fields.selection([(u"身份证", u"身份证"), (u"其它", u"其它")], u"证件类型"),
        "yfzjmcother": fields.char(u"名称", size=10),
        "yfzjmc_no": fields.char(u"证件号码", size=30),
        "yfage": fields.integer(u"孕妇年龄(周岁)"),
        "yffqage": fields.integer(u"胎儿父亲年龄(周岁)"),
        "yflastyj": fields.date(u"末次月经"),
        "yfyjzq": fields.integer(u"月经周期"),
        "yftelno": fields.char(u"手机号", size=15),
        "yfjjlltel": fields.char(u"紧急联络电话", size=20),
        "yfpostaddr": fields.char(u"邮件地址", size=50),
        "yfpostno": fields.char(u"邮编", size=6),
        "yfheight": fields.integer(u"身高(cm)"),
        "yfweight": fields.float(u"体重(kg)"),
        "yfycount": fields.integer(u'孕次数'),
        "yfzcount": fields.integer(u'产次数'),
        "yfblycs": fields.selection([(u'无', u'无'), (u'有', u'有')], u'不良孕产史'),
        "yfblycstext": fields.char(u"不良孕产史说明", size=20),
        "yfjzycb": fields.selection([(u'无', u'无'), (u'有', u'有')], u'家族遗传病'),
        "yfjzycbtext": fields.char(u"家族遗传病说明", size=20),
        "yffqsfrsthx": fields.selection([(u'无', u'无'), (u'有', u'有')], u'夫妻双方染色体核型'),
        "yffqsfrsthxtext": fields.char(u"夫妻双方染色体核型说明", size=20),
        "yfyczk": fields.selection([(u'单胎', u'单胎'), (u'双胎', u'双胎'), (u'其它', u'其它')], u"孕娠状况"),
        "yfyczktext": fields.char(u'孕娠说明', size=20),
        "yfissgyr": fields.selection([(u'否', u'否'), (u'是', u'是')], u'试管婴儿'),
        "yfcsjc": fields.selection([(u'未见异常', u'未见异常'), (u'提示异常', u'提示异常')], u"超声检查"),
        "yfcsjctext": fields.char(u'异常原因', size=20),
        "yfxqsc": fields.selection([(u'未做', u'未做'), (u'已做', u'已做')], u'血清筛查'),
        "yfxqsctext": fields.char(u'风险提示', size=20),
        "yfyyjrxccss": fields.selection([(u'无', u'无'), (u'已预约', u'已预约')], u'预约介入性穿刺手术'),
        "yfyyjrxccssdate": fields.date(u'预约日期'),
        "yfxbzl": fields.selection([(u'否', u'否'), (u'是', u'是')], u'细胞治疗'),
        "yfxbzltext": fields.char(u'细胞治疗说明', size=20),
        "yfzlfz": fields.selection([(u'否', u'否'), (u'是', u'是')], u'肿瘤患者'),
        "yfzlfztext": fields.char(u'肿瘤患者说明', size=20),
        "yfynnytsx": fields.selection([(u'否', u'否'), (u'是', u'是')], u'一年内异体输血'),
        "yfynnytsxtext": fields.char(u'一年内异体输血说明', size=20),
        "yftsqkbz": fields.char(u'特殊情况备注', size=100),
        "note": fields.text(u'备注'),
        "state": fields.selection([('draft', u'草稿'), ('done', u'完成'), ('cancel', u'取消')], u'状态'),
    }
    _defaults = {
        "state": lambda obj, cr, uid, context: "draft",
    }
    _sql_constraints = [
        ('sample_number_uniq', 'unique(name)', u'样品编号不能重复!'),
    ]
