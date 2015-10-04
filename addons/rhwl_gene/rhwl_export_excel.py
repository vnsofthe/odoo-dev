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
import shutil

_logger = logging.getLogger(__name__)
class rhwl_export_excel(osv.osv_memory):
    _name = "rhwl.gene.export.excel"
    _description = "Rhwl Excel Report"
    _columns={
        "file":fields.binary(u"文件"),
        "name":fields.char("File Name"),
        "state":fields.selection([('draft','Draft'),('netdisk','NetDisk'),('excel','Excel'),('done','Done')],string="State"),
    }

    _defaults={
        "state":'draft'
    }

    def action_excel(self,cr,uid,ids,context=None):
        if not context:
            context={}
        if context.get('func_name','')=='informat':
            return self.action_excel_informat(cr,uid,ids,context=context)
        elif context.get('func_name','')=='dna':
            return self.action_excel_dna(cr,uid,ids,context=context)
        elif context.get('func_name','')=="snp":
            return self.action_excel_snp(cr,uid,ids,context=context)
        elif context.get("func_name","")=="gene_new_picking":
            return self.action_excel_gene_new(cr,uid,ids,context=context)

    def action_excel_gene_new(self,cr,uid,ids,context=None):
        if not context.get("active_id"):return
        ids = context.get("active_id")
        picking_obj = self.pool.get("rhwl.genes.new.picking").browse(cr,uid,ids,context=context)
        w = xlwt.Workbook(encoding='utf-8')
        ws = w.add_sheet(u"易感机构发货")
        ws.col(1).width =3500
        ws.write(0,0,u"送检机构")
        ws.write(0,1,u"套餐")
        ws.write(0,2,u"样本编号")
        ws.write(0,3,u"姓名")
        ws.write(0,4,u"性别")
        excel_row=1
        genes_ids = self.pool.get("rhwl.genes.new.picking.line.detail").search(cr,uid,[("line_id.picking_id.id","=",ids),("genes_id.is_single_post","=",False)],context=context)
        genes_ids = self.pool.get("rhwl.easy.genes.new").search(cr,uid,[("id","in",genes_ids)],order="hospital,package_id,name",context=context)
        for i in self.pool.get("rhwl.easy.genes.new").browse(cr,uid,genes_ids,context=context):
            ws.write(excel_row,0,i.hospital.name)
            ws.write(excel_row,1,i.package_id.code+i.package_id.name)
            ws.write(excel_row,2,i.name)
            ws.write(excel_row,3,i.cust_name)
            ws.write(excel_row,4,u"男" if i.sex=="M" else u"女")
            excel_row +=1

        #导出单独邮寄
        genes_ids = self.pool.get("rhwl.genes.new.picking.line.detail").search(cr,uid,[("line_id.picking_id.id","=",ids),("genes_id.is_single_post","=",True)],context=context)
        if genes_ids:
            ws2 = w.add_sheet(u"单独邮寄")
            ws2.col(1).width =3500
            ws2.write(0,0,u"送检机构")
            ws2.write(0,1,u"套餐")
            ws2.write(0,2,u"样本编号")
            ws2.write(0,3,u"姓名")
            ws2.write(0,4,u"性别")
            ws2.write(0,5,u"联系电话")
            ws2.write(0,6,u"邮寄地址")

            excel_row=1

            genes_ids = self.pool.get("rhwl.easy.genes.new").search(cr,uid,[("id","in",genes_ids)],order="hospital,package_id,name",context=context)
            for i in self.pool.get("rhwl.easy.genes.new").browse(cr,uid,genes_ids,context=context):
                ws2.write(excel_row,0,i.hospital.name)
                ws2.write(excel_row,1,i.package_id.code+i.package_id.name)
                ws2.write(excel_row,2,i.name)
                ws2.write(excel_row,3,i.cust_name)
                ws2.write(excel_row,4,u"男" if i.sex=="M" else u"女")
                ws2.write(excel_row,5,i.mobile)
                ws2.write(excel_row,6,"".join([x for x in [i.state_id.name,i.city_id.name,i.area_id.name,i.address] if x]))
                excel_row +=1
        fileobj = NamedTemporaryFile('w+',delete=True)
        xlsname =  fileobj.name
        fileobj.close()
        w.save(xlsname)
        f=open(xlsname,'rb')
        id=self.create(cr,uid,{"file":base64.encodestring(f.read()),"name":picking_obj.name+u"易感发货单.xls","state":"excel"})
        f.close()
        os.remove(xlsname)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rhwl.gene.export.excel',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': id,
            'views': [(False, 'form')],
            'target': 'new',
            'name':u"导出新易感发货单Excel"
        }

    def action_excel_snp(self,cr,uid,ids,context=None):
        if not context.get("active_ids"):return
        ids=context.get("active_ids")
        if isinstance(ids,(list,tuple)):
            ids.sort()
        w = xlwt.Workbook(encoding='utf-8')
        ws = w.add_sheet("Sheet1")
        ws.col(1).width =3500
        ws.write(0,0,u"批次")
        ws.write(0,1,u"基因编码")
        ws.write(0,2,u"姓名")
        ws.write(0,3,u"性别")
        header=[]

        rows=1
        for i in self.pool.get("rhwl.easy.genes.batch").browse(cr,uid,ids,context=context):
            gene_ids = self.pool.get("rhwl.easy.genes").search(cr,uid,[("batch_no","=",i.name),("typ","!=",False)])
            data = self.pool.get("rhwl.easy.genes").get_gene_type_list(cr,uid,gene_ids,context=context)
            for k,v in data.items():
                for k1,v1 in v.items():
                    ws.write(rows,0,i.name)
                    ws.write(rows,1,k1)
                    ws.write(rows,2,v1.get("cust_name"))
                    ws.write(rows,3,u"男" if k=="M" else u"女")

                    if not header:
                        header = v1.keys()
                        header.remove("name")
                        header.remove("cust_name")
                        header.sort()
                        for s in header:
                            ws.write(0,header.index(s)+4,s)
                    for s in header:
                        ws.write(rows,header.index(s)+4,v1[s])
                    rows+=1
        fileobj = NamedTemporaryFile('w+',delete=True)
        xlsname =  fileobj.name
        fileobj.close()
        w.save(xlsname)
        f=open(xlsname,'rb')
        id=self.create(cr,uid,{"file":base64.encodestring(f.read()),"name":u"位点数据.xls","state":"excel"})
        f.close()
        os.remove(xlsname)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rhwl.gene.export.excel',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': id,
            'views': [(False, 'form')],
            'target': 'new',
            'name':u"导出位点数据Excel"
        }

    def action_excel_dna(self,cr,uid,ids,context=None):
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
        ws = w.add_sheet("Sheet1")

        ws.col(0).width =3500 #1000 = 3.14(Excel)
        ws.col(1).width = 4000


        rows=0

        old_date=""
        file_s=""
        file_e=""
        for i in self.pool.get("rhwl.easy.genes").browse(cr,uid,ids,context=context):
            if not file_s:
                file_s=i.date.split("-")
                file_s=str(int(file_s[1]))+"."+str(int(file_s[2]))

            if i.date != old_date:
                old_date = i.date.split("-")
                ws.write_merge(rows,rows,0,4,".".join(old_date)+u"会员部送检样品质检不合格名单",style=self.get_excel_style(font_size=11))
                rows += 1

            image_dir=".".join(i.date.split("-")) + u"会员部送检样品质检不合格报告"
            if not os.path.exists(os.path.join(xlsname,image_dir)):
                os.mkdir(os.path.join(xlsname,image_dir))

            if i.state=="dna_except":
                report_data = {'report_type':'pentaho'}
                report_id = openerp.service.report.exp_report("dev",1,'rhwl.gene.dna.except.ids',[i.id],report_data)

                report_struct = None
                while True:
                    report_struct = openerp.service.report.exp_report_get("dev", 1, report_id)
                    if report_struct["state"]:
                        break

                    time.sleep(0.25)

                rep = base64.b64decode(report_struct['result'])
                image_file = os.path.join(os.path.join(xlsname,image_dir),i.name+u"-"+i.cust_name+u".pdf")
                f=open(image_file,'wb')
                f.write(rep)
                f.close()

            ws.write(rows,0,i.name,style=self.get_excel_style(font_size=11))
            ws.write(rows,1,i.cust_name,style=self.get_excel_style(font_size=11))
            ws.write(rows,2,u"男" if i.sex==u"T" else u"女",style=self.get_excel_style(font_size=11))
            ws.write(rows,3,True and i.identity or "",style=self.get_excel_style(font_size=11))

            rows +=1

            old_date=i.date

            file_e=i.date.split("-")
            file_e=str(int(file_e[1]))+"."+str(int(file_e[2]))

        if file_s==file_e:
            file_str=file_s
        else:
            file_str = file_s+"-"+file_e

        w.save(os.path.join(xlsname,file_str+u"会员部送检样品质检不合格名单.xls"))

        if not os.path.exists(u"/data/odoo/file/upload/样本质检异常"):
            os.mkdir(u"/data/odoo/file/upload/样本质检异常")
        t_dir=u"/data/odoo/file/upload/样本质检异常/"+file_str+u"会员部送检样品质检不合格名单及报告"
        if not os.path.exists(t_dir):
            os.mkdir(t_dir)

        for i in os.listdir(xlsname):
            if os.path.exists(os.path.join(t_dir,i.decode('utf-8'))):
                if os.path.isdir(os.path.join(t_dir,i.decode('utf-8'))):
                    shutil.rmtree(os.path.join(t_dir,i.decode('utf-8')))
                else:
                    os.remove(os.path.join(t_dir,i.decode('utf-8')))
            shutil.move(os.path.join(xlsname,i.decode('utf-8')),os.path.join(t_dir,i.decode('utf-8')))

        id = self.create(cr,uid,{"state":"netdisk",})

        os.system("rm -Rf "+xlsname)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rhwl.gene.export.excel',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': id,
            'views': [(False, 'form')],
            'target': 'new',
            'name':u"导出质检异常Excel"
        }

    def action_excel_informat(self,cr,uid,ids,context=None):
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
        ws.write(0,0,u"序号",style=self.get_excel_style(font_size=11))
        ws.write(0,1,u"基因样品编码",style=self.get_excel_style(font_size=11)),
        ws.write(0,2,u"姓名",style=self.get_excel_style(font_size=11)),
        ws.write(0,3,u"性别",style=self.get_excel_style(font_size=11)),
        ws.write(0,4,u"身份证号",style=self.get_excel_style(font_size=11)),
        ws.write(0,5,u"备注",style=self.get_excel_style(font_size=11)),
        ws.write(0,6,u"手机号",style=self.get_excel_style(font_size=11)),
        ws.write(0,7,u"会员部反馈",style=self.get_excel_style(font_size=11))
        ws.col(1).width = 4500 #1000 = 3.14(Excel)
        ws.col(4).width = 7000
        ws.col(5).width = 8000
        ws.col(6).width = 6000
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

            ws.write(rows,0,seq,style=self.get_excel_style(font_size=11,horz=xlwt.Alignment.HORZ_CENTER))
            ws.write(rows,1,i.name,style=self.get_excel_style(font_size=11))
            ws.write(rows,2,i.cust_name,style=self.get_excel_style(font_size=11))
            ws.write(rows,3,u"男" if i.sex==u"T" else u"女",style=self.get_excel_style(font_size=11))
            ws.write(rows,4,True and i.identity or "",style=self.get_excel_style(font_size=11))
            ws.write(rows,5,i.except_note,style=self.get_excel_style(font_size=11))
            ws.write(rows,6,True and i.mobile or "",style=self.get_excel_style(font_size=11))
            ws.write(rows,7,True and i.confirm_note or "",style=self.get_excel_style(font_size=11))
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

        if not os.path.exists(u"/data/odoo/file/upload/样本问题反馈"):
            os.mkdir(u"/data/odoo/file/upload/样本问题反馈")
        t_dir=u"/data/odoo/file/upload/样本问题反馈/"+file_str+u"邮寄样本问题反馈"
        if not os.path.exists(t_dir):
            os.mkdir(t_dir)

        for i in os.listdir(xlsname):
            if os.path.exists(os.path.join(t_dir,i.decode('utf-8'))):
                if os.path.isdir(os.path.join(t_dir,i.decode('utf-8'))):
                    shutil.rmtree(os.path.join(t_dir,i.decode('utf-8')))
                else:
                    os.remove(os.path.join(t_dir,i.decode('utf-8')))
            shutil.move(os.path.join(xlsname,i.decode('utf-8')),os.path.join(t_dir,i.decode('utf-8')))

        id = self.create(cr,uid,{"state":"netdisk",})

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