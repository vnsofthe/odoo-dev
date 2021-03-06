# -*- coding: utf-8 -*-

import threading
from openerp.osv import osv,fields
import base64
from tempfile import NamedTemporaryFile
import xlrd,os
import datetime
import logging
import xlwt
import zipfile
import shutil
import subprocess
_logger = logging.getLogger(__name__)

class rhwl_lib(osv.osv_memory):
    _name="rhwl.genes.merge"
    _columns={
        "file1_bin":fields.binary(string=u"Excel文件1",required=True),
        "file2_bin":fields.binary(string=u"Excel文件2",required=True),
        "file1_dir":fields.char(u"文件1分析文件夹"),
        "file2_dir":fields.char(u"文件2分析文件夹"),
        "sec_confirm":fields.boolean(u"以文件2结果为准"),
        "file_data":fields.binary(string=u"合并后文件"),
        "name":fields.char("Name"),
        "state":fields.selection([("draft","draft"),("done","done")],string="State"),
        "action":fields.selection([("1",u"片段分析"),("2",u"Sanger测序数据合并")],u"处理类型",required=True)
    }
    _defaults={
        "state":"draft",
        "name":u"位点合并结果.xls",
        "sec_confirm":False,
        "action":"1"
    }

    def action_merge(self,cr,uid,id,context=None):
        if context is None:
            context = {}
        this = self.browse(cr, uid, id,context=context)
        if this.action=="2":
            return self.action_merge_1(cr,uid,id,context=context)
        else:
            return self.action_merge_2(cr,uid,id,context=context)

    #处理两个excel结果的合并
    def action_merge_1(self,cr,uid,id,context=None):
        if context is None:
            context = {}
        this = self.browse(cr, uid, id,context=context)
        fileobj = NamedTemporaryFile('w+',delete=True)
        xlsname =  fileobj.name
        f1_name=xlsname+'_1.xls'
        f2_name=xlsname+'_2.xls'
        fileobj.close()
        f1=open(f1_name,'wb')
        f2=open(f2_name,'wb')

        f1.write(this.file1_bin.decode('base64'))
        f1.close()
        f2.write(this.file2_bin.decode('base64'))
        f2.close()

        header=[]
        data={}
        for f in [f1_name,f2_name]:
            try:
                bk = xlrd.open_workbook(f)
                sh = bk.sheet_by_index(0)
            except:
               raise osv.except_osv(u"打开出错",u"请确认文件格式是否为正确的报告标准Excel格式。")
            nrows = sh.nrows
            ncols = sh.ncols
            sheet_header={}
            #保存excel表头，在产生新的excel时要用到
            if not header:
                for c in range(1,ncols):
                    val=sh.cell_value(0,c)
                    if val:header.append(val)
            #记录当前excel中的表头位置
            for c in range(1,ncols):
                val=sh.cell_value(0,c)
                if val:sheet_header[c]=val

            for r in range(1,nrows):
                no=str(sh.cell_value(r,0)).split(".")[0].split("-")[0]
                if not data.has_key(no):data[no]={}
                for c in range(1,ncols):
                    val=sh.cell_value(r,c)
                    if not data[no].has_key(sheet_header[c]):
                        data[no][sheet_header[c]]=""
                    if not data[no][sheet_header[c]]:
                        data[no][sheet_header[c]]=val
                    if this.sec_confirm and val:
                        data[no][sheet_header[c]]=val
                    else:
                        if val and data[no][sheet_header[c]]!=val:
                            raise osv.except_osv(u"合并出错",u"样本编码%s，位点%s,有两个不同的结果[%s,%s]." %(no,sheet_header[c],val,data[no][sheet_header[c]]))
        os.remove(f1_name)
        os.remove(f2_name)

        w = xlwt.Workbook(encoding='utf-8')
        ws = w.add_sheet("Sheet1")
        #写表头
        col_row=1
        for h in header:
            ws.write(0,col_row,h)
            col_row+=1
        ws.write(0,0,"Sample Name")
        row_count=1
        for d in data.keys():
            ws.write(row_count,0,d)
            col_row=1
            for h in header:
                ws.write(row_count,col_row,data[d][h])
                col_row += 1
            row_count+=1
        w.save(xlsname+".xls")
        f=open(xlsname+".xls",'rb')

        self.write(cr,uid,id,{"state":"done","file_data": base64.encodestring(f.read())})
        f.close()
        os.remove(xlsname+".xls")
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rhwl.genes.merge',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': this.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

    #两个不同结果合并
    def action_merge_2(self,cr,uid,id,context=None):
        if context is None:
            context = {}
        this = self.browse(cr, uid, id,context=context)
        fileobj = NamedTemporaryFile('w+',delete=True)
        xlsname =  fileobj.name
        fileobj.close()
        PDIR="/data/odoo/library"
        #if not os.path.exists(os.path.join(PDIR,this.file1_dir)):
        #    raise osv.except_osv("Error","文件1所指定的文件夹不存在。")
        #if not os.path.exists(os.path.join(PDIR,this.file2_dir)):
        #    raise osv.except_osv("Error","文件2所指定的文件夹不存在。")

        f1=open(os.path.join(PDIR,xlsname+"1.txt"),'w')
        f2=open(os.path.join(PDIR,xlsname+"2.txt"),'w')

        f1.write(this.file1_bin.decode('base64'))
        f1.close()
        f2.write(this.file2_bin.decode('base64'))
        f2.close()
        env = os.environ.copy()
        with open(os.path.join(PDIR,xlsname+"3.xls"),'w') as dn:
            rc = subprocess.call(("perl","/data/odoo/library/bin/snpScan.merge.pl",os.path.join(PDIR,xlsname+"1.txt"),os.path.join(PDIR,xlsname+"2.txt")), env=env, stdout=dn, stderr=subprocess.STDOUT)
            if rc:
                raise Exception('Command Error.')
        #perl /data/odoo/library/bin/snpScan.merge.pl merge.test.1.txt merge.test.2.txt /data/odoo/library/bin/merge-test/1st /data/odoo/library/bin/merge-test/2nd
        f=open(os.path.join(PDIR,xlsname+"3.xls"),'rb')
        self.write(cr,uid,id,{"state":"done","file_data": base64.encodestring(f.read())})
        f.close()
        #os.remove(xlsname+".xls")
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rhwl.genes.merge',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': this.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

