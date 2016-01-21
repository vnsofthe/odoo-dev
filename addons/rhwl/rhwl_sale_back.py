# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID,api
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import datetime,time
import rhwl_sms
import requests
import logging
import openerp.tools as tools

class rhwl_sale_back(osv.osv):
    _name = "rhwl.sampleone.sale.back"

    _columns={
        "name":fields.many2one("sale.sampleone", string=u"样本单号",ondelete="restrict"),
        "yfxm": fields.related('name', 'yfxm', type='char', string=u'孕妇姓名', readonly=1),
        "cx_date": fields.related('name', 'cx_date', type='char', string=u'采血日期', readonly=1),
        "yfage": fields.related('name', 'yfage', type='integer', string=u'年龄(周岁)', readonly=1),
        "yfyzweek": fields.related('name', 'yfyzweek', type='integer', string=u'孕周', readonly=1),
        "yftelno": fields.related('name', 'yftelno', type='char', string=u'孕妇电话', readonly=1),
        "cxys": fields.related('name', 'cxys', relation="res.partner", type='many2one', string=u'采血医生', readonly=1,store=True),
        "cxyy": fields.related('name', 'cxyy', relation="res.partner", type='many2one', string=u'采血医院', readonly=1,store=True),
        "yfzjmc_no": fields.related("name","yfzjmc_no",type="char",string=u"证件号码",readonly=1,store=True, size=30),
        "back_note":fields.char(u"退费原因",size=200),
        "back_done":fields.boolean(u"已退费"),
        "back_pages":fields.boolean(u"单据已寄回",help=u"知情同意书/退款协议/收费凭证"),
        "note":fields.text(u"备注"),
        "state":fields.selection([("draft",u"草稿"),("confirm",u"退费中"),("done",u"已完成")],string=u"状态"),
        "user_id":fields.many2one("res.users",u"处理人员")

    }

    _sql_constraints = [
        ('sample_sale_back_uniq', 'unique(name)', u'样品编号不能重复!'),
    ]
    _defaults = {
        "state": lambda obj, cr, uid, context: "draft",
        "user_id":lambda obj,cr,uid,context:uid,
    }

    def action_state_confirm(self,cr,uid,ids,context=None):
        self.write(cr,uid,ids,{"state":"confirm"},context=context)

    def action_state_done(self,cr,uid,ids,context=None):
        self.write(cr,uid,ids,{"state":"done"},context=context)