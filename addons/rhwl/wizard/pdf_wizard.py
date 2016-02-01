# -*- coding: utf-8 -*-

import threading
from openerp.osv import osv,fields
from openerp import SUPERUSER_ID
import base64
from tempfile import NamedTemporaryFile
import xlrd,os
import datetime
import logging
import xlwt
import zipfile
import shutil
import subprocess
import re
_logger = logging.getLogger(__name__)

class pdf_wizard(osv.osv_memory):
    _name = "rhwl.sample.one.zip"
    _columns={
        "file_bin":fields.binary(string=u"压缩文件",required=True),
        "name":fields.char("Name"),
        "state":fields.selection([("draft","draft"),("done","done")],string="State"),
    }
    _defaults={
        "state":"draft",
    }

    def pdf_update(self,cr,uid,name,file,context=None):
        sampleone = self.pool.get("sale.sampleone")
        id = sampleone.search(cr,uid,[("name","=",name)],context=context)

        if not id:return
        obj = sampleone.browse(cr,uid,id,context=context)
        f=open(file,"rb")
        img = f.read()
        f.close()
        vals={
            "name":name+"_"+obj.yfxm+".pdf",
            "datas_fname":name+"_"+obj.yfxm+".pdf",
            "description":name+"_"+obj.yfxm+".pdf",
            "res_model":"sale.sampleone",
            "res_id":obj.id,
            "create_date":fields.datetime.now,
            "create_uid":SUPERUSER_ID,
            "datas":base64.b64encode(img),
        }
        atta_obj = self.pool.get('ir.attachment')
        return atta_obj.create(cr,SUPERUSER_ID,vals)

    def zip_upload(self,cr,uid,id,context=None):
        if context is None:
            context = {}
        obj = self.browse(cr, uid, id,context=context)
        if not obj.file_bin:
            raise osv.except_osv("Error","上传文件不可以为空。")

        data_file = NamedTemporaryFile(delete=False)

        try:
            data_file.write(obj.file_bin.decode('base64'))
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
                        if os.path.isfile(os.path.join(dump_dir,i)):
                            name_list = re.split("[_\.]",i) #分解文件名称
                            if len(name_list)==6:
                                self.pdf_update(cr,uid,name_list[3],os.path.join(dump_dir,i),context=context)
                            os.unlink(os.path.join(dump_dir,i))
                        elif os.path.isdir(os.path.join(dump_dir,i)):
                            p_path = os.path.join(dump_dir,i)
                            for p in os.listdir(p_path):
                                if os.path.isfile(os.path.join(p_path,p)):
                                    name_list = re.split("[_\.]",p) #分解文件名称
                                    if len(name_list)==6:
                                        self.pdf_update(cr,uid,name_list[3],os.path.join(p_path,p),context=context)
                                    os.unlink(os.path.join(p_path,p))
                            os.removedirs(p_path)

                    if os.path.exists(dump_dir):os.removedirs(dump_dir)
                    env = os.environ.copy()
            else:
                os.unlink(data_file.name)
                _logger.warning('File format is not ZIP')
                raise Exception("File format is not ZIP")

        finally:
            if os.path.exists(data_file.name):os.unlink(data_file.name)
        return True