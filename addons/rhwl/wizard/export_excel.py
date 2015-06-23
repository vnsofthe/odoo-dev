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
class export_excel(osv.osv_memory):
    _name = "sale.sample.export.excel"
    _description = "Sample Excel Report"
    _columns={
        "file":fields.binary(u"文件"),
        "name":fields.char("File Name"),
        "state":fields.selection([('draft','Draft'),('done','Done')],string="State"),
    }

    _defaults={
        "state":'draft'
    }

    def action_excel(self,cr,uid,ids,context=None):
        if not context:
            context={}
        if context.get('func_name','')=='report1':
            return self.action_excel_bx(cr,uid,ids,context=context)
        elif context.get('func_name','')=='report2':
            return self.action_excel_fy(cr,uid,ids,context=context)

    def action_excel_bx(self,cr,uid,ids,context=None):
        if not context.get("active_ids"):return
        fileobj = NamedTemporaryFile('w+',delete=True)
        xlsname =  fileobj.name
        fileobj.close()
        ids=context.get("active_ids")
        if isinstance(ids,(list,tuple)):
            ids.sort()

        w = xlwt.Workbook(encoding='utf-8')
        ws = w.add_sheet("Sheet1")

        ws.write(0,0,u"检测编号")
        ws.write(0,1,u"孕妇姓名")
        ws.write(0,2,u"手机号")
        ws.write(0,3,u"身份证号")
        ws.write(0,4,u"采血日期")

        rows=1
        for i in self.pool.get("sale.sampleone").browse(cr,uid,ids,context=context):
            ws.write(rows,0,i.name)
            ws.write(rows,1,i.yfxm)
            ws.write(rows,2,i.yftelno)
            ws.write(rows,3,i.yfzjmc_no)
            ws.write(rows,4,i.cx_date)
            rows+=1

        w.save(xlsname)
        f=open(xlsname,'rb')

        id = self.create(cr,uid,{"state":"done","file":base64.encodestring(f.read()),"name":u"保险信息单.xls"})
        f.close()
        os.remove(xlsname)

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.sample.export.excel',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': id,
            'views': [(False, 'form')],
            'target': 'new',
            'name':u"导出保险信息单Excel"
        }

    def action_excel_fy(self,cr,uid,ids,context=None):
        if not context.get("active_ids"):return
        fileobj = NamedTemporaryFile('w+',delete=True)
        xlsname =  fileobj.name
        fileobj.close()
        ids=context.get("active_ids")
        if isinstance(ids,(list,tuple)):
            ids.sort()

        w = xlwt.Workbook(encoding='utf-8')
        ws = w.add_sheet("Sheet1")

        ws.write(1,0,u"中心条码")
        ws.write(1,1,u"病人姓名")
        ws.write(1,2,u"年龄")
        ws.write(1,3,u"孕周")
        ws.write(1,4,u"采样日期")
        ws.write(1,5,u"送检医院")
        ws.write(1,6,u"送检人员")
        ws.write(1,7,u"临床收费")
        ws.write(1,8,u"备注")


        rows=1
        for i in self.pool.get("sale.sampleone").browse(cr,uid,ids,context=context):
            ws.write(rows,0,i.name)
            ws.write(rows,1,i.yfxm)
            ws.write(rows,2,i.yftelno)
            ws.write(rows,3,i.yfzjmc_no)
            ws.write(rows,4,i.cx_date)
            rows+=1

        w.save(xlsname)
        f=open(xlsname,'rb')

        id = self.create(cr,uid,{"state":"done","file":base64.encodestring(f.read()),"name":u"费用结算单.xls"})
        f.close()
        os.remove(xlsname)

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.sample.export.excel',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': id,
            'views': [(False, 'form')],
            'target': 'new',
            'name':u"导出费用结算单Excel"
        }