class rhwl_analyze(osv.osv_memory):
    _name = "rhwl.genes.analyze"
    _columns = {
        "zip":fields.binary(string=u"检测数据压缩包",required=True),
        "excel":fields.binary(string=u"分析结果"),
        "log":fields.binary(string=u"分析日志"),
        "filename":fields.char("Name"),
        "log_filename":fields.char("Log Name"),
        "output_name":fields.char(u"输出文件名"),
        "state":fields.selection([("draft","draft"),("done","done")],string="State"),
    }
    _defaults={
        "state":"draft"
    }

    def action_analyze(self,cr,uid,id,context=None):
        if not context:
            context={}
        if not context.has_key("sanger"):
            return self.action_analyze1(cr,uid,id,context=context)
        else:
            return self.action_analyze2(cr,uid,id,context=context)

    def action_analyze1(self,cr,uid,id,context=None):
        if context is None:
            context = {}
        obj = self.browse(cr, uid, id,context=context)

        data_file = NamedTemporaryFile(delete=False)

        try:
            data_file.write(obj.zip.decode('base64'))
            data_file.close()
            if zipfile.is_zipfile(data_file.name):
                dump_dir=data_file.name+"excel"
                if not os.path.exists(dump_dir):
                    os.mkdir(dump_dir)
                dir_file=None
                with zipfile.ZipFile(data_file.name, 'r') as z:
                    # only extract known members!
                    filestore = [m for m in z.namelist() if m.endswith('fsa') or m.endswith('txt')]
                    z.extractall(dump_dir, filestore) #解压缩文件到临时目录
                    for i in os.listdir(dump_dir):
                        if os.path.isdir(os.path.join(dump_dir,i)):
                            if os.path.exists(os.path.join("/data/odoo/library",i)):
                                #shutil.rmtree(os.path.join("/data/odoo/library",i))
                                for p in os.listdir(os.path.join(dump_dir,i)):
                                    if os.path.exists(os.path.join(os.path.join("/data/odoo/library",i),p)):
                                        os.remove(os.path.join(os.path.join("/data/odoo/library",i),p))
                                    shutil.move(os.path.join(os.path.join(dump_dir,i),p),os.path.join(os.path.join("/data/odoo/library",i),p))
                                os.removedirs(os.path.join(os.path.join(dump_dir,i)))
                            else:
                                shutil.move(os.path.join(dump_dir,i),os.path.join("/data/odoo/library",i))
                            dir_file=os.path.join("/data/odoo/library",i)
                    if os.path.exists(dump_dir):os.removedirs(dump_dir)
                    env = os.environ.copy()
                    with open(os.devnull) as dn:
                        rc = subprocess.call(("perl","/data/odoo/library/bin/creat.pl",dir_file,"/data/odoo/library/bin/"), env=env, stdout=dn, stderr=subprocess.STDOUT)
                        if rc:
                            raise Exception('Command Error.')
                        log_file=[]
                        for i in os.listdir(dir_file):
                            if i.split(".")[-1]=="xls":
                                 f=open(os.path.join(dir_file,i),'rb')
                                 self.write(cr,uid,id,{"state":"done","filename":i,"excel": base64.encodestring(f.read())})
                                 f.close()

                            if i.split(".")[-1]=="log":
                                f=open(os.path.join(dir_file,i),'r')
                                log_file += [i.split(".")[0]+","+x for x in f.readlines()]
                                f.close()
                                os.remove(os.path.join(dir_file,i))
                        if log_file:
                            self.write(cr,uid,id,{"log_filename":"分析日志.txt","log": base64.encodestring("".join(log_file))})
                        return {
                                'type': 'ir.actions.act_window',
                                'res_model': 'rhwl.genes.analyze',
                                'view_mode': 'form',
                                'view_type': 'form',
                                'res_id': obj.id,
                                'views': [(False, 'form')],
                                'target': 'new',
                            }

            else:
                os.unlink(data_file.name)
                _logger.warning('File format is not ZIP')
                raise Exception("File format is not ZIP")

        finally:
            if os.path.exists(data_file.name):os.unlink(data_file.name)
        return True

    def action_analyze2(self,cr,uid,id,context=None):
        if context is None:
            context = {}
        obj = self.browse(cr, uid, id,context=context)
        if not obj.output_name:
            raise osv.except_osv("Error","输出文件名不可以为空。")

        data_file = NamedTemporaryFile(delete=False)

        try:
            data_file.write(obj.zip.decode('base64'))
            data_file.close()
            if zipfile.is_zipfile(data_file.name):
                dump_dir=data_file.name+"_zip"
                if not os.path.exists(dump_dir):
                    os.mkdir(dump_dir)
                dir_file=None
                with zipfile.ZipFile(data_file.name, 'r') as z:
                    # only extract known members!
                    filestore = [m for m in z.namelist()]
                    z.extractall(dump_dir, filestore) #解压缩文件到临时目录
                    for i in os.listdir(dump_dir):
                        ii = "sanger_"+i
                        if os.path.isdir(os.path.join(dump_dir,i)):
                            if os.path.exists(os.path.join("/data/odoo/library",ii)):
                                shutil.rmtree(os.path.join("/data/odoo/library",ii))

                            shutil.move(os.path.join(dump_dir,i),os.path.join("/data/odoo/library",ii))
                            dir_file=os.path.join("/data/odoo/library",ii)
                    if os.path.exists(dump_dir):os.removedirs(dump_dir)
                    env = os.environ.copy()

                    with open(os.path.join(dir_file,"out.log"),'w') as dn:
                        rc = subprocess.call(("perl","/data/odoo/library/bin/Sanger.operation.pl",dir_file,obj.output_name), env=env, stdout=dn, stderr=subprocess.STDOUT)
                        if rc:
                            raise Exception('Command Error.')

                        for i in os.listdir(dir_file):
                            if i.split(".")[-1]=="xls":
                                 f=open(os.path.join(dir_file,i),'rb')
                                 self.write(cr,uid,id,{"state":"done","filename":i,"excel": base64.encodestring(f.read())})
                                 f.close()

                        return {
                                'type': 'ir.actions.act_window',
                                'res_model': 'rhwl.genes.analyze',
                                'view_mode': 'form',
                                'view_type': 'form',
                                'res_id': obj.id,
                                'views': [(False, 'form')],
                                'target': 'new',
                            }

            else:
                os.unlink(data_file.name)
                _logger.warning('File format is not ZIP')
                raise Exception("File format is not ZIP")

        finally:
            if os.path.exists(data_file.name):os.unlink(data_file.name)
        return True