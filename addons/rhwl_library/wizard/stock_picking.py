# -*- coding: utf-8 -*-
import time

from openerp.osv import fields, osv
from openerp.tools.translate import _
import xlwt
import base64
import os
from tempfile import NamedTemporaryFile
import logging

_logging = logging.getLogger(__name__)
class stock_picking(osv.osv_memory):
    _name = "rhwl.library.excel.report"
    _description = "Excel Report"

    _columns={
        "file_bin":fields.binary(u"文件内容"),
        "file_name":fields.char(u"文件名"),
        "state":fields.selection([('draft','Draft'),('done','Done')],"State")
    }

    _defaults={
        "state":"draft"
    }

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

    def action_excel_report(self,cr,uid,ids,context=None):
        if not context.get("active_id"):return

        fileobj = NamedTemporaryFile('w+',delete=True)
        xlsname =  fileobj.name
        fileobj.close()

        w = xlwt.Workbook(encoding='utf-8')
        ws = w.add_sheet("Sheet1")
        ws.col(1).width = 9000 #1000 = 3.715(Excel)

        ws.write_merge(0,0,0,8,u"人和未来物资入库单",self.get_excel_style(18,xlwt.Alignment.HORZ_CENTER))

        rows=1
        for i in self.pool.get("stock.picking").browse(cr,uid,context.get("active_id"),context=context):
            if not i.pack_operation_ids:continue
            ws.write(rows,1,u"入库单号："+ i.name,self.get_excel_style(12))
            ws.write(rows,6,u"入库时间："+ i.date_done,self.get_excel_style(12))
            rows += 1
            ws.write(rows,0,u"序号",self.get_excel_style(12,border=xlwt.Borders.MEDIUM))
            ws.write(rows,1,u"产品",self.get_excel_style(12,border=xlwt.Borders.MEDIUM))
            ws.write(rows,2,u"品牌",self.get_excel_style(12,border=xlwt.Borders.MEDIUM))
            ws.write(rows,3,u"货号",self.get_excel_style(12,border=xlwt.Borders.MEDIUM))
            ws.write(rows,4,u"规格",self.get_excel_style(12,border=xlwt.Borders.MEDIUM))
            ws.write(rows,5,u"数量",self.get_excel_style(12,border=xlwt.Borders.MEDIUM))
            ws.write(rows,6,u"单位",self.get_excel_style(12,border=xlwt.Borders.MEDIUM))
            ws.write(rows,7,u"库位",self.get_excel_style(12,border=xlwt.Borders.MEDIUM))
            ws.write(rows,8,u"类别",self.get_excel_style(12,border=xlwt.Borders.MEDIUM))
            rows += 1
            row_seq=1
            for j in i.pack_operation_ids:
                ws.write(rows,0,row_seq,self.get_excel_style(12,border=xlwt.Borders.MEDIUM))
                ws.write(rows,1,j.product_id.name,self.get_excel_style(12,border=xlwt.Borders.MEDIUM))
                ws.write(rows,2,j.product_id.brand if j.product_id.brand else "",self.get_excel_style(12,border=xlwt.Borders.MEDIUM))
                ws.write(rows,3,j.product_id.default_code  if j.product_id.default_code else "",self.get_excel_style(12,border=xlwt.Borders.MEDIUM))
                ws.write(rows,4,j.product_id.attribute_value_ids.name if j.product_id.attribute_value_ids.name else "",self.get_excel_style(12,border=xlwt.Borders.MEDIUM))
                ws.write(rows,5,j.product_qty,self.get_excel_style(12,border=xlwt.Borders.MEDIUM))
                ws.write(rows,6,_(j.product_uom_id.name),self.get_excel_style(12,border=xlwt.Borders.MEDIUM))
                ws.write(rows,7,_(j.location_dest_id.display_name),self.get_excel_style(12,border=xlwt.Borders.MEDIUM))
                ws.write(rows,8,_(j.product_id.categ_id.name),self.get_excel_style(12,border=xlwt.Borders.MEDIUM))
                rows += 1

            rows += 2

        ws.write(rows,1,u"主管：",self.get_excel_style(12))
        ws.write(rows,6,u"入库人员：",self.get_excel_style(12))

        w.save(xlsname+".xls")
        f=open(xlsname+".xls",'rb')
        id = self.create(cr,uid,{"state":"done","file_name":u"入库单.xls","file_bin": base64.encodestring(f.read())})
        f.close()
        os.remove(xlsname+".xls")
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rhwl.library.excel.report',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': id,
            'views': [(False, 'form')],
            'target': 'new',
        }

