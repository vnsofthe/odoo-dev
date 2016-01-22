# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID,api
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import datetime,time
import logging

class rhwl_picking(osv.osv):
    _name = "rhwl.sample.picking"
    _columns = {
        "name":fields.char(u"发货单号",size=10,required=True),
        "batch_no":fields.char(u"批号",size=10,required=True),
        "date":fields.date(u"日期",required=True),
        "state":fields.selection([("draft",u"草稿"),("confirm",u"确认"),("done",u"完成")],string=u"状态",required=True),
        "user_id":fields.many2one("res.users",string=u"处理人员",required=True),
        "line":fields.one2many("rhwl.sample.picking.line","parent_id",string="Detail"),
        "express":fields.one2many("rhwl.sample.picking.express","parent_id",string="express")
    }
    _defaults={
        "user_id":lambda obj,cr,uid,context:uid,
        "state":"draft",
        "date":fields.date.today,
    }

    _sql_constraints = [
        ('rhwl_sample_picking_name_uniq', 'unique(name)', u'发货单号不能重复!'),
    ]

class rhwl_picking_line(osv.osv):
    _name = "rhwl.sample.picking.line"
    _columns={
        "name":fields.many2one("sale.sampleone",string=u"样本编号",ondelete="restrict"),
        "parent_id":fields.many2one("rhwl.sample.picking",string="Parent"),
        "yfxm": fields.related('name', 'yfxm', type='char', string=u'孕妇姓名', readonly=1),
        "cx_date": fields.related('name', 'cx_date', type='char', string=u'采血日期', readonly=1),
        "yfage": fields.related('name', 'yfage', type='integer', string=u'年龄(周岁)', readonly=1),
        "yfyzweek": fields.related('name', 'yfyzweek', type='integer', string=u'孕周', readonly=1),
        "yftelno": fields.related('name', 'yftelno', type='char', string=u'孕妇电话', readonly=1),
        "cxys": fields.related('name', 'cxys', relation="res.partner", type='many2one', string=u'采血医生', readonly=1),
        "cxyy": fields.related('name', 'cxyy', relation="res.partner", type='many2one', string=u'采血医院', readonly=1),
    }

class rhwl_picking_express(osv.osv):
    _name = "rhwl.sample.picking.express"
    _columns={
        "parent_id":fields.many2one("rhwl.sample.picking",u"发货单号",ondelete="restrict"),
        "partner_id":fields.many2one("res.partner",string=u"收件机构",),
        "partner_text":fields.char(u"收件人",size=100),
        "address":fields.char(u"详细地址",size=150),
        "mobile": fields.char(u"手机号码", size=20),
        "qty":fields.integer(u"数量"),
        "state_id": fields.many2one("res.country.state",string=u'省'),
        "city_id": fields.many2one("res.country.state.city",string=u'市',domain="[('state_id','=',state_id)]"),
        "area_id":fields.many2one("res.country.state.city.area",string=u"区/县",domain="[('city_id','=',city_id)]"),
        "express_id":fields.many2one("stock.picking.express",u"快递单",ondelete="restrict"),
        "detail_no":fields.text("Detail No")
    }