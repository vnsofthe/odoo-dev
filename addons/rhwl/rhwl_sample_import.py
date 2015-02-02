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

#
# Order Point Method:
#    - Order if the virtual stock of today is bellow the min of the defined order point
#

import threading
from openerp.osv import osv,fields
import base64
from tempfile import NamedTemporaryFile
import xlrd,os

class rhwl_import(osv.osv_memory):
    _name = 'sale.sampleone.import.report'
    _columns = {
        "file_bin":fields.binary(string=u"文件名",required=True),
    }

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
            print xlsname+".xls"
            bk = xlrd.open_workbook(xlsname+".xls")
            try:
                sh = bk.sheet_by_index(0)
            except:
                print "no sheet in Sheet1"
                return None
            nrows = sh.nrows
            ncols = sh.ncols
            for i in range(2,nrows+1):
                ids = self.pool.get("sale.sampleone").search(cr,uid,[("name","=",sh.cell_value(i-1,0))])
                if not ids:
                    raise osv.except_osv(u"接收检测结果出错",u"样品编号[%s]在系统中不存在。" %(sh.cell_value(i-1,0),))
                t13 = sh.cell_value(i-1,1)
                t18 = sh.cell_value(i-1,2)
                t21 = sh.cell_value(i-1,3)
                self.pool.get("sale.sampleone").write(cr,uid,ids,{"lib_t13":t13,"lib_t18":t18,"lib_t21":t21})
                if t13<3 and t13>-3 and t18<3 and t18>-3 and t21<3 and t21>-3:
                    self.pool.get("sale.sampleone").action_check_ok(cr,uid,ids,context=context)
                else:
                    self.pool.get("sale.sampleone").action_check_except(cr,uid,ids,context=context)

        finally:
            fileobj.close()
            f.close()
        return True