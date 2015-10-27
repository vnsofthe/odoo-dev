# -*- coding: utf-8 -*-
from openerp import SUPERUSER_ID,api
import threading
from openerp.osv import osv,fields
import base64
from tempfile import NamedTemporaryFile
import xlrd,os
import datetime
import logging
_logger = logging.getLogger(__name__)

class rhwl_import(osv.osv_memory):
    _name = 'rhwl.genes.ys.import'
    _columns = {
        "file_bin":fields.binary(string=u"位点结果文件"),
    }
    _defaults={
        "is_over":False
    }

    def import_report(self, cr, uid, ids, context=None):
        """接收检测点位数据"""
        if context is None:
            context = {}
        this = self.browse(cr, uid, ids[0])
        over_no=[] #记录重复转入的样本号
        fileobj = NamedTemporaryFile('w+',delete=True)
        xlsname =  fileobj.name
        f=open(xlsname+'.xls','wb')
        fileobj.close()
        try:
            #fileobj.write(base64.decodestring(this.file_bin.decode('base64')))
            b=this.file_bin.decode('base64')
            f.write(b)
            f.close()
            try:
                bk = xlrd.open_workbook(xlsname+".xls")
                sh = bk.sheet_by_index(0)
            except:
               raise osv.except_osv(u"打开出错",u"请确认位点数据文件格式是否为正确的报告标准格式。")
            nrows = sh.nrows
            ncols = sh.ncols
            snp={}
            for i in range(1,ncols):
                v=sh.cell_value(0,i)
                if not v:continue

                snp[i]=v

            genes_ids=[]
            for i in range(1,nrows):
                no=sh.cell_value(i,0)
                if not no:continue
                id=self.pool.get("rhwl.genes.ys").search(cr,uid,[("name","=",no)],context=context)
                if not id:
                    raise osv.except_osv(u"错误",u"样本编码[%s]不存在。"%(no,))
                if genes_ids.count(id[0])>0:
                    raise osv.except_osv(u"错误",u"编号[%s]在Excel中存在多笔。"%(no,))
                genes_ids.append(id[0])
                self.pool.get("rhwl.genes.ys").write(cr,uid,id,{"log":[[0,0,{"note":u"导入位点数据","data":"SNP"}]]},context=context)
                type_ids = self.pool.get("rhwl.genes.ys.snp").search(cr,uid,[("parent_id","=",id[0])],context=context)
                old_type={}
                if type_ids:
                    over_no.append(no)
                    for t in self.pool.get("rhwl.genes.ys.snp").browse(cr,uid,type_ids,context=context):
                        old_type[t.snp]=t.typ
                is_ok=True #判断全部位点是否有值
                for k in snp.keys():
                    v=str(sh.cell_value(i,k)).split(".")[0].replace("/","")
                    if old_type.has_key(snp.get(k)):
                        if old_type[snp.get(k)]=="N/A":
                            old_type[snp.get(k)]=v
                        if v=="N/A":
                            v=old_type[snp.get(k)]
                        if  old_type[snp.get(k)] != v:
                            raise osv.except_osv(u"错误",u"基因样本编码[%s]位点[%s]原来的值为[%s],现在的值为[%s],请确认原因。"%(no,snp.get(k),old_type[snp.get(k)],v))

                    val={
                        "parent_id":id[0],
                        "snp":snp.get(k),
                        "typ": v.replace("/",""),
                    }
                    self.pool.get("rhwl.genes.ys.snp").create(cr,uid,val,context=context)
                    if v=="N/A":is_ok=False
                self.pool.get("rhwl.genes.ys").write(cr,uid,id,{"batch_no":"YS"+datetime.datetime.now().strftime("%y%m%d")},context=context)
                self.pool.get("rhwl.genes.ys").action_state_snp(cr,uid,id,context=context)
                if type_ids:
                    self.pool.get("rhwl.genes.ys.snp").write(cr,uid,type_ids,{"active":False},context=context)

        finally:
            f.close()
            os.remove(xlsname+'.xls')
        self.pool.get("rhwl.weixin.base").send_qy_text(cr,SUPERUSER_ID,"rhwlyy","is_export_ys","本次导入叶酸检测位点%s笔"%(nrows-1,))
        return

    def import_report_el(self, cr, uid, ids, context=None):
        """接收检测点位数据"""
        if context is None:
            context = {}
        this = self.browse(cr, uid, ids[0])
        over_no=[] #记录重复转入的样本号
        fileobj = NamedTemporaryFile('w+',delete=True)
        xlsname =  fileobj.name
        f=open(xlsname+'.xls','wb')
        fileobj.close()
        try:
            #fileobj.write(base64.decodestring(this.file_bin.decode('base64')))
            b=this.file_bin.decode('base64')
            f.write(b)
            f.close()
            try:
                bk = xlrd.open_workbook(xlsname+".xls")
                sh = bk.sheet_by_index(0)
            except:
               raise osv.except_osv(u"打开出错",u"请确认位点数据文件格式是否为正确的报告标准格式。")
            nrows = sh.nrows
            ncols = sh.ncols
            snp={}
            for i in range(1,ncols):
                v=sh.cell_value(0,i)
                if not v:continue

                snp[i]=v

            genes_ids=[]
            for i in range(1,nrows):
                no=sh.cell_value(i,0)
                if not no:continue
                id=self.pool.get("rhwl.genes.el").search(cr,uid,[("name","=",no)],context=context)
                if not id:
                    raise osv.except_osv(u"错误",u"样本编码[%s]不存在。"%(no,))
                if genes_ids.count(id[0])>0:
                    raise osv.except_osv(u"错误",u"编号[%s]在Excel中存在多笔。"%(no,))
                genes_ids.append(id[0])
                self.pool.get("rhwl.genes.el").write(cr,uid,id,{"log":[[0,0,{"note":u"导入位点数据","data":"SNP"}]]},context=context)
                type_ids = self.pool.get("rhwl.genes.el.snp").search(cr,uid,[("parent_id","=",id[0])],context=context)
                old_type={}
                if type_ids:
                    over_no.append(no)
                    for t in self.pool.get("rhwl.genes.el.snp").browse(cr,uid,type_ids,context=context):
                        old_type[t.snp]=t.typ
                is_ok=True #判断全部位点是否有值
                for k in snp.keys():
                    v=str(sh.cell_value(i,k)).split(".")[0].replace("/","")
                    if old_type.has_key(snp.get(k)):
                        if old_type[snp.get(k)]=="N/A":
                            old_type[snp.get(k)]=v
                        if v=="N/A":
                            v=old_type[snp.get(k)]
                        if  old_type[snp.get(k)] != v:
                            raise osv.except_osv(u"错误",u"基因样本编码[%s]位点[%s]原来的值为[%s],现在的值为[%s],请确认原因。"%(no,snp.get(k),old_type[snp.get(k)],v))

                    val={
                        "parent_id":id[0],
                        "snp":snp.get(k),
                        "typ": v.replace("/",""),
                    }
                    self.pool.get("rhwl.genes.el.snp").create(cr,uid,val,context=context)
                    if v=="N/A":is_ok=False
                self.pool.get("rhwl.genes.el").write(cr,uid,id,{"batch_no":"EL"+datetime.datetime.now().strftime("%y%m%d")},context=context)
                self.pool.get("rhwl.genes.el").action_state_snp(cr,uid,id,context=context)
                if type_ids:
                    self.pool.get("rhwl.genes.el.snp").write(cr,uid,type_ids,{"active":False},context=context)

        finally:
            f.close()
            os.remove(xlsname+'.xls')
        self.pool.get("rhwl.weixin.base").send_qy_text(cr,SUPERUSER_ID,"rhwlyy","is_export_el","本次导入耳聋检测位点%s笔"%(nrows-1,))
        return