# -*- coding: utf-8 -*-

import threading
from openerp.osv import osv,fields
import base64
from tempfile import NamedTemporaryFile
import xlrd,os
import datetime
import logging

_logger = logging.getLogger(__name__)
class rhwl_import(osv.osv_memory):
    _name = 'rhwl.genes.import'
    _columns = {
        "file_bin":fields.binary(string=u"文件名",required=True),
    }

    def date_trun(self,val):
        _logger.info(val)
        if list(str(val)).count("/")==0:
            d=xlrd.xldate_as_tuple(int(val),0)
            _logger.info("%s/%s/%s"%(d[0],d[1],d[2]))
            return "%s/%s/%s"%(d[0],d[1],d[2])
        else:
            return val

    def import_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        this = self.browse(cr, uid, ids[0])

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
               raise osv.except_osv(u"打开出错",u"请确认文件格式是否为正确的报告标准格式。")
            nrows = sh.nrows
            ncols = sh.ncols
            for i in range(2,nrows+1):
                if not sh.cell_value(i-1,0):continue

                val={
                    "date":datetime.datetime.strptime(sh.cell_value(i-1,0),"%Y/%m/%d"),
                    "cust_name":sh.cell_value(i-1,1),
                    "sex": 'T' if sh.cell_value(i-1,2)==u"男" else 'F',
                    "name":sh.cell_value(i-1,3),
                    "identity":sh.cell_value(i-1,4)
                }

                self.pool.get("rhwl.easy.genes").create(cr,uid,val,context=context)

        finally:
            f.close()
            os.remove(xlsname+'.xls')
        v_id=self.pool.get('ir.ui.view').search(cr,uid,[('name', '=', "rhwl.easy.genes.view.tree")])

        return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                "view_id":v_id,
                'res_model': 'rhwl.easy.genes',
                "context":{'search_default_type_draft':1,'search_default_type_exceptconfirm':1},
                'view_mode': 'tree'}

    def import_report2(self, cr, uid, ids, context=None):
        """接收质检数据"""
        if context is None:
            context = {}
        this = self.browse(cr, uid, ids[0])

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
               raise osv.except_osv(u"打开出错",u"请确认文件格式是否为正确的报告标准格式。")
            nrows = sh.nrows

            for i in range(2,nrows):
                no=sh.cell_value(i,1)
                if not no:continue
                if type(no)==type(1.0):no = no.__trunc__()
                id=self.pool.get("rhwl.easy.genes").search(cr,uid,[("name","=",no)],context=context)
                self.pool.get("rhwl.easy.genes").write(cr,uid,id,{"log":[[0,0,{"note":u"导入质检数据","data":"DNA"}]]},context=context)
                obj_ids = self.pool.get("rhwl.easy.genes.check").search(cr,uid,[("genes_id.name",'=',no)],context=context)
                if obj_ids:
                    self.pool.get("rhwl.easy.genes.check").write(cr,uid,obj_ids,{"active":False})
                t1=sh.cell_value(i,3)
                t2=sh.cell_value(i,5)
                t3=sh.cell_value(i,6)
                val={
                        "genes_id":id[0],
                        "date":self.date_trun(sh.cell_value(i,0)),
                        "dna_date":self.date_trun(sh.cell_value(i,2)),
                        "concentration":t1,
                        "lib_person":sh.cell_value(i,4),
                        "od260_280":t2,
                        "od260_230":t3,
                        "chk_person":sh.cell_value(i,7),
                        "data_loss":sh.cell_value(i,8),
                        "loss_person":sh.cell_value(i,9),
                        "loss_date":self.date_trun(sh.cell_value(i,10)),
                        "active":True,
                    }
                _logger.info(val)
                self.pool.get("rhwl.easy.genes.check").create(cr,uid,val,context=context)
                if (t1<10 or t2<1.8 or t2>2 or t3<2) and obj_ids:
                    self.pool.get("rhwl.easy.genes").action_state_dna(cr,uid,id,context=context)

        finally:
            f.close()
            os.remove(xlsname+'.xls')

        return

    def import_report3(self, cr, uid, ids, context=None):
        """接收检测点位数据"""
        if context is None:
            context = {}
        this = self.browse(cr, uid, ids[0])

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
               raise osv.except_osv(u"打开出错",u"请确认文件格式是否为正确的报告标准格式。")
            nrows = sh.nrows
            ncols = sh.ncols
            snp={}
            for i in range(1,ncols):
                v=sh.cell_value(0,i)
                if not v:continue
                snp[i]=v

            for i in range(1,nrows):
                no=sh.cell_value(i,0)
                if not no:continue
                id=self.pool.get("rhwl.easy.genes").search(cr,uid,[("name","=",no)],context=context)
                self.pool.get("rhwl.easy.genes").write(cr,uid,id,{"log":[[0,0,{"note":u"导入点位数据","data":"SNP"}]]},context=context)
                cr.execute("delete from rhwl_easy_genes_type where genes_id=%s" %(id[0],))
                for k in snp.keys():
                    val={
                        "genes_id":id[0],
                        "snp":snp.get(k),
                        "typ": str(sh.cell_value(i,k)).split(".")[0],
                    }
                    self.pool.get("rhwl.easy.genes.type").create(cr,uid,val,context=context)

        finally:
            f.close()
            os.remove(xlsname+'.xls')

        return
