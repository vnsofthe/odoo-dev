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
from lxml import etree
_logger = logging.getLogger(__name__)

class rhwl_gene(osv.osv):
    STATE_SELECT_LIST=[
        ('draft', u'草稿'),
        ('cancel', u'检测取消'),
        ('except', u'信息异常'),
        ('except_confirm', u'异常已确认'),
        ('confirm', u'信息已确认'),
        ('dna_except', u'DNA质检不合格'),
        ('dna_ok',u"DNA质检合格"),
        ('ok', u'位点数据已导入'),
        ('report', u'生成报告中'),
        ('report_done', u"报告已生成"),
        ("result_done", u"风险报告确认"),
        ("deliver", u"印刷厂已接收"),
        ('done', u'客户已收货')
    ]
    STATE_SELECT = dict(STATE_SELECT_LIST)

    _name = "rhwl.easy.genes.new"
    _order = "date desc,name asc"

    def _genes_type_get(self, cr, uid, ids, field_names, arg, context=None):
        res = {}
        maps = {}
        for id in ids:
            res[id] = {}.fromkeys(field_names, "")
            type_ids = self.pool.get("rhwl.easy.genes.new.type").search(cr, uid, [("genes_id.id", '=', id)],
                                                                    context=context)
            for i in self.pool.get("rhwl.easy.genes.new.type").browse(cr, uid, type_ids, context=context):
                res[id][maps.get(i.snp, i.snp)] = i.typ
        return res


    _columns = {
        "batch_no": fields.char(u"批次",select=True),
        "name": fields.char(u"基因样本编号", required=True, size=10),
        "date": fields.date(u"送检日期", required=True),
        "cust_name": fields.char(u"会员姓名", required=True, size=50),
        "name_pinying":fields.char(u"姓名(拼音)",size=20),
        "sex": fields.selection([('M', u"男"), ('F', u"女")], u"性别", required=True),
        "height":fields.integer(u"身高cm"),
        "width":fields.float(u"体重kg"),
        "mingzhu":fields.char(u"民族",size=20),
        "identity": fields.char(u"身份证号", size=18),
        "mobile": fields.char(u"手机号码", size=15),
        "contact":fields.char(u"紧急联系人",size=20),
        "contact_tel":fields.char(u"联系人电话",size=20),
        "Permanent_city":fields.char(u"常住城市",size=20),
        "state_id": fields.many2one("res.country.state",string=u'省'),
        "city_id": fields.many2one("res.country.state.city",string=u'市',domain="[('state_id','=',state_id)]"),
        "area_id":fields.many2one("res.country.state.city.area",string=u"区/县",domain="[('city_id','=',city_id)]"),
        "address":fields.char(u"详细地址",size=100),
        "email":fields.char(u"电子邮箱",size=50),
        "weixin":fields.char(u"微信号",size=20),
        "hospital":fields.many2one('res.partner', string=u'送检医院',domain="[('is_company', '=', True), ('customer', '=', True)]", required=True),
        "birthday": fields.date(u"出生日期"),
        "receiv_date": fields.datetime(u"接收时间"),
        "package_id":fields.many2one("rhwl.genes.base.package",string="套餐", required=True,ondelete="restrict"),
        "state": fields.selection(STATE_SELECT_LIST, u"状态"),
        "note": fields.text(u"备注"),
        "img_atta":fields.many2one("ir.attachment","IMG"),
        "img_new":fields.related("img_atta","datas",type="binary"),
        "log": fields.one2many("rhwl.easy.genes.new.log", "genes_id", "Log"),
        "typ": fields.one2many("rhwl.easy.genes.new.type", "genes_id", "Type"),
        "dns_chk": fields.one2many("rhwl.easy.genes.new.check", "genes_id", "DNA_Check"),
        "export_img":fields.boolean("Export Img"),
        "q1_0":fields.boolean(u"无"),
        "q1_1":fields.boolean(u"肿瘤"),
        "q1_2":fields.boolean(u"糖尿病"),
        "q1_3":fields.boolean(u"呼吸性疾病"),
        "q1_4":fields.boolean(u"心脑血管疾病"),
        "q1_5":fields.boolean(u"消化道溃疡"),
        "q1_6":fields.boolean(u"妇科病"),
        "q1_7":fields.boolean(u"过敏史"),
    }
    _sql_constraints = [
        ('rhwl_easy_genes_name_uniq', 'unique(name)', u'样本编号不能重复!'),
    ]
    _defaults = {
        "state": 'draft',
        "cust_prop": "tjs",
        "is_risk":False,
        "is_child":False,
        "export_img":False,
        "q1_0":False,
        "q1_1":False,
        "q1_2":False,
        "q1_3":False,
        "q1_4":False,
        "q1_5":False,
        "q1_6":False,
        "q1_7":False,
    }


    def write(self, cr, uid, id, val, context=None):
        if not context:
            context={}
        if val.get("state","") in ("confirm",):
            obj = self.browse(cr,SUPERUSER_ID,id,context=context)
            identity = val.get("identity",obj.identity)
            if identity and len(identity)==18:
                try:
                    birthday = datetime.datetime.strptime(identity[6:14],"%Y%m%d")
                    day = datetime.datetime.today() - birthday
                    if day.days<0 or day.days>54750:
                        raise osv.except_osv(u"错误",u"身份证号码中的年月日不在合理范围。")
                except:
                    raise osv.except_osv(u"错误",u"身份证号码中的年月日格式错误。")
        if val.get("identity"):
            val["birthday"]=datetime.datetime.strptime(val.get("identity")[6:14],"%Y%m%d")

        if val.has_key("state"):
            val["log"] = [
                [0, 0, {"note": u"状态变更为:" + self.STATE_SELECT.get(val.get("state")), "data": val.get("state"),"user_id":context.get("user_id",uid)}]]

        return super(rhwl_gene, self).write(cr, uid, id, val, context=context)

    def read_group(self, cr, uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False, lazy=True):
        if groupby.count("date")>0 and not orderby:
            orderby="date desc"

        res=super(rhwl_gene,self).read_group(cr,uid,domain,fields,groupby,offset,limit,context=context,orderby=orderby,lazy=lazy)
        return res

    def unlink(self, cr, uid, ids, context=None):
        if isinstance(ids, (long, int)):
            ids = [ids]
        if uid != SUPERUSER_ID: ids = self.search(cr, uid, [("id", "in", ids), ("state", "=", "draft")],
                                                  context=context)
        return super(rhwl_gene, self).unlink(cr, uid, ids, context=context)


    def action_state_confirm(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {"state": "confirm"})

    def action_state_cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {"state": "cancel"})

    def action_state_dna(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {"state": "dna_except"})

    def action_state_dnaok(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {"state": "dna_ok"})

    def action_state_ok(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {"state": "ok"})

    def action_state_reset(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {"state": "draft"})

    def action_state_report(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {"state": "report"})

    def action_state_result_done(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {"state": "result_done"})

    def action_view_pdf(self, cr, uid, ids, context=None):
        return {'type': 'ir.actions.act_url',
                'url': context.get("file_name", "/"),
                'target': 'new'}



    #根据中间日期计算本周期的起迄日期
    def date_between(self,days=20):
        today = datetime.datetime.today()
        if today.day<=days:
            s_date = today-datetime.timedelta(days=today.day+1)
            s_date = datetime.datetime(s_date.year,s_date.month,days+1)
            e_date = today
        else:
            s_date = datetime.datetime(today.year,today.month,days+1)
            e_date = today
        return s_date,e_date



