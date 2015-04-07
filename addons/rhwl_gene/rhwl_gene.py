# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID,api
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import datetime
import requests
import logging
import os
import shutil

_logger = logging.getLogger(__name__)
class rhwl_gene(osv.osv):
    STATE_SELECT={
        'draft':u'草稿',
        'except':u'信息异常',
        'except_confirm':u'异常确认',
        'confirm':u'信息确认',
        'dna_except':u'DNA质检不合格',
        'cancel':u'取消',
        'ok':u'检测完成',
        'report':u'生成报告中',
        'report_done':u"报告已生成",
        "result_done":u"风险报告确认",
        "deliver":u"已出货",
        'done':u'完成'
    }
    _name = "rhwl.easy.genes"
    _order="date desc,name asc"
    def _genes_type_get(self, cr, uid, ids, field_names, arg, context=None):
        res = {}
        maps={}
        for id in ids:
            res[id] = {}.fromkeys(field_names, "")
            type_ids=self.pool.get("rhwl.easy.genes.type").search(cr,uid,[("genes_id.id",'=',id)],context=context)
            for i in self.pool.get("rhwl.easy.genes.type").browse(cr,uid,type_ids,context=context):
                res[id][maps.get(i.snp,i.snp)] = i.typ
        return res

    _columns={
        "batch_no":fields.char(u"批次"),
        "name":fields.char(u"基因样本编号",required=True,size=10),
        "date":fields.date(u"送检日期",required=True),
        "cust_name":fields.char(u"会员姓名",required=True,size=10),
        "sex":fields.selection([('T',u"男"),('F',u"女")],u"性别",required=True),
        "identity":fields.char(u"身份证号",size=18),
        "mobile":fields.char(u"手机号码",size=15),
        "birthday":fields.date(u"出生日期"),
        "receiv_date":fields.datetime(u"接收时间"),
        "except_note":fields.text(u"信息异常内容"),
        "confirm_note":fields.text(u"信息异常反馈"),
        "state":fields.selection(STATE_SELECT.items(),u"状态"),
        "note":fields.text(u"备注"),
        "gene_id":fields.char(u"基因编号",size=20),
        "cust_prop":fields.selection([("tjs",u"泰济生客户"),("employee",u"内部员工"),("vip",u"VIP客户"),("extra",u"外部人员")],string=u"客户属性"),
        "img":fields.binary(u"图片"),
        "log":fields.one2many("rhwl.easy.genes.log","genes_id","Log"),
        "typ":fields.one2many("rhwl.easy.genes.type","genes_id","Type"),
        "dns_chk":fields.one2many("rhwl.easy.genes.check","genes_id","DNA_Check"),
        "pdf_file":fields.char(u"风险报告",size=100),
        "rs1042713":fields.function(_genes_type_get,type="char",string='rs1042713', multi='typ'),
        "rs1050152":fields.function(_genes_type_get,type="char",string='rs1050152', multi='typ'),
    }
    _sql_constraints = [
        ('rhwl_easy_genes_name_uniq', 'unique(name)', u'样本编号不能重复!'),
    ]
    _defaults={
        "state":'draft',
        "cust_prop":"tjs",
    }
    def create(self,cr,uid,val,context=None):
        val["log"]=[[0,0,{"note":u"资料新增","data":"create"}]]
        #if not val.get("batch_no",None):
        #    val["batch_no"]=datetime.datetime.strftime(datetime.datetime.today(),"%m-%d")
        return super(rhwl_gene,self).create(cr,uid,val,context=context)

    def write(self,cr,uid,id,val,context=None):
        if val.has_key("state"):
            val["log"]=[[0,0,{"note":u"状态变更为:"+self.STATE_SELECT.get(val.get("state")),"data":val.get("state")}]]
        if val.has_key("img"):
            val["log"]=[[0,0,{"note":u"图片变更","data":"img"}]]
        return super(rhwl_gene,self).write(cr,uid,id,val,context=context)

    def unlink(self, cr, uid, ids, context=None):
        if isinstance(ids,(long,int)):
            ids=[ids]
        if uid!=SUPERUSER_ID:ids = self.search(cr,uid,[("id","in",ids),("state","=","draft")],context=context)
        return super(rhwl_gene,self).unlink(cr,uid,ids,context=context)

    def action_state_except(self, cr, uid, ids, context=None):
        if not context:
            context={}
        if context.get("view_type")=="tree":
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'res_model': 'rhwl.easy.genes.popup',
                'view_mode': 'form',
                'name':u"异常说明",
                'target': 'new',
                'context':{'col':'except_note'},
                'flags': {'form': {'action_buttons': False}}}

        return self.write(cr,uid,ids,{"state":"except"})

    def action_state_except_confirm(self,cr,uid,ids,context=None):
        if not context:
            context={}
        if context.get("view_type")=="tree":
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'res_model': 'rhwl.easy.genes.popup',
                'view_mode': 'form',
                'name':u"回馈说明",
                'target': 'new',
                'context':{'col':'confirm_note'},
                'flags': {'form': {'action_buttons': False}}}

        return self.write(cr,uid,ids,{"state":"except_confirm"})


    def action_state_confirm(self, cr, uid, ids, context=None):
        return self.write(cr,uid,ids,{"state":"confirm"})

    def action_state_cancel(self,cr,uid,ids,context=None):
        return self.write(cr,uid,ids,{"state":"cancel"})

    def action_state_dna(self,cr,uid,ids,context=None):
        return self.write(cr,uid,ids,{"state":"dna_except"})

    def action_state_ok(self,cr,uid,ids,context=None):
        return self.write(cr,uid,ids,{"state":"ok"})

    def action_state_reset(self,cr,uid,ids,context=None):
        return self.write(cr,uid,ids,{"state":"draft"})

    def action_state_report(self,cr,uid,ids,context=None):
        return self.write(cr,uid,ids,{"state":"report"})

    def action_state_result_done(self,cr,uid,ids,context=None):
        return self.write(cr,uid,ids,{"state":"result_done"})

    def action_view_pdf(self,cr,uid,ids,context=None):
        return {'type': 'ir.actions.act_url',
                'url': context.get("file_name","/"),
                'target': 'new'}

    def create_gene_type_file(self,cr,uid,ids,context=None):
        ids=self.search(cr,uid,[("state","=","ok")],context=context)
        if ids:
            if isinstance(ids,(long,int)):
                ids=[ids]
            obj=self.browse(cr,uid,ids,context=context)
            title={}
            data=[]
            for i in obj:
                if not i.typ:
                    ids.remove(i.id)
                    continue
                rec=[]
                for t in i.typ:
                    k=t.snp
                    k=k.encode("utf-8")
                    if not title.has_key(k):
                        title[k]=""
                    rec.append((k,(t.typ).encode("utf-8")))
                rec_dict = dict(rec)
                r=[i.name.encode("utf-8"),i.cust_name.encode("utf-8"),i.sex.encode("utf-8") if i.sex.encode("utf-8")=='F' else 'M',]
                for k in title.keys():
                    r.append(rec_dict[k])
                data.append(r)


            fpath = os.path.join(os.path.split(__file__)[0],"static/remote/snp")
            fname=os.path.join(fpath,"snp_"+datetime.datetime.now().strftime("%Y%m%d%H%M%S")+".txt")

            f=open(fname,"w+")
            f.write("编号\t姓名\t性别\t"+"\t".join(title.keys())+'\n')
            for i in data:
                f.write("\t".join(i)+'\n')
            f.close()
            self.action_state_report(cr,uid,ids,context=context)

    def get_gene_pdf_file(self,cr,uid,context=None):
        fpath = os.path.join(os.path.split(__file__)[0],"static/remote/report")
        tpath = os.path.join(os.path.split(__file__)[0],"static/local/report")
        for f in os.listdir(fpath):
            newfile = os.path.join(fpath,f)
            if os.path.isdir(newfile):
                for f1 in os.listdir(newfile):
                    f2=f1.split("_")[0] + ".pdf"
                    shutil.move(os.path.join(newfile,f1),os.path.join(tpath,f2))
                    ids = self.search(cr,uid,[("name","=",f2.split(".")[0])])
                    if ids:
                        self.write(cr,uid,ids,{"pdf_file":"rhwl_gene/static/local/report/"+f2,"state":"report_done","batch_no":datetime.datetime.strftime(datetime.datetime.today(),"%m%d")})
                os.removedirs(newfile)


