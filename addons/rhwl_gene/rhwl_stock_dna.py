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

class rhwl_dna(osv.osv):
    _name = "rhwl.gene.stock.dna"

    _columns={
        "name":fields.char(u"名称",size=20),
        "start_date":fields.date(u"起始日期",required=True),
        "end_date":fields.date(u"终止日期",required=True),
        "is_ok":fields.boolean(u"已全部导入"),
        "line":fields.one2many("rhwl.gene.stock.dna.line","parent_id",string="Detail"),
        "original":fields.one2many("rhwl.gene.stock.dna.original","parent_id",string="original")
    }

    def create(self,cr,uid,val,context=None):
        id = self.search(cr,uid,['|','&',("start_date","<=",val["start_date"]),("end_date",">=",val["start_date"]),'&',("start_date","<=",val["end_date"]),("end_date",">=",val["end_date"])])
        if id:
            raise osv.except_osv("ERROR",u"日期范围不能重复。")
        gene_id = self.pool.get("rhwl.easy.genes").search(cr,uid,[("date",">=",val["start_date"]),("date","<=",val["end_date"]),("cust_prop","in",["tjs","tjs_vip"])],context=context)
        id = super(rhwl_dna,self).create(cr,uid,val,context=context)

        line_id = self.pool.get("rhwl.gene.stock.dna.line").search(cr,uid,[("name.id","in",gene_id)])
        self.pool.get("rhwl.gene.stock.dna.line").write(cr,uid,line_id,{"parent_id":id},context=context)

        original_id = self.pool.get("rhwl.gene.stock.dna.original").search(cr,uid,[("name.id","in",gene_id)])
        self.pool.get("rhwl.gene.stock.dna.original").write(cr,uid,original_id,{"parent_id":id},context=context)
        return id

    def write(self,cr,uid,ids,val,context=None):
        if isinstance(ids,(long,int)):
            ids = [ids]
        if len(ids)>1 and (val.has_key("start_date") or val.has_key("end_date")):
            raise osv.except_osv("ERROR",u"日期范围不能重复。")
        if (not val.has_key("start_date")) and (not val.has_key("end_date")):
            pass
        else:
            if val.has_key("start_date") and val.has_key("end_date"):
                s_date = val["start_date"]
                e_date = val["end_date"]
            else:
                obj = self.browse(cr,uid,ids,context=context)
                s_date = val.get("start_date",obj.start_date)
                e_date = val.get("end_data",obj.end_date)
            id = self.search(cr,uid,['|','&',("start_date","<=",s_date),("end_date",">=",s_date),'&',("start_date","<=",e_date),("end_date",">=",e_date)])
            if id:
                raise osv.except_osv("ERROR",u"日期范围不能重复。")

        res = super(rhwl_dna,self).write(cr,uid,ids,val,context=context)

        for i in self.browse(cr,uid,ids,context=context):
            gene_id = self.pool.get("rhwl.easy.genes").search(cr,uid,[("date",">=",i.start_date),("date","<=",i.end_date),("cust_prop","in",["tjs","tjs_vip"])],context=context)

            move_id = self.pool.get("rhwl.gene.stock.dna.line").search(cr,uid,[("parent_id","=",i.id),("name.id","not in",gene_id)])
            self.pool.get("rhwl.gene.stock.dna.line").write(cr,uid,move_id,{"parent_id":False},context=context)

            line_id = self.pool.get("rhwl.gene.stock.dna.line").search(cr,uid,[("name.id","in",gene_id)])
            self.pool.get("rhwl.gene.stock.dna.line").write(cr,uid,line_id,{"parent_id":i.id},context=context)

            if i.is_ok:
                for g in gene_id:
                    if self.pool.get("rhwl.gene.stock.dna.line").search_count(cr,uid,[("name.id","=",g)])==0:
                        self.pool.get("rhwl.gene.stock.dna.line").create(cr,uid,{"parent_id":i.id,"name":g,"note":u"样本已用完"},context=context)

            original_id = self.pool.get("rhwl.gene.stock.dna.original").search(cr,uid,[("parent_id","=",i.id),("name.id","not in",gene_id)])
            self.pool.get("rhwl.gene.stock.dna.original").write(cr,uid,move_id,{"parent_id":False},context=context)

            line_id = self.pool.get("rhwl.gene.stock.dna.original").search(cr,uid,[("name.id","in",gene_id)])
            self.pool.get("rhwl.gene.stock.dna.original").write(cr,uid,line_id,{"parent_id":i.id},context=context)
        return res

class rhwl_dna_line(osv.osv):
    _name = "rhwl.gene.stock.dna.line"

    _columns={
        "parent_id":fields.many2one("rhwl.gene.stock.dna","Parent"),
        "name":fields.many2one("rhwl.easy.genes",u"基因样本编号",required=True),
        "box_no":fields.char(u"盒号",size=15),
        "hole_no":fields.char(u"孔号",size=3),
        "note":fields.char(u"备注",size=20),
        "user_name":fields.char(u"操作人员",size=50),
        "is_first":fields.boolean(u"首次提取")
    }

    _defaults={
        "is_first":True,
    }

    def create(self,cr,uid,val,context=None):
        d = self.pool.get("rhwl.easy.genes").browse(cr,uid,val["name"],context=context).date
        p_ids = self.pool.get("rhwl.gene.stock.dna").search(cr,uid,[("start_date","<=",d),("end_date",">=",d)],context=context)
        if p_ids:
            val["parent_id"] = p_ids[0]
        return super(rhwl_dna_line,self).create(cr,uid,val,context=context)

    def write(self,cr,uid,ids,val,context=None):
        if val.has_key("name"):
            d = self.pool.get("rhwl.easy.genes").browse(cr,uid,val["name"],context=context).date
            p_ids = self.pool.get("rhwl.gene.stock.dna").search(cr,uid,[("start_date","<=",d),("end_date",">=",d)],context=context)
            if p_ids:
                val["parent_id"] = p_ids[0]
            else:
                val["parent_id"]=False
        return super(rhwl_dna_line,self).write(cr,uid,ids,val,context=context)

class rhwl_dna_original(osv.osv):
    _name="rhwl.gene.stock.dna.original"

    _columns={
        "parent_id":fields.many2one("rhwl.gene.stock.dna","Parent"),
        "name":fields.many2one("rhwl.easy.genes",u"基因样本编号",required=True),
        "box_no":fields.char(u"盒号",size=15),
        "hole_no":fields.char(u"孔号",size=3),
        "user_name":fields.char(u"存储人员",size=50),
    }

    def create(self,cr,uid,val,context=None):
        d = self.pool.get("rhwl.easy.genes").browse(cr,uid,val["name"],context=context).date
        p_ids = self.pool.get("rhwl.gene.stock.dna").search(cr,uid,[("start_date","<=",d),("end_date",">=",d)],context=context)
        if p_ids:
            val["parent_id"] = p_ids[0]
        return super(rhwl_dna_original,self).create(cr,uid,val,context=context)

    def write(self,cr,uid,ids,val,context=None):
        if val.has_key("name"):
            d = self.pool.get("rhwl.easy.genes").browse(cr,uid,val["name"],context=context).date
            p_ids = self.pool.get("rhwl.gene.stock.dna").search(cr,uid,[("start_date","<=",d),("end_date",">=",d)],context=context)
            if p_ids:
                val["parent_id"] = p_ids[0]
            else:
                val["parent_id"]=False
        return super(rhwl_dna_original,self).write(cr,uid,ids,val,context=context)