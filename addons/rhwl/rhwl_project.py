# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
import datetime
import re

class rhwl_project(osv.osv):
    _name = "rhwl.project"

    _columns = {
        "name":fields.char(u"项目名称"),
        "catelog":fields.char(u"类别"),
        "process":fields.char(u"进度"),
        "user_id":fields.many2one("res.users",u"负责人"),
        "content1":fields.char(string = u"12月5"),
        "content2":fields.char(string = u"12月12"),
        "content3":fields.char(string = u"12月19"),
        "content4":fields.char(string = u"12月26"),
        "content5":fields.char(string = u"01月2"),
        "content6":fields.char(string = u"01月9"),
        "content7":fields.char(string = u"01月16"),
        "content8":fields.char(string = u"01月23"),
        "content9":fields.char(string = u"2015/02月第一周"),
        "content10":fields.char(string = u"2015/02月第二周"),
        "content11":fields.char(string = u"2015/02月第三周"),
        "content12":fields.char(string = u"2015/02月第四周")
    }