class rhwl_gene_log(osv.osv):
    _name = "rhwl.easy.genes.log"
    _order = "date desc"
    _columns={
        "genes_id":fields.many2one("rhwl.easy.genes","Genes ID"),
        "date":fields.datetime(u"时间"),
        "user_id":fields.many2one("res.users",u"操作人员"),
        "note":fields.text(u"作业说明"),
        "data":fields.char("Data")
    }

    _defaults={
        "date":fields.datetime.now,
        "user_id":lambda obj,cr,uid,context:uid,
    }

class rhwl_gene_check(osv.osv):
    _name = "rhwl.easy.genes.check"
    _columns={
        "genes_id":fields.many2one("rhwl.easy.genes","Genes ID"),
        "date":fields.date(u"收样日期"),
        "dna_date":fields.date(u"提取日期"),
        "concentration":fields.char(u"浓度",size=5,help=u"参考值>=10"),
        "lib_person":fields.char(u"实验操作人",size=10),
        "od260_280":fields.char("OD260/OD280",size=5,help=u"参考值1.8-2.0"),
        "od260_230":fields.char("OD260/OD230",size=5,help=u"参考值>=2.0"),
        "chk_person":fields.char(u"检测人",size=10),
        "data_loss":fields.char(u"数据缺失率",size=6,help=u"参考值<1%"),
        "loss_person":fields.char(u"判读人",size=10),
        "loss_date":fields.date(u"判读日期"),
        "active":fields.boolean("Active"),
    }

    _defaults={
        "active":True
    }

class rhwl_gene_type(osv.osv):
    _name = "rhwl.easy.genes.type"
    _columns={
        "genes_id":fields.many2one("rhwl.easy.genes","Genes ID"),
        "snp":fields.char("SNP",size=20),
        "typ":fields.char("Type",size=10),
        "active":fields.boolean("Active"),
    }
    _defaults={
        "active":True
    }

class rhwl_gene_popup(osv.osv_memory):
    _name="rhwl.easy.genes.popup"
    _columns={
        "note":fields.text(u"说明")
    }

    def action_ok(self, cr, uid, ids, context=None):
        obj = self.browse(cr,uid,ids,context)
        s={
            "confirm_note":"except_confirm",
            "except_note":"except"
        }
        col=context.get('col')
        self.pool.get("rhwl.easy.genes").write(cr,uid,context.get("active_id",0),{col:obj.note,"state":s.get(col)})
