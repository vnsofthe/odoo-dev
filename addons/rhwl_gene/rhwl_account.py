# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID, api
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import datetime,time
import logging
import os
import shutil
import re
from openerp import tools

class rhwl_account(osv.osv):
    _name = "rhwl.genes.account"

    def _get_count(self,cr,uid,ids,fields_name,args,context=None):
        res={}.fromkeys(ids,{})
        for i in ids:
            res[i]={}.fromkeys(fields_name,0)
            obj = self.browse(cr,uid,i,context=context)
            res[i]["count"] = self.pool.get("rhwl.easy.genes").search_count(cr,uid,[("date",">=",obj.start_date),("date","<=",obj.end_date),("cust_prop","in",["tjs","tjs_vip"])],context=context)
            res[i]["except_count"] = self.pool.get("rhwl.easy.genes").search_count(cr,uid,[("date",">=",obj.start_dna),("date","<=",obj.end_dna),("cust_prop","in",["tjs","tjs_vip"]),("state","=","dna_except")],context=context)
            res[i]["real_count"] = res[i]["count"] - res[i]["except_count"]

        return res

    _columns={
        "start_date":fields.date(u"样本起始日期",required=True),
        "end_date":fields.date(u"样本终止日期",required=True),
        "state":fields.selection([("draft",u"草稿"),("done",u"完成")],u"状态"),
        "count":fields.function(_get_count,type="integer",multi="get_count",string=u"送检样本数量"),
        "start_dna":fields.date(u"质检异常起始日期",required=True),
        "end_dna":fields.date(u"质检异常终止日期",required=True),
        "except_count":fields.function(_get_count,type="integer",multi="get_count",string=u"质检不合格数量"),
        "real_count":fields.function(_get_count,type="integer",multi="get_count",string=u"实际对帐数量")
    }

    _defaults={
        "state":"draft"
    }