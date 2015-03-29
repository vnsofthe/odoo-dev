# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID,api
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import datetime
import requests
import logging

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
        'report':u'报告发送',
        'done':u'完成'
    }
    _name = "rhwl.easy.genes"
    _columns={
        "batch_no":fields.char(u"批号"),
        "name":fields.char(u"样本编码",required=True,size=10),
        "date":fields.date(u"日期",required=True),
        "cust_name":fields.char(u"客户姓名",required=True,size=10),
        "sex":fields.selection([('T',u"男"),('F',u"女")],u"性别"),
        "identity":fields.char(u"身份证号",size=18),
        "mobile":fields.char(u"手机号",size=15),
        "birthday":fields.date(u"出生日期"),
        "receiv_date":fields.datetime(u"接收时间"),
        "except_note":fields.text(u"信息问题反馈"),
        "confirm_note":fields.text(u"信息确认回馈"),
        "state":fields.selection(STATE_SELECT.items(),u"状态"),
        "note":fields.text(u"备注"),
        "gene_id":fields.char(u"基因编号",size=20),
        "img":fields.binary(u"图片"),
        "log":fields.one2many("rhwl.easy.genes.log","genes_id","Log")
    }

    _defaults={
        "state":'draft',
    }
    def create(self,cr,uid,val,context=None):
        val["log"]=[[0,0,{"note":u"资料新增","data":"create"}]]
        if not val.get("batch_no",None):
            val["batch_no"]=datetime.datetime.strftime(datetime.datetime.today(),"%m-%d")
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
        ids = self.search(cr,uid,[("id","in",ids),("state","=","draft")],context=context)
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
