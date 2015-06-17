# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import time

from openerp.osv import fields, osv
from openerp.tools.translate import _
import xlwt
import base64
import os
from tempfile import NamedTemporaryFile
import tempfile
import openerp
import logging
import zipfile
import subprocess

_logger = logging.getLogger(__name__)
class rhwl_export_excel(osv.osv_memory):
    _name = "rhwl.gene.export.excel"
    _description = "Rhwl Excel Report"
    _columns={
        "file":fields.binary(u"文件"),
        "name":fields.char("File Name"),
        "state":fields.selection([('draft','Draft'),('done','Done')],string="State"),
    }

    _defaults={
        "state":'draft'
    }

    def action_excel(self,cr,uid,ids,context=None):
        if not context.get("active_ids"):return
        fileobj = NamedTemporaryFile('w+',delete=True)
        xlsname =  fileobj.name
        fileobj.close()
        if not os.path.exists(xlsname):
            os.mkdir(xlsname)

        ids=context.get("active_ids")
        if isinstance(ids,(list,tuple)):
            ids.sort()

        w = xlwt.Workbook(encoding='utf-8')
        ws = w.add_sheet(u"样本问题反馈")
        ws.write(0,0,u"序号")
        ws.write(0,1,u"基因样品编码"),
        ws.write(0,2,u"姓名"),
        ws.write(0,3,u"性别"),
        ws.write(0,4,u"身份证号"),
        ws.write(0,5,u"备注"),
        ws.write(0,6,u"手机号"),
        ws.write(0,7,u"会员部反馈")
        ws.col(1).width = 4500 #1000 = 3.14(Excel)
        ws.col(4).width = 7000
        ws.col(5).width = 8000

        rows=1
        seq=1
        old_date=""
        file_s=""
        file_e=""
        for i in self.pool.get("rhwl.easy.genes").browse(cr,uid,ids,context=context):
            if not file_s:
                file_s=i.date.split("-")
                file_s=str(int(file_s[1]))+"."+str(int(file_s[2]))

            if i.date != old_date:
                old_date = i.date.split("-")
                ws.write(rows,0,str(int(old_date[1]))+u"月"+str(int(old_date[2]))+u"日")
                rows += 1
                seq = 1
            image_dir=".".join([str(int(k)) for k in i.date.split("-")[1:]]) + u"日邮寄样本问题反馈图片"

            if i.img_new:
                if not os.path.exists(os.path.join(xlsname,image_dir)):
                    os.mkdir(os.path.join(xlsname,image_dir))
                image_file = os.path.join(os.path.join(xlsname,image_dir),i.name+i.cust_name+u".png")
                f=open(image_file,'wb')
                f.write(base64.decodestring(i.img_new))
                f.close()

            ws.write(rows,0,seq)
            ws.write(rows,1,i.name)
            ws.write(rows,2,i.cust_name)
            ws.write(rows,3,u"男" if i.sex==u"T" else u"女")
            ws.write(rows,4,True and i.identity or "")
            ws.write(rows,5,i.except_note)
            ws.write(rows,6,True and i.mobile or "")
            ws.write(rows,7,True and i.confirm_note or "")
            rows +=1
            seq += 1
            old_date=i.date

            file_e=i.date.split("-")
            file_e=str(int(file_e[1]))+"."+str(int(file_e[2]))

        if file_s==file_e:
            file_str=file_s
        else:
            file_str = file_s+"-"+file_e

        w.save(os.path.join(xlsname,file_str+u"邮寄样本问题反馈.xls"))

        os.system("cd "+xlsname+"/;zip -r "+os.path.join(xlsname,file_str+"邮寄样本问题反馈.zip")+" ./*")
            #rc = subprocess.Popen(("zip","-r",,"./*"), cwd=xlsname,env=env, stdout=dn, stderr=subprocess.STDOUT)
            #if rc:
            #    raise Exception('ZIP Command Error.'+rc)
        f=open(os.path.join(xlsname,file_str+u"邮寄样本问题反馈.zip"),'rb')
        id = self.create(cr,uid,{"state":"done","name":file_str+u"邮寄样本问题反馈.zip","file": base64.encodestring(f.read())})
        f.close()
        os.system("rm -Rf "+xlsname)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rhwl.gene.export.excel',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': id,
            'views': [(False, 'form')],
            'target': 'new',
            'name':u"导出样本问题反馈Excel"
        }

    def zip_dir(self,path, stream, include_dir=True):      # TODO add ignore list
        path = os.path.normpath(path)
        len_prefix = len(os.path.dirname(path)) if include_dir else len(path)
        if len_prefix:
            len_prefix += 1

        with zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_DEFLATED, allowZip64=True) as zipf:
            for dirpath, dirnames, filenames in os.walk(path):

                for fname in filenames:

                    bname, ext = os.path.splitext(fname)
                    ext = ext or bname
                    if ext not in ['.pyc', '.pyo', '.swp', '.DS_Store']:
                        path = os.path.normpath(os.path.join(dirpath, fname))

                        if os.path.isfile(path):
                            zipf.write(path, path[len_prefix:].decode('utf-8'))

    def get_excel_style(self,font_size=10,horz=xlwt.Alignment.HORZ_LEFT,border=xlwt.Borders.NO_LINE):
        #18号字，加边框，水平靠右，垂直居中
        style2 = xlwt.XFStyle()
        style2.font = xlwt.Font()
        style2.font.name=u"宋体"
        style2.font.height = 20*font_size
        style2.alignment = xlwt.Alignment()
        style2.alignment.horz = horz
        style2.alignment.vert = xlwt.Alignment.VERT_CENTER
        style2.borders = xlwt.Borders() # Add Borders to Style
        style2.borders.left = border # May be: NO_LINE, THIN, MEDIUM, DASHED, DOTTED, THICK, DOUBLE, HAIR, MEDIUM_DASHED, THIN_DASH_DOTTED, MEDIUM_DASH_DOTTED, THIN_DASH_DOT_DOTTED, MEDIUM_DASH_DOT_DOTTED, SLANTED_MEDIUM_DASH_DOTTED, or 0x00 through 0x0D.
        style2.borders.right = border
        style2.borders.top = border
        style2.borders.bottom = border
        style2.borders.left_colour = 0x40
        style2.borders.right_colour = 0x40
        style2.borders.top_colour = 0x40
        style2.borders.bottom_colour = 0x40
        return style2