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
        "file_data":fields.binary(string=u"合并后文件"),
        "name":fields.char("Name"),
        "state":fields.selection([("draft","draft"),("done","done")],string="State"),
    }
    _defaults={
        "state":"draft",
        "name":u"位点合并结果.xls"
    }

    def action_merge(self,cr,uid,id,context=None):
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
               raise osv.except_osv(u"打开出错",u"请确认文件格式是否为正确的报告标准格式。")
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

class rhwl_analyze(osv.osv_memory):
    _name = "rhwl.genes.analyze"
    _columns = {
        "zip":fields.binary(string=u"检测数据压缩包",required=True),
        "excel":fields.binary(string=u"分析结果"),
        "filename":fields.char("Name"),
        "state":fields.selection([("draft","draft"),("done","done")],string="State"),
    }
    _defaults={
        "state":"draft"
    }

    def action_analyze(self,cr,uid,id,context=None):
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
                    filestore = [m for m in z.namelist() if m.endswith('fsa')]
                    z.extractall(dump_dir, filestore)
                    for i in os.listdir(dump_dir):
                        if os.path.isdir(os.path.join(dump_dir,i)):
                            shutil.move(os.path.join(dump_dir,i),os.path.join("d:\\",i))
                            dir_file=i
                    os.remove(dump_dir)
                    env = os.environ.copy()
                    with open(os.devnull) as dn:
                        rc = subprocess.call(("/home/rd/test/snp.sh",) + dir_file, env=env, stdout=dn, stderr=subprocess.STDOUT)
                        if rc:
                            raise Exception('Command Error.')
            else:
                os.unlink(data_file.name)
                _logger.warning('File format is not ZIP')
                raise Exception("File format is not ZIP")

        finally:
            if os.path.exists(data_file.name):os.unlink(data_file.name)
        return True