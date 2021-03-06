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
import urllib2
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

    _name = "rhwl.easy.genes"
    _order = "date desc,name asc"

    def _genes_type_get(self, cr, uid, ids, field_names, arg, context=None):
        res = {}
        maps = {}
        for id in ids:
            res[id] = {}.fromkeys(field_names, "")
            type_ids = self.pool.get("rhwl.easy.genes.type").search(cr, uid, [("genes_id.id", '=', id)],
                                                                    context=context)
            for i in self.pool.get("rhwl.easy.genes.type").browse(cr, uid, type_ids, context=context):
                res[id][maps.get(i.snp, i.snp)] = i.typ
        return res

    def _get_risk_detail(self,cr,uid,ids,field_names,arg,context=None):
        res={}
        for id in ids:
            res[id] = {}.fromkeys(field_names,"")
            obj = self.pool.get("rhwl.easy.genes").browse(cr,uid,id,context=context)
            for o in obj.risk:
                res[id][o.disease_id.code]=o.risk
        return res


    def _get_risk(self,cr,uid,ids,field_names,arg,context=None):
        res={}
        for id in ids:
            res[id]={"risk_count":0,"risk_text":""}
            risk_id = self.pool.get("rhwl.easy.gene.risk").search(cr,uid,[("genes_id.id","=",id),'|',("risk","=","高风险"),("risk","=","低能力")])
            res[id]["risk_count"]=risk_id.__len__()

            t=[]
            for i in self.pool.get("rhwl.easy.gene.risk").browse(cr,uid,risk_id,context=context):
                t.append(i.disease_id.name)
            res[id]["risk_text"]=u"、".join(t)

        return res


    _columns = {
        "batch_no": fields.char(u"批次",select=True),
        "name": fields.char(u"基因样本编号", required=True, size=10),
        "date": fields.date(u"送检日期", required=True),
        "cust_name": fields.char(u"会员姓名", required=True, size=50),
        "sex": fields.selection([('T', u"男"), ('F', u"女")], u"性别", required=True),
        "identity": fields.char(u"身份证号", size=18),
        "mobile": fields.char(u"手机号码", size=15),
        "birthday": fields.date(u"出生日期"),
        "receiv_date": fields.datetime(u"接收时间"),
        "except_note": fields.text(u"信息异常内容"),
        "confirm_note": fields.text(u"信息异常反馈"),
        "state": fields.selection(STATE_SELECT_LIST, u"状态"),
        "note": fields.text(u"备注"),
        "gene_id": fields.char(u"基因编号", size=20),
        "language":fields.selection([("CN",u"中文"),("EN",u"英文"),("RU",u"俄文"),("VN",u"越南文"),("MY",u"马来语"),("ID",u"印度尼西亚语"),("IN",u"印度")],u"报告语种"),
        "cust_prop": fields.selection([("tjs", u"泰济生普通客户"), ("tjs_vip",u"泰济生VIP客户"),("employee", u"内部员工"), ("vip", u"内部VIP客户"), ("extra", u"外部人员")],
                                      string=u"客户属性"),
        "package":fields.selection([("01",u"标准版"),("03",u"尊享版"),("02",u"升级版+"),("04",u"优雅女士"),("06",u"快乐儿童"),("05",u"精英男士")],string=u"产品类别"),
        "package_id":fields.many2one("rhwl.tjs.genes.base.package",string=u"检测项目"),
        "img": fields.binary(u"图片"),
        "img_atta":fields.many2one("ir.attachment","IMG"),
        "img_new":fields.related("img_atta","datas",type="binary"),
        "log": fields.one2many("rhwl.easy.genes.log", "genes_id", "Log"),
        "typ": fields.one2many("rhwl.easy.genes.type", "genes_id", "Type"),
        "dns_chk": fields.one2many("rhwl.easy.genes.check", "genes_id", "DNA_Check"),
        "risk": fields.one2many("rhwl.easy.gene.risk", "genes_id", "Risk"),
        "pdf_file": fields.char(u"中文风险报告", size=100),
        "pdf_file_en": fields.char(u"英文风险报告", size=100),
        "pdf_file_other": fields.char(u"母语风险报告", size=100),
        "is_risk":fields.boolean(u"是高风险"),
        "is_child":fields.boolean(u"是儿童"),
        "risk_count": fields.function(_get_risk, type="integer", string=u'高风险疾病数', multi='risk'),
        "risk_text": fields.function(_get_risk, type="char", string=u'高风险疾病', multi='risk'),
        "snp_name":fields.char("SNP File",size=20),
        "batch_id":fields.many2one("rhwl.easy.genes.batch","Batch_id"),
        "export_img":fields.boolean("Export Img"),
        "ftp_upload":fields.boolean("FTP Upload"),
        "A1":fields.function(_get_risk_detail,type="char",string="A1",multi="risk_detail"),
        "A2":fields.function(_get_risk_detail,type="char",string="A2",multi="risk_detail"),
        "A3":fields.function(_get_risk_detail,type="char",string="A3",multi="risk_detail"),
        "A4":fields.function(_get_risk_detail,type="char",string="A4",multi="risk_detail"),
        "A5":fields.function(_get_risk_detail,type="char",string="A5",multi="risk_detail"),
        "A6":fields.function(_get_risk_detail,type="char",string="A6",multi="risk_detail"),
        "A7":fields.function(_get_risk_detail,type="char",string="A7",multi="risk_detail"),
        "A8":fields.function(_get_risk_detail,type="char",string="A8",multi="risk_detail"),
        "A9":fields.function(_get_risk_detail,type="char",string="A9",multi="risk_detail"),
        "A10":fields.function(_get_risk_detail,type="char",string="A10",multi="risk_detail"),
        "A11":fields.function(_get_risk_detail,type="char",string="A11",multi="risk_detail"),
        "A12":fields.function(_get_risk_detail,type="char",string="A12",multi="risk_detail"),
        "A13":fields.function(_get_risk_detail,type="char",string="A13",multi="risk_detail"),
        "A14":fields.function(_get_risk_detail,type="char",string="A14",multi="risk_detail"),
        "A15":fields.function(_get_risk_detail,type="char",string="A15",multi="risk_detail"),
        "A16":fields.function(_get_risk_detail,type="char",string="A16",multi="risk_detail"),
        "A17":fields.function(_get_risk_detail,type="char",string="A17",multi="risk_detail"),
        "A18":fields.function(_get_risk_detail,type="char",string="A18",multi="risk_detail"),
        "A19":fields.function(_get_risk_detail,type="char",string="A19",multi="risk_detail"),
        "A20":fields.function(_get_risk_detail,type="char",string="A20",multi="risk_detail"),
        "A21":fields.function(_get_risk_detail,type="char",string="A21",multi="risk_detail"),
        "A22":fields.function(_get_risk_detail,type="char",string="A22",multi="risk_detail"),
        "A23":fields.function(_get_risk_detail,type="char",string="A23",multi="risk_detail"),
        "B1":fields.function(_get_risk_detail,type="char",string="B1",multi="risk_detail"),
        "B2":fields.function(_get_risk_detail,type="char",string="B2",multi="risk_detail"),
        "B3":fields.function(_get_risk_detail,type="char",string="B3",multi="risk_detail"),
        "B4":fields.function(_get_risk_detail,type="char",string="B4",multi="risk_detail"),
        "B5":fields.function(_get_risk_detail,type="char",string="B5",multi="risk_detail"),
        "B6":fields.function(_get_risk_detail,type="char",string="B6",multi="risk_detail"),
        "B7":fields.function(_get_risk_detail,type="char",string="B7",multi="risk_detail"),
        "B8":fields.function(_get_risk_detail,type="char",string="B8",multi="risk_detail"),
        "B9":fields.function(_get_risk_detail,type="char",string="B9",multi="risk_detail"),
        "B10":fields.function(_get_risk_detail,type="char",string="B10",multi="risk_detail"),
        "B11":fields.function(_get_risk_detail,type="char",string="B11",multi="risk_detail"),
        "B12":fields.function(_get_risk_detail,type="char",string="B12",multi="risk_detail"),
        "B13":fields.function(_get_risk_detail,type="char",string="B13",multi="risk_detail"),
        "B14":fields.function(_get_risk_detail,type="char",string="B14",multi="risk_detail"),
        "B15":fields.function(_get_risk_detail,type="char",string="B15",multi="risk_detail"),
        "B16":fields.function(_get_risk_detail,type="char",string="B16",multi="risk_detail"),
        "C1":fields.function(_get_risk_detail,type="char",string="C1",multi="risk_detail"),
        "C2":fields.function(_get_risk_detail,type="char",string="C2",multi="risk_detail"),
        "C3":fields.function(_get_risk_detail,type="char",string="C3",multi="risk_detail"),
        "C4":fields.function(_get_risk_detail,type="char",string="C4",multi="risk_detail"),
        "C5":fields.function(_get_risk_detail,type="char",string="C5",multi="risk_detail"),
        "C6":fields.function(_get_risk_detail,type="char",string="C6",multi="risk_detail"),
        "C7":fields.function(_get_risk_detail,type="char",string="C7",multi="risk_detail"),
        "C8":fields.function(_get_risk_detail,type="char",string="C8",multi="risk_detail"),
        "C9":fields.function(_get_risk_detail,type="char",string="C9",multi="risk_detail"),
        "C10":fields.function(_get_risk_detail,type="char",string="C10",multi="risk_detail"),
        "C11":fields.function(_get_risk_detail,type="char",string="C11",multi="risk_detail"),
        "C12":fields.function(_get_risk_detail,type="char",string="C12",multi="risk_detail"),
        "D1":fields.function(_get_risk_detail,type="char",string="D1",multi="risk_detail"),
        "D2":fields.function(_get_risk_detail,type="char",string="D2",multi="risk_detail"),
        "D3":fields.function(_get_risk_detail,type="char",string="D3",multi="risk_detail"),
        "D4":fields.function(_get_risk_detail,type="char",string="D4",multi="risk_detail"),
        "D5":fields.function(_get_risk_detail,type="char",string="D5",multi="risk_detail"),
        "D6":fields.function(_get_risk_detail,type="char",string="D6",multi="risk_detail"),
        "D7":fields.function(_get_risk_detail,type="char",string="D7",multi="risk_detail"),
        "D8":fields.function(_get_risk_detail,type="char",string="D8",multi="risk_detail"),
        "D9":fields.function(_get_risk_detail,type="char",string="D9",multi="risk_detail"),
        "D10":fields.function(_get_risk_detail,type="char",string="D10",multi="risk_detail"),
        "D11":fields.function(_get_risk_detail,type="char",string="D11",multi="risk_detail"),
        "D12":fields.function(_get_risk_detail,type="char",string="D12",multi="risk_detail"),
		"D13":fields.function(_get_risk_detail,type="char",string="D13",multi="risk_detail"),
        "D14":fields.function(_get_risk_detail,type="char",string="D14",multi="risk_detail"),
        "E1":fields.function(_get_risk_detail,type="char",string="E1",multi="risk_detail"),
        "E2":fields.function(_get_risk_detail,type="char",string="E2",multi="risk_detail"),
        "E3":fields.function(_get_risk_detail,type="char",string="E3",multi="risk_detail"),
        "F1":fields.function(_get_risk_detail,type="char",string="F1",multi="risk_detail"),
        "F2":fields.function(_get_risk_detail,type="char",string="F2",multi="risk_detail"),
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
        "language":"CN",
        "ftp_upload":False,
        "package":"01"
    }

    def init(self, cr):
        ids = self.search(cr,SUPERUSER_ID,[("package","=","A")])
        self.write(cr,SUPERUSER_ID,ids,{"package":"01"})

        ids = self.search(cr,SUPERUSER_ID,[("birthday","=",False)])
        for i in ids:
            obj = self.browse(cr,SUPERUSER_ID,i)
            if obj.identity and len(obj.identity)==18:
                try:
                    d=datetime.datetime.strptime(obj.identity[6:14],"%Y%m%d").strftime("%Y/%m/%d")
                    self.write(cr,SUPERUSER_ID,i,{"birthday":d})
                except:
                    pass
        #ids = self.search(cr,SUPERUSER_ID,[("package_id","=",False)])
        #for i in self.browse(cr,SUPERUSER_ID,ids):
        #    pid = self.pool.get("rhwl.tjs.genes.base.package").search(cr,SUPERUSER_ID,[("code","=",i.package)])
        #    self.write(cr,SUPERUSER_ID,i.id,{"package_id":pid[0]})



    def create(self, cr, uid, val, context=None):
        val["log"] = [[0, 0, {"note": u"资料新增", "data": "create"}]]
        if not val.get("batch_no",None):
            val["batch_no"]=datetime.datetime.strftime(datetime.datetime.today(),"%m-%d")
        if val.has_key("package") and (not val.has_key("package_id")):
            p_id = self.pool.get("rhwl.tjs.genes.base.package").search(cr,uid,[("code","=",val.get("package"))])
            val["packaage_id"] = p_id[0]
        if val.has_key("package_id") and (not val.has_key("package")):
            p_obj = self.pool.get("rhwl.tjs.genes.base.package").browse(cr,uid,val.get("package_id"))
            val["package"] = p_obj.code
        return super(rhwl_gene, self).create(cr, uid, val, context=context)

    def write(self, cr, uid, id, val, context=None):
        if not context:
            context={}
        if val.has_key("package") and (not val.has_key("package_id")):
            p_id = self.pool.get("rhwl.tjs.genes.base.package").search(cr,uid,[("code","=",val.get("package"))])
            p_obj = self.pool.get("rhwl.tjs.genes.base.package").browse(cr,uid,p_id,context=context)
            val["packaage_id"] = p_obj.id
        if val.has_key("package_id") and (not val.has_key("package")):
            p_obj = self.pool.get("rhwl.tjs.genes.base.package").browse(cr,uid,val.get("package_id"))
            val["package"] = p_obj.code

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
        if val.get("identity") and len(val.get("identity"))==18:
            val["birthday"]=datetime.datetime.strptime(val.get("identity")[6:14],"%Y%m%d")

        if val.has_key("state"):
            val["log"] = [
                [0, 0, {"note": u"状态变更为:" + self.STATE_SELECT.get(val.get("state")), "data": val.get("state"),"user_id":context.get("user_id",uid)}]]
            #如果重新变更为已收货，则PDF要重新上传
            if val.get("state")=="done":
                val["ftp_upload"]=False
        if val.has_key("img"):
            #log_id = self.pool.get("rhwl.easy.genes.log").search(cr,uid,[("genes_id","in",id),("data","=","expimg")])
            #if log_id:
            #    self.pool.get("rhwl.easy.genes.log").write(cr,uid,log_id,{"data":"expimg,1"},context=context)
            val["log"] = [[0, 0, {"note": u"图片变更", "data": "img"}]]
            val["export_img"]=False
            if context.has_key("name"):
                obj_name = context["name"]
            else:
                obj = self.browse(cr,SUPERUSER_ID,id,context=context)
                obj_name = obj.name

            vals={
                "name":obj_name,
                "datas_fname":obj_name+".jpg",
                "description":obj_name+" information to IMG",
                "res_model":"rhwl.easy.genes",
                "res_id":id[0],
                "create_date":fields.datetime.now,
                "create_uid":SUPERUSER_ID,
                "datas":val.get("img"),
            }
            atta_obj = self.pool.get('ir.attachment')
            #if obj.img_atta:
            #    atta_obj.unlink(cr,SUPERUSER_ID,obj.img_atta.id)
            atta_id = atta_obj.create(cr,SUPERUSER_ID,vals)
            val["img_atta"]=atta_id
            val.pop("img")

        return super(rhwl_gene, self).write(cr, uid, id, val, context=context)

    def read_group(self, cr, uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False, lazy=True):

        if groupby.count("date")>0 and not orderby:
            orderby="date desc"
        else:
            orderby="id desc"

        res=super(rhwl_gene,self).read_group(cr,uid,domain,fields,groupby,offset,limit,context=context,orderby=orderby,lazy=lazy)
        return res

    def unlink(self, cr, uid, ids, context=None):
        if isinstance(ids, (long, int)):
            ids = [ids]
        if uid != SUPERUSER_ID: ids = self.search(cr, uid, [("id", "in", ids), ("state", "=", "draft")],
                                                  context=context)
        return super(rhwl_gene, self).unlink(cr, uid, ids, context=context)

    def action_state_except(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        if context.get("view_type") == "tree":
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'res_model': 'rhwl.easy.genes.popup',
                'view_mode': 'form',
                'name': u"异常说明",
                'target': 'new',
                'context': {'col': 'except_note'},
                'flags': {'form': {'action_buttons': False}}}

        return self.write(cr, uid, ids, {"state": "except"})

    def action_state_except_confirm(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        if context.get("view_type") == "tree":
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'res_model': 'rhwl.easy.genes.popup',
                'view_mode': 'form',
                'name': u"回馈说明",
                'target': 'new',
                'context': {'col': 'confirm_note'},
                'flags': {'form': {'action_buttons': False}}}

        return self.write(cr, uid, ids, {"state": "except_confirm"})


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

    #取得指定id列表的所有位点数据
    def get_gene_type_list(self,cr,uid,ids,context=None):
        data={}
        for i in self.browse(cr,uid,ids,context=context):
            sex=i.sex.encode("utf-8") if i.sex.encode("utf-8") == 'F' else 'M'
            key = i.name.encode("utf-8")
            if not data.has_key(sex):
                data[sex]={}
            if not data[sex].has_key(key):
                data[sex][key]={"name":key,
                           "cust_name":i.cust_name.encode("utf-8"),
                                "language":i.language.encode("utf-8")
                           }

            for t in i.typ:
                k = t.snp.encode("utf-8")
                data[sex][key][k]=(t.typ).encode("utf-8").replace("/","")

        return data

    #导出样本信息图片
    def export_genes_img(self,cr,uid,context=None):
        upload_path = os.path.join(os.path.split(__file__)[0], "static/local/upload/tjs")
        d=os.path.join(upload_path,u"样本信息图片")
        if not os.path.exists(d):
            os.mkdir(d)
        all_ids = self.search(cr,uid,[("cust_prop","in",["tjs","tjs_vip"]),("export_img","=",False)],context=context)
        #pic_ids = self.search(cr,uid,[("cust_prop","in",["tjs","tjs_vip"]),("export_img","=",False)],context=context)
        #for i in pic_ids:
        #    all_ids.remove(i)
        filestore=tools.config.filestore(cr.dbname)
        for i in self.browse(cr,uid,all_ids,context=context):
            if not i.img_atta:continue
            if len(i.date.split("/"))>1:
                tname = ".".join(i.date.split('/')[1:]) + u"会_图片"
            else:
                tname = ".".join(i.date.split('-')[1:]) + u"会_图片"
            tname = os.path.join(d,tname)
            if not os.path.exists(tname):
                os.mkdir(tname)
            att_obj = self.pool.get('ir.attachment').browse(cr,uid,i.img_atta.id,context=context)
            if not os.path.exists(os.path.join(filestore,att_obj.store_fname)):continue
            if (not os.path.exists(os.path.join(tname,i.name+u"_"+i.cust_name+u".jpg"))) or os.stat(os.path.join(filestore,att_obj.store_fname)).st_size != os.stat(os.path.join(tname,i.name+u"_"+i.cust_name+u".jpg")).st_size:
                shutil.copy(os.path.join(filestore,att_obj.store_fname),os.path.join(tname,i.name+u"_"+i.cust_name+u".jpg"))
            self.write(cr,uid,i.id,{"log":[[0,0,{"note":u"图片导出","data":"expimg"}]],"export_img":True})

    #导出样本位点数据到报告生成服务器
    def create_gene_type_file(self,cr,uid,ids,context=None):
        self.pool.get("rhwl.genes.picking").export_box_genes(cr,uid,context=context) #先导出已经分箱的样本
        self.export_genes_img(cr,uid,context=context) #导出图片信息
        cr.execute("select package,count(*) from rhwl_easy_genes where state='ok' group by package")
        for i in cr.fetchall():
            self.create_gene_type_file_package(cr,uid,ids,i[0],context=context)

    def create_gene_type_file_package(self, cr, uid, ids, package,context=None):

        ids = self.search(cr, uid, [("state", "=", "ok"),("package","=",package),("typ","!=",False)], order="batch_no,name",limit=200,context=context)
        if not ids:return

        if isinstance(ids, (long, int)):
            ids = [ids]
        data = self.get_gene_type_list(cr,uid,ids,context=context)
        if package=="01":
            snp_name = "snp_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            fpath = os.path.join(os.path.split(__file__)[0], "static/remote/snp")
        else:
            pid = self.pool.get("rhwl.tjs.genes.base.package").search(cr,SUPERUSER_ID,[("code","=",package)])
            pobj = self.pool.get("rhwl.tjs.genes.base.package").browse(cr,SUPERUSER_ID,pid,context=context)
            snp_name = pobj.report_no+"_"+datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            fpath = os.path.join(os.path.split(__file__)[0], "static/tjs_new_remote/snp")

        fname = os.path.join(fpath, snp_name + ".txt")
        header=[]
        f = open(fname, "w+")

        for s in ["F","M"]:
            if not data.has_key(s):continue
            data_list=data[s].keys()
            data_list.sort()
            for k in data_list:
                line_row=[data[s][k]["name"],data[s][k]["cust_name"],s,data[s][k]["language"]]
                if not header:
                    header = data[s][k].keys()
                    header.remove("name")
                    header.remove("cust_name")
                    header.remove("language")
                    header.sort()
                    f.write("编号\t姓名\t性别\t语种\t" + "\t".join(header) + '\n')
                for i in header:
                    line_row.append(data[s][k][i])
                f.write("\t".join(line_row) + '\n')
        f.close()
        os.system("chmod 777 "+fname)
        self.action_state_report(cr, uid, ids, context=context)
        self.write(cr,uid,ids,{"snp_name":snp_name},context=context)
        js={
            "first":"易感样本检测结果转报告生成：",
            "keyword1":"即时",
            "keyword2":"本次转出样本%s笔，等待生成报告。" %(len(ids),),
            "keyword3":fields.datetime.now(),
            "remark":"以上数据仅供参考，详细情况请登录Odoo查询。"
        }
        self.pool.get("rhwl.weixin.base").send_template2(cr,uid,js,"is_lib_import",context=context)

    #发送文件大小错误微信通知
    def pdf_size_error(self,cr,uid,file,lens,context=None):
        s=os.stat(file).st_size
        if s/1024/1024<16 or ( (lens<10 and s/1024/1024>50) or (lens>=10 and s/1024/1024>90) ):
            js={
                "first":"易感样本报告接收出错：",
                "keyword1":"即时",
                "keyword2":"样本报告%s文件大小不正确。" %(os.path.split(file)[-1],),
                "keyword3":fields.datetime.now(),
                "remark":"以上数据仅供参考，详细情况请登录服务器查询。"
            }
            self.pool.get("rhwl.weixin.base").send_template2(cr,uid,js,"is_jobmanager",context=context)
            return True
        else:
            return False

    #接收风险报告
    def get_gene_pdf_file(self, cr, uid, context=None):
        #_logger.warn("cron job get_gene_pdf_file")
        pdf_files=[]
        model_path=os.path.split(__file__)[0]
        fpath = os.path.join(model_path, "static/remote/report")
        for f in os.listdir(fpath):
            pdf_files.append(os.path.join(fpath,f))
        fpath = os.path.join(model_path, "static/tjs_new_remote/report")
        for f in os.listdir(fpath):
            pdf_files.append(os.path.join(fpath,f))

        tpath = os.path.join(model_path, "static/local/report")
        pdf_count = 0
        last_week = time.time() - 60*60*24*3
        self.pool.get("rhwl.genes.picking")._clear_picking_dict()
        for newfile in pdf_files:
            #newfile = os.path.join(fpath, f)
            if not os.path.isdir(newfile):continue
            for f1 in os.listdir(newfile):
                name_list = re.split("[_\.]",f1) #分解文件名称
                #文件名分为六种模式

                if self.pdf_size_error(cr,uid,os.path.join(newfile, f1),len(name_list),context=context):
                    continue

                if len(name_list)==2:
                    f2 = ".".join(name_list)
                    shutil.move(os.path.join(newfile, f1), os.path.join(tpath, f2))
                    ids = self.search(cr, uid, [("name", "=", f2.split(".")[0])])
                    if ids:
                        self.write(cr, uid, ids,
                                   {"pdf_file": "rhwl_gene/static/local/report/" + f2, "state": "report_done"})
                        pdf_count += 1
                elif len(name_list)==3:
                    f2 = ".".join([name_list[0],name_list[2]])
                    shutil.move(os.path.join(newfile, f1), os.path.join(tpath, f2))
                    ids = self.search(cr, uid, [("name", "=", f2.split(".")[0])])
                    if ids:
                        self.write(cr, uid, ids,
                                   {"pdf_file": "rhwl_gene/static/local/report/" + f2, "state": "report_done"})
                        pdf_count += 1
                elif len(name_list)==4:
                    #23999945_张三_CN.pdf
                    lang = name_list[2]
                    col_name="pdf_file"

                    if lang=="CN":
                        f2 = ".".join([name_list[0],name_list[3]])
                    else:
                        f2 = ".".join([name_list[0]+"_"+name_list[2],name_list[3]])
                        if lang=="EN":
                            col_name = "pdf_file_en"
                        else:
                            col_name = "pdf_file_other"
                    shutil.move(os.path.join(newfile, f1), os.path.join(tpath, f2))
                    ids = self.search(cr, uid, [("name", "=", f2.split(".")[0])])
                    if ids:
                        self.write(cr, uid, ids,
                                   {col_name: "rhwl_gene/static/local/report/" + f2, "state": "report_done"})
                        pdf_count += 1

                elif len(name_list)==6 or len(name_list)==10:
                    gene_no = name_list[2]
                    if len(f.split("_"))==3:
                        picking_no = f.split("_")[1]
                    else:
                        picking_no = self.pool.get("rhwl.genes.picking")._get_picking_from_genes(cr,uid,gene_no,context=context)
                    if not picking_no:continue
                    ppath=os.path.join(tpath,picking_no)
                    if not os.path.exists(ppath):
                        os.mkdir(ppath)
                    shutil.move(os.path.join(newfile, f1), os.path.join(ppath, f1))

            if os.path.getmtime(newfile) < last_week:
                os.rmdir(newfile)
        cr.commit()
        if pdf_count>0:
            js={
                "first":"易感样本报告接收：",
                "keyword1":"即时",
                "keyword2":"本次接收样本报告%s本。" %(pdf_count,),
                "keyword3":fields.datetime.now(),
                "remark":"以上数据仅供参考，详细情况请登录Odoo查询。"
            }
            self.pool.get("rhwl.weixin.base").send_template2(cr,uid,js,"is_jobmanager",context=context)

        #分析风险数据
        fpath = os.path.join(model_path, "static/remote/excel")
        tpath = os.path.join(model_path, "static/local/excel")
        for f in os.listdir(fpath):
            if f.split(".")[-1]!="xls":continue
            if f.split("_")[0]=="box":continue
            if os.path.isfile(os.path.join(tpath, f)):os.remove(os.path.join(tpath, f)) #删除目标位置相同的文件
            shutil.move(os.path.join(fpath, f), os.path.join(tpath, f))
            fs = open(os.path.join(tpath, f),"r")
            res = fs.readlines()
            fs.close()
            risk = res[0].replace("\n","").split("\t")[3:]
            disease = self.pool.get("rhwl.gene.disease")
            disease_dict={} #疾病在表中的id
            dict_index=3
            #检查风险报告中的疾病基本数据
            for r in risk:
                if not r:continue
                r_id = disease.search(cr,uid,[("name","=",r.decode("utf-8"))])
                if not r_id:
                    shutil.move(os.path.join(tpath, f),os.path.join(fpath, f))
                    _logger.warn(u"疾病名称[%s]在基本数据中不存在。" %(r.decode("utf-8"),))
                    return
                disease_dict[dict_index]=[r,r_id[0]]
                dict_index +=1

            for l in res[1:]:
                is_risk=False
                l = l.replace("\n","").split("\t")
                gene_id = self.pool.get("rhwl.easy.genes").search(cr,uid,[("name","=",l[0].decode("utf-8"))])
                if not gene_id:
                    _logger.warn(u"样本编号[%s]在基本数据中不存在。" %(l[0].decode("utf-8"),))
                else:
                    risk_id=self.pool.get("rhwl.easy.gene.risk").search(cr,uid,[("genes_id","in",gene_id)])
                    if risk_id:
                        self.pool.get("rhwl.easy.gene.risk").write(cr,uid,risk_id,{"active":False})
                    val=[]
                    for k in disease_dict.keys():
                        val.append([0, 0, {"disease_id": disease_dict[k][1], "risk": l[k]}])
                        if l[k]=="高风险" or l[k]=="低能力":is_risk=True
                    self.pool.get("rhwl.easy.genes").write(cr,uid,gene_id,{"is_risk":is_risk,"risk":val})
        self.pool.get("rhwl.genes.picking").create_box(cr,uid,context=context) #接收完风险数据以后，重新调用分箱

    #样本状态数据微信通知
    def weixin_notice_template2(self,cr,uid,context=None):
        s_date,e_date = self.date_between(20)
        #统计今日收样笔数
        cr.execute("""select count(*) from rhwl_easy_genes where cust_prop in ('tjs','tjs_vip') and create_date::date = now()::date""")
        for i in cr.fetchall():
            today_count = i[0]

        #下次送货数据
        pick_count=0
        pick_id = self.pool.get( "rhwl.genes.picking").search(cr,uid,[("date",">=",datetime.datetime.today()),("state","!=","done")],order="date",limit=1)
        if pick_id:
            pick_obj = self.pool.get( "rhwl.genes.picking").browse(cr,uid,pick_id,context=context)
            pick_count = pick_obj.files

        #本期样本笔数
        idscount = self.search_count(cr,uid,[("date",">=",s_date),("date","<=",e_date),("cust_prop","in",["tjs","tjs_vip"])],context=context)
        cr.execute("""with d as (select batch_no,state,count(*) as c,date from rhwl_easy_genes where cust_prop in ('tjs','tjs_vip') group by batch_no,state,date order by batch_no)
                    select *
                    from d dd
                    where not exists(select * from d where state='done' and d.batch_no=dd.batch_no)""")


        v_count0=0
        v_count1=0
        v_count2=0
        v_count3=0
        v_count4=0
        v_count5 = 0
        dna_rate={}
        not_dna_except={} #记录不报告质检比率的批次
        wait_receiv=[]
        for i in cr.fetchall():
            if not dna_rate.has_key(i[0]):
                dna_rate[i[0]]={"count":0,"except":0}
            dna_rate[i[0]]["count"] =dna_rate[i[0]]["count"]+i[2]
            if i[1]=='draft':
                batch_id = self.pool.get("rhwl.easy.genes.batch").search(cr,uid,[("name","=",i[0]),("post_date","!=",False)])
                if not batch_id:
                    v_count0 += i[2] #待收件
                    wait_receiv.append(str(i[2])+"/"+".".join((i[3].split("-")[1:])))
                not_dna_except[i[0]]=True

                #样本是草稿，但如果已经设定实验收件日期，则数据归为实验中
                batch_id = self.pool.get("rhwl.easy.genes.batch").search(cr,uid,[("name","=",i[0]),("lib_date","!=",False)])
                if batch_id:
                    v_count1 += i[2] #待检测
            elif i[1] in ['except','except_confirm','confirm']:
                v_count1 += i[2] #待检测
                not_dna_except[i[0]]=True
            elif i[1] in ['dna_ok','ok','report']:
                v_count2 += i[2] #待生成报告
            elif i[1] == 'dna_except':
                v_count3 += i[2] #质检异常
                dna_rate[i[0]]["except"] = dna_rate[i[0]]["except"] + i[2]
            elif i[1] in ['report_done',"result_done","deliver",]:
                v_count4 += i[2] #待送货
            elif i[1] in ['done']:
                v_count5 += i[2] #已完成
        except_rate=[]
        for k,v in dna_rate.items():
            if not not_dna_except.get(k,False):
                except_rate.append(k.encode("utf-8")+"="+str(v["except"])+"/"+str(v["count"]))
        js={
            "first":"易感样本状况统计：",
            "keyword1":"本期从(%s-%s)"%(s_date.strftime("%Y/%m/%d"),e_date.strftime("%Y/%m/%d")),
            "keyword2":"今日送样%s,在途%s%s，实验中%s，排版中%s，已出报告%s(质检不合格%s，待印刷%s,下次送货%s)。本期总计%s笔。" %(today_count,v_count0,("["+",".join(wait_receiv)+"]" if wait_receiv else ""),v_count1,v_count2,v_count4+v_count3+v_count5,v_count3,v_count4-pick_count,pick_count,idscount),
            "keyword3":(datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime("%Y/%m/%d %H:%M:%S"),
            "remark":"以上数据仅供参考，详细情况请登录Odoo查询。"
        }
        self.pool.get("rhwl.weixin.base").send_template2(cr,uid,js,"is_notice",context=context)

    #样本实验进度微信提醒
    def weixin_notice_template3(self,cr,uid,context=None):
        cr.execute("""select date,count(*) c
                      from rhwl_easy_genes
                      where cust_prop in ('tjs','tjs_vip')
                      and state in ('confirm','except_confirm','draft','except')
                      and date<=(now() - interval '4 day')::date group by date""")
        res=[]
        for i in cr.fetchall():
            res.append("日期:"+str(i[0])+",样本数:"+str(i[1]))
        if res:
            js={
                "first":"易感样本实验进度提醒：",
                "keyword1":"4天之前送达样本",
                "keyword2":";".join(res),
                "keyword3":(datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime("%Y/%m/%d %H:%M:%S"),
                "remark":"亲爱的实验同事，以上样本，须在本周日之前出结果，否则就会超出和客户约定的送货周期。收到本条消息时，请及时和运营部同事确认，谢谢。"
            }
            self.pool.get("rhwl.weixin.base").send_template2(cr,uid,js,"is_library",context=context)
            content="易感样本实验进度提醒，统计周期：%s,提醒说明：%s,%s"%(js["keyword1"],js["keyword2"],js["remark"])
            self.pool.get("rhwl.weixin.base").send_qy_text(cr,uid,'rhwlyy',"is_library",content,context=context)

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

    def action_ftp_upload(self,cr,uid,ids,context=None):
        self.ftp_uploads(cr,uid,ids,context=context)

    def ftp_uploads(self,cr,uid,ids,context=None):
        ids = self.search(cr,uid,[("state","=","done"),("ftp_upload","=",False),("cust_prop","in",["tjs","tjs_vip"])],limit=100)
        for i in self.browse(cr,uid,ids,context=context):
            os.system("scp /data/odoo/file/report/%s*.pdf rhwlwz@119.39.48.126:/home/rhwlwz/ftp/"%(i.name.encode("utf-8"),))
            self.write(cr,uid,i.id,{"ftp_upload":True})

    #导出样本位点数据到报告生成服务器
    def temp_export(self, cr, uid, ids, context=None):
        ids = self.search(cr, uid, [("name", "in", ['3599999021','3599999843','3599998984','3599999187','3599999887'])], order="batch_no,name",limit=200,context=context)
        if not ids:return

        if isinstance(ids, (long, int)):
            ids = [ids]
        data = self.get_gene_type_list(cr,uid,ids,context=context)
        snp_name = "snp_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        fpath = os.path.join(os.path.split(__file__)[0], "static/remote/snp/hebin")
        fname = os.path.join(fpath, snp_name + ".txt")
        header=[]
        f = open(fname, "w+")

        for s in ["F","M"]:
            if not data.has_key(s):continue
            data_list=data[s].keys()
            data_list.sort()
            for k in data_list:
                line_row=[data[s][k]["name"],data[s][k]["cust_name"],s]
                if not header:
                    header = data[s][k].keys()
                    header.remove("name")
                    header.remove("cust_name")
                    header.sort()
                    f.write("编号\t姓名\t性别\t" + "\t".join(header) + '\n')
                for i in header:
                    line_row.append(data[s][k][i])
                f.write("\t".join(line_row) + '\n')
        f.close()

    #在线接收T客户样本信息
    def action_get_online_genes(self,cr,uid,ids,context=None):
        today= datetime.datetime.today().strftime("%Y-%m-%d")
        before_day = (datetime.datetime.today()+datetime.timedelta(days=-3)).strftime("%Y-%m-%d")
        u = urllib2.urlopen("http://genereport.taiji-sun.com/file/API/SampleInfoToGenetalks?beginTime="+before_day+"&endTime="+today)
        data = u.readlines()

        if not data:return
        content = eval(data[0])
        package={
            "01":"01",
            "02":"02",
            "03":"03",
            "04":"04",
            "05":"05",
            "06":"06"
        }
        batch_no={}
        for i in  content:
            id = self.search(cr,uid,[("name","=",i["SampleCode"])],context=context)
            if id:continue
            if not package.has_key(i["SampleCatalogCode"]):
                raise osv.except_osv("Error",u"检测代号[%s]名称[%s]在系统未设置，不可以转入。"%(i["SampleCatalogCode"],i["SampleCatalogName"]))
            sex = i["Gender"]==u"男" and "T" or "F"
            date = i["CreatedTime"].split(" ")[0]
            cust_prop = i["IsVIP"]==u"否" and "tjs" or "tjs_vip"
            idt = i["IDNumber"]

            is_child = True if len(idt)==18 and int(idt[6:10])>=(datetime.datetime.today().year-12) and int(idt[6:10])<(datetime.datetime.today().year) else False
            birthday = False
            if idt and len(idt)==18:
                try:
                    birthday = datetime.datetime.strptime(idt[6:14],"%Y%m%d").strftime("%Y/%m/%d")
                except:
                    pass
            if not batch_no.has_key(date):
                batch_no[date]={}
            if batch_no.get(date).get(package.get(i["SampleCatalogCode"])):
                max_no=batch_no.get(date).get(package.get(i["SampleCatalogCode"]))
            else:
                cr.execute("select max(batch_no) from rhwl_easy_genes where cust_prop in ('tjs','tjs_vip') and package='%s' "%(package.get(i["SampleCatalogCode"])))
                max_no=None
                for no in cr.fetchall():
                    max_no = no[0]
                if not max_no:max_no=package.get(i["SampleCatalogCode"])+"-000"
                if package.get(i["SampleCatalogCode"])=="01":
                    max_no=str(int(max_no)+1).zfill(3)
                else:
                    max_no=max_no[0:3]+str(int(max_no[3:])+1).zfill(3)
                batch_no[date][package.get(i["SampleCatalogCode"])]=max_no

            self.create(cr,uid,{"name":i["SampleCode"],"receiv_date":i["RecivedTime"],"identity":i["IDNumber"],"cust_name":i["ClientName"],"sex":sex,"date":date,"cust_prop":cust_prop,"is_child":is_child,"birthday":birthday,"package":package.get(i["SampleCatalogCode"]),"batch_no":max_no},context=context)


#样本对象操作日志
class rhwl_gene_log(osv.osv):
    _name = "rhwl.easy.genes.log"
    _order = "date desc"
    _columns = {
        "genes_id": fields.many2one("rhwl.easy.genes", "Genes ID",select=True),
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
    _name = "rhwl.easy.genes.check"
    _columns = {
        "genes_id": fields.many2one("rhwl.easy.genes", "Genes ID",select=True),
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
    _name = "rhwl.easy.genes.type"
    _columns = {
        "genes_id": fields.many2one("rhwl.easy.genes", "Genes ID",select=True),
        "snp": fields.char("SNP", size=20),
        "typ": fields.char("Type", size=10),
        "active": fields.boolean("Active"),
    }
    _defaults = {
        "active": True
    }

#疾病风险对象
class rhwl_gene_risk(osv.osv):
    _name = "rhwl.easy.gene.risk"
    _columns = {
        "genes_id": fields.many2one("rhwl.easy.genes", "Genes ID",select=True),
        "disease_id": fields.many2one("rhwl.gene.disease", string=u"疾病名"),
        "risk": fields.char(u"风险", size=20),
        "active": fields.boolean("Active"),
    }
    _defaults = {
        "active": True
    }

#报告书信息异常
class rhwl_report_except(osv.osv):
    _name = "rhwl.easy.genes.report.except"
    _columns={
        "name":fields.many2one("rhwl.easy.genes",u"基因样本编号",required=True),
        "cust_name": fields.char(u"会员姓名(原)", readonly=True, size=10),
        "sex": fields.selection([('T', u"男"), ('F', u"女")], u"性别(原)", readonly=True),
        "identity": fields.char(u"身份证号(原)", size=18,readonly=True),
        "cust_name_n": fields.char(u"会员姓名(新)", required=True, size=10),
        "sex_n": fields.selection([('T', u"男"), ('F', u"女")], u"性别(新)", required=True),
        "identity_n": fields.char(u"身份证号(新)", size=18),
        "state":fields.selection([("draft",u"草稿"),("confirm",u"确认")]),
        "user_id":fields.many2one("res.users",u"异常确认人",required=True),
        "date":fields.date(u"确认日期",required=True),
        "note":fields.text(u"备注"),
    }

    _defaults={
        "state":'draft',
    }

    @api.onchange("name")
    def onchange_name(self):
        self.cust_name = self.name.cust_name
        self.sex = self.name.sex
        self.identity = self.name.identity
        self.cust_name_n = self.name.cust_name
        self.sex_n = self.name.sex
        self.identity_n = self.name.identity

    def create(self,cr,uid,val,context=None):
        obj = self.pool.get("rhwl.easy.genes").browse(cr,uid,val.get("name"),context=context)
        val["cust_name"]=obj.cust_name
        val["sex"] = obj.sex
        val["identity"] = obj.identity
        return super(rhwl_report_except,self).create(cr,uid,val,context=context)

    def action_state_confirm(self,cr,uid,ids,context=None):
        self.write(cr,uid,ids,{"state":"confirm"},context=context)
        obj = self.browse(cr,uid,ids,context=context)
        if obj.cust_name != obj.cust_name_n or obj.sex != obj.sex_n or obj.identity != obj.identity_n:
            self.pool.get("rhwl.easy.genes").write(cr,uid,obj.name.id,{"cust_name":obj.cust_name_n,"sex":obj.sex_n,"identity":obj.identity_n},context=context)
            if obj.name.state.encode("utf-8") in ('report','report_done',"result_done","deliver",'done'):
                self.pool.get("rhwl.easy.genes").write(cr,uid,obj.name.id,{"state":"ok"},context=context)

#批号时间段统计
class rhwl_gene_batch(osv.osv):
    _name = "rhwl.easy.genes.batch"
    _order = "name desc"

    def str2date(self,str):
        if not str:return None
        return datetime.datetime.strptime(str.split(" ")[0],"%Y-%m-%d")

    def _get_genes1(self,cr,uid,ids,field_names,arg,context=None):
        res=dict.fromkeys(ids,{})
        genes_table = self.pool.get("rhwl.easy.genes")
        log_table = self.pool.get("rhwl.easy.genes.log")

        for i in ids:
            res[i] = dict.fromkeys(field_names,None)
            gene_id = genes_table.search(cr,uid,[("batch_id","=",i)],context=context)

            if not gene_id:continue
            gene_obj = genes_table.browse(cr,uid,gene_id[0],context=context)

            res[i]["date"] = self.str2date(gene_obj.date)
            res[i]["qty"] = len(gene_id)
            res[i]["imgs"] = genes_table.search_count(cr,uid,[("batch_id","=",i),("img_atta","!=",False)],context=context)
            log_id = log_table.search(cr,uid,[("genes_id","in",gene_id),("data","=","DNA")],order="date desc",context=context)
            if log_id:
                log_id = log_id[0]
                log_obj = log_table.browse(cr,uid,log_id,context=context)
                res[i]["dna_date"] = self.str2date(log_obj.date)
            else:
                res[i]["dna_date"] = None

            log_id = log_table.search(cr,uid,[("genes_id","in",gene_id),("data","=","SNP")],order="date desc",context=context)
            if log_id:
                log_id = log_id[0]
                log_obj = log_table.browse(cr,uid,log_id,context=context)
                res[i]["snp_date"] = self.str2date(log_obj.date)
            else:
                res[i]["snp_date"] = None
            gene_id = genes_table.search(cr,uid,[("batch_id","=",i),("state","=","dna_except")],context=context)
            res[i]["dna_qty"] = len(gene_id)
            res[i]["dna_rate"] = str(round((res[i]["dna_qty"]*1.0)/res[i]["qty"],4)*100)+"%"

            cr.execute("select name,lib_date from rhwl_easy_genes_batch where id="+str(i))

            obj = cr.fetchall()

            batch_no,lib_date = obj[0]
            if lib_date:lib_date = self.str2date(lib_date)
            if res[i]["date"] and lib_date:
                res[i]["express_days"] = (lib_date - res[i]["date"]).days
            if lib_date and res[i]["snp_date"]:
                res[i]["library_days"] = (res[i]["snp_date"] - lib_date).days
                wd=lib_date.weekday()
                if res[i]["library_days"]<=7-wd:
                    res[i]["library_result"] = 3
                elif res[i]["library_days"]<=(7-wd)+7:
                    res[i]["library_result"] = 2
                elif res[i]["library_days"]<=(7-wd)+14:
                    res[i]["library_result"] = 1
                else:
                    res[i]["library_result"] = 0
            line_id = self.pool.get("rhwl.genes.picking.line").search(cr,uid,[("batch_no","=",batch_no)],order="id desc",context=context)
            if line_id:
                line_id = line_id[0]
                line_obj = self.pool.get("rhwl.genes.picking.line").browse(cr,uid,line_id,context=context)
                res[i]["send_date"] = self.str2date(line_obj.picking_id.date)
                res[i]["real_date"] = self.str2date(line_obj.picking_id.real_date)
                if res[i]["date"] and res[i]["real_date"]:
                    res[i]["all_days"] = (res[i]["real_date"] - res[i]["date"]).days

        return res

    _columns={
        "name":fields.char(u"批次",required=True),
        "date":fields.function(_get_genes1,type="date",string=u"送检日期",store=True,multi="get_genes1"),
        "qty":fields.function(_get_genes1,type="integer",string=u"送检数量",multi="get_genes1"),
        "post_date":fields.date(u'快递收件日期'),
        "lib_date":fields.date(u'实验签收日期'),
        "express_days":fields.function(_get_genes1,type="integer",arg="name",string=u"收样天数",multi="get_genes1"),
        "dna_date":fields.function(_get_genes1,type="date",string=u"质检确认日期",multi="get_genes1"),
        "snp_date":fields.function(_get_genes1,type="date",string=u"位点导入日期",multi="get_genes1"),
        "dna_qty":fields.function(_get_genes1,type="integer",string=u"质检不合格数量",multi="get_genes1"),
        "dna_rate":fields.function(_get_genes1,type="char",string=u"质检不合格比率(%)",multi="get_genes1"),
        "library_days":fields.function(_get_genes1,type="integer",string=u"实验天数",multi="get_genes1"),
        "library_result":fields.function(_get_genes1,type="integer",string=u"实验进度",multi="get_genes1"),
        "send_date":fields.function(_get_genes1,type="date",string=u"预计发货日期",multi="get_genes1"),
        "real_date":fields.function(_get_genes1,type="date",string=u"实际发货日期",multi="get_genes1"),
        "all_days":fields.function(_get_genes1,type="integer",string=u"送货周期",multi="get_genes1"),
        "imgs":fields.function(_get_genes1,type="integer",string=u"已拍照数",multi="get_genes1"),

    }

    def create(self,cr,uid,val,context=None):
        gene_id = self.pool.get("rhwl.easy.genes").search(cr,uid,[("batch_no","=",val.get("name"))],context=context)
        if not gene_id:
            raise osv.except_osv(u"错误",u"批次错误，请输入正确的批次号。")
        id = super(rhwl_gene_batch,self).create(cr,uid,val,context=context)
        self.pool.get("rhwl.easy.genes").write(cr,uid,gene_id,{"batch_id":id},context=context)
        return id

    def action_button(self,cr,uid,ids,context=None):
        pass

#疾病分类对象
class rhwl_gene_disease_type(osv.osv):
    _name = "rhwl.gene.disease.type"
    _columns = {
        "name": fields.char(u"分类名称", size=100),
        "line": fields.one2many("rhwl.gene.disease", "type_id", string=u"疾病名称")
    }

#疾病明细对象
class rhwl_gene_disease(osv.osv):
    _name = "rhwl.gene.disease"
    _columns = {
        "name": fields.char(u"疾病名称", size=50),
        "type_id": fields.many2one("rhwl.gene.disease.type", string=u"分类名称"),
        "code":fields.char("Code",size=5),
    }


class rhwl_gene_popup(osv.osv_memory):
    _name = "rhwl.easy.genes.popup"
    _columns = {
        "note": fields.text(u"说明")
    }

    def action_ok(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids, context)
        s = {
            "confirm_note": "except_confirm",
            "except_note": "except"
        }
        col = context.get('col')
        if not context:
            context={}
        context["user_id"]=uid
        tab = context.get("tab","rhwl.easy.genes")
        self.pool.get(tab).write(cr, SUPERUSER_ID, context.get("active_id", 0),
                                               {col: obj.note, "state": s.get(col)},context=context)