#样本对象操作日志
class rhwl_gene_log(osv.osv):
    _name = "rhwl.easy.genes.new.log"
    _order = "date desc"
    _columns = {
        "genes_id": fields.many2one("rhwl.easy.genes.new", "Genes ID",select=True),
        "date": fields.datetime(u"时间"),
        "user_id": fields.many2one("res.users", u"操作人员"),
        "note": fields.text(u"作业说明"),
        "data": fields.char("Data")
    }

    _defaults = {
        "date": fields.datetime.now,
        "user_id": lambda obj, cr, uid, context: uid,
    }

#疾病检测结果对象
class rhwl_gene_check(osv.osv):
    _name = "rhwl.easy.genes.new.check"
    _columns = {
        "genes_id": fields.many2one("rhwl.easy.genes.new", "Genes ID",select=True),
        "date": fields.date(u"收样日期"),
        "dna_date": fields.date(u"提取日期"),
        "concentration": fields.char(u"浓度", size=5, help=u"参考值>=10"),
        "lib_person": fields.char(u"实验操作人", size=10),
        "od260_280": fields.char("OD260/OD280", size=5, help=u"参考值1.8-2.0"),
        "od260_230": fields.char("OD260/OD230", size=5, help=u"参考值>=2.0"),
        "chk_person": fields.char(u"检测人", size=10),
        "data_loss": fields.char(u"数据缺失率", size=6, help=u"参考值<1%"),
        "loss_person": fields.char(u"判读人", size=10),
        "loss_date": fields.date(u"判读日期"),
        "active": fields.boolean("Active"),
    }

    _defaults = {
        "active": True
    }

#疾病位点数据对象
class rhwl_gene_type(osv.osv):
    _name = "rhwl.easy.genes.new.type"
    _columns = {
        "genes_id": fields.many2one("rhwl.easy.genes.new", "Genes ID",select=True),
        "snp": fields.char("SNP", size=20),
        "typ": fields.char("Type", size=10),
        "active": fields.boolean("Active"),
    }
    _defaults = {
        "active": True
    }

