# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID, api
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import datetime
import requests
import logging
import os
import shutil

_logger = logging.getLogger(__name__)

class rhwl_picking(osv.osv):
    _name="rhwl.genes.picking"
    _columns={
        "name":fields.char(u"发货单号",size=10,required=True),
        "date":fields.date(u"发货日期",required=True),
        "line":fields.one2many("rhwl.genes.picking.line","picking_id","Detail"),
    }
    _defaults={
        "date":fields.date.today,

    }

class rhwl_picking_line(osv.osv):
    _name = "rhwl.genes.picking.line"

    def _get_box_qty(self,cr,uid,ids,field_names,arg,context=None):
        res=dict.fromkeys(ids,0)
        for k in res.keys():
            res[k] = self.pool.get("rhwl.genes.picking.box").search_count(cr,uid,[("line_id","=",k)])
        return res

    def _get_detail_qty(self,cr,uid,ids,field_names,arg,context=None):
        res=dict.fromkeys(ids,0)
        for k in res.keys():
            res[k] = self.pool.get("rhwl.genes.picking.box.line").search_count(cr,uid,[("box_id.line_id.id","=",k)])
        return res

    _columns={
        "picking_id":fields.many2one("rhwl.genes.picking",u"发货单号",ondelete="restrict"),
        "seq":fields.integer(u"序号",required=True),
        "product_name":fields.char(u"货品名称",size=20),
        "batch_no":fields.char(u"批号",size=15,required=True),
        "batch_kind":fields.selection([("normal",u"普通"),("vip",u"VIP客户"),("resend",u"破损重印")],u"类型"),
        "box_qty":fields.function(_get_box_qty,type="integer",string=u"箱数"),
        "qty":fields.function(_get_detail_qty,type="integer",string=u"数量"),
        "note":fields.char(u"备注",size=200),
        "box_line":fields.one2many("rhwl.genes.picking.box","line_id","Detail"),
    }
    _defaults={
        "product_name":u"检测报告",
        "batch_kind":"normal",
    }
    _sql_constraints = [
        ('rhwl_genes_picking_seq_uniq', 'unique(picking_id,seq)', u'发货明细序号不能重复!'),
    ]

    @api.onchange("batch_kind")
    def _onchange_batch_kind(self):
        if self.batch_kind=="resend":
            self.batch_no="破损重印"
        elif self.batch_kind=="vip":
            self.batch_no="VIP客户"
        else:
            self.batch_no=""

    def create(self,cr,uid,val,context=None):
        if val.get("seq",0)<=0:
            raise osv.except_osv(u'错误',u'发货明细的序号必须大于0')
        if val.get("batch_kind")=="normal":
            ids=self.pool.get("rhwl.easy.genes").search(cr,uid,[("batch_no","=",val.get("batch_no"))],context=context)
            if not ids:
                raise osv.except_osv(u"错误",u"批次号不存在，请输入正确的批次号码。")
            ids=self.pool.get("rhwl.easy.genes").search_count(cr,uid,[("batch_no","=",val.get("batch_no")),("state","in",["draft","except","except_confirm","confirm"])],context=context)
            if ids:
                raise osv.except_osv(u"错误",u"该批次下还有样本没有实验结果，不能建立发货明细。")

        line_id = super(rhwl_picking_line,self).create(cr,uid,val,context=context)

        if val.get("batch_kind")=="normal":
            risk_type={"H":True,"L":False}
            box_no="0"
            for k in risk_type.keys():
                ids=self.pool.get("rhwl.easy.genes").search(cr,uid,[("batch_no","=",val.get("batch_no")),("state","not in",["cancel"]),("cust_prop","=","tjs"),("is_risk","=",risk_type[k])],order="name")
                while len(ids)>13:
                    box_no=str(int(box_no)+1)
                    self._insert_box(cr,uid,line_id,box_no,k,ids[0:13])
                    ids=ids[13:]
                else:
                    if len(ids)>0:
                        box_no=str(int(box_no)+1)
                        self._insert_box(cr,uid,line_id,box_no,k,ids)
        elif val.get("batch_kind")=="vip":
            ids = self.search(cr,uid,[("picking_id","=",val.get("picking_id")),("batch_kind","=","normal")])
            batchno=[]
            for i in self.browse(cr,uid,ids):
                batchno.append(i.batch_no)
            risk_type={"H":True,"L":False}
            box_no="0"
            for k in risk_type.keys():
                ids=self.pool.get("rhwl.easy.genes").search(cr,uid,[("batch_no","in",batchno),("state","not in",["cancel"]),("cust_prop","=","tjs_vip"),("is_risk","=",risk_type[k])],order="name")
                while len(ids)>13:
                    box_no=str(int(box_no)+1)
                    self._insert_box(cr,uid,line_id,box_no,k,ids[0:13])
                    ids=ids[13:]
                else:
                    if len(ids)>0:
                        box_no=str(int(box_no)+1)
                        self._insert_box(cr,uid,line_id,box_no,k,ids)

        return line_id

    def _insert_box(self,cr,uid,id,box,level,val):
        values=[]
        for i in val:
            values.append([0,0,{"genes_id":i}])
        return self.pool.get("rhwl.genes.picking.box").create(cr,uid,{"line_id":id,"name":box,"level":level,"detail":values})


class rhwl_picking_box(osv.osv):
    _name="rhwl.genes.picking.box"
    _columns={
        "line_id":fields.many2one("rhwl.genes.picking.line",u"发货明细",ondelete="cascade"),
        "name":fields.char(u"箱号",size=5,required=True),
        "level":fields.selection([("H",u"高风险"),("L",u"低风险")],u"风险值"),
        "detail":fields.one2many("rhwl.genes.picking.box.line","box_id","Detail")
    }
    _sql_constraints = [
        ('rhwl_genes_picking_box_name_uniq', 'unique(line_id,name)', u'发货明细箱号不能重复!'),
    ]

class rhwl_picking_box_line(osv.osv):
    _name="rhwl.genes.picking.box.line"
    _columns={
        "box_id":fields.many2one("rhwl.genes.picking.box",u"箱号",ondelete="cascade"),
        "genes_id":fields.many2one("rhwl.easy.genes",u"基因样本编号",ondelete="restrict",required=True),
        "name":fields.related("genes_id","cust_name",type="char",string=u"会员姓名")
    }