# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID, api
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import openerp.tools.osutil
import datetime
import requests
import logging
import os
import shutil
import xlwt
import re
_logger = logging.getLogger(__name__)

#样本发货单对象
class rhwl_picking(osv.osv):
    _name="rhwl.genes.new.picking"

    BOX_TO_PICKING={}
    BATCH_TO_PICKING={}

    BOX_TO_BATCH={}


    def _get_files(self,cr,uid,ids,field_names,arg,context=None):
        res=dict.fromkeys(ids,0)
        for i in self.browse(cr,uid,ids,context=context):
            for l in i.line:
                res[i.id] = res[i.id]+l.qty
        return res

    def _get_batchs(self,cr,uid,ids,field_name,arg,context=None):
        res=dict.fromkeys(ids,"")
        for i in self.browse(cr,uid,ids,context=context):
            batch=[]
            for b in i.line:
                if b.batch_kind=="normal":
                    batch.append(b.batch_no)
            res[i.id]=','.join(batch)
        return res

    _order="date desc"
    _columns={
        "name":fields.char(u"发货单号",size=10,required=True),
        "date":fields.date(u"预计发货日期",required=True),
        "real_date":fields.date(u"实际发货日期",),
        "state":fields.selection([("draft",u"草稿"),("upload",u"已上传"),("send",u"印刷已接收"),("done",u"完成")],u"状态"),
        "files":fields.function(_get_files,type="integer",string=u"合计样本数"),
        "upload":fields.integer(u"已上传文件数",readonly=True),
        "note":fields.char(u"备注",size=300),
        "batchs":fields.function(_get_batchs,type="char",string=u"发货批号"),
        "line":fields.one2many("rhwl.genes.new.picking.line","picking_id","Detail"),
        "box":fields.one2many("rhwl.genes.new.picking.box","picking_id",string="Box",readonly=True),
    }
    _defaults={
        "date":fields.date.today,
        "state":"draft",
    }
    #重载更新方法，发货单状态更新时，同时更新发货单对应的所有样本信息状态。
    def write(self,cr,uid,ids,val,context=None):
        id=super(rhwl_picking,self).write(cr,uid,ids,val,context=context)
        if val.has_key("state"):
            stat = {
                "draft":'result_done',
                "send":'deliver',
                "done":'done',
                "upload":"result_done"
            }
            objs=self.browse(cr,uid,ids,context=context)
            genes_id=[]
            for i in objs.line:
                for j in i.box_line:
                    for k in j.detail:
                       genes_id.append(k.genes_id.id)
            self.pool.get("rhwl.easy.genes.new").write(cr,uid,genes_id,{"state":stat[val["state"]]},context=context)
        return id

    def pdf_copy(self,cr,uid,pdf_path,d_path,files):
        u_count = 0
        t_count = 0

        for k,v in files.items():
            for k1,v1 in v.items():
                t_count += len(v1)
                for i in v1:
                    if os.path.exists(os.path.join(pdf_path,i[0])):
                        f_path = os.path.join(os.path.join(d_path,k),k1)
                        if (not os.path.exists(os.path.join(f_path,i[0]))) or os.stat(os.path.join(pdf_path,i[0])).st_size != os.stat(os.path.join(f_path,i[0])).st_size:
                            shutil.copy(os.path.join(pdf_path,i[0]),os.path.join(f_path,i[0]))

                        u_count += 1
        return (t_count,u_count)

    #根据发货单，生成需要上传的目录结构，并复制pdf文件到相应的目录中。
    def report_upload(self,cr,uid,context=None):
        for i in self.search(cr,uid,[("state","=","draft")],context=context):
            self.action_pdf_upload(cr,uid,i,context=context)

    def action_pdf_upload(self,cr,uid,id,context=None):
        upload_path = os.path.join(os.path.split(__file__)[0], "static/local/upload/yg")
        pdf_path = os.path.join(os.path.split(__file__)[0], "static/local/report/yg")

        if isinstance(id,(long,int)):
            id=[id]

        for i in id:
            obj=self.browse(cr,uid,i,context=context)
            d=obj.date.replace("/","").replace("-","") #发货单需创建的目录名称
            d_path=os.path.join(upload_path,d)
            files={}
            if not os.path.exists(d_path):
                os.mkdir(d_path)
            for l in obj.line:
                if l.qty==0:continue
                k1=l.batch_no+"-"+str(l.qty)
                line_path=os.path.join(d_path,k1)
                if not os.path.exists(line_path):
                    os.mkdir(line_path)
                if not files.has_key(k1):files[k1]={}

                for b in l.detail:
                    k2=b.genes_id.package_id.code + "." +b.genes_id.package_id.name
                    box_path=os.path.join(line_path,k2)
                    if not os.path.exists(box_path):
                        os.mkdir(box_path)

                    if not files[k1].has_key(k2):files[k1][k2]=[]

                    pdf_file = b.genes_id.name+".pdf"
                    files[k1][k2].append([pdf_file,b.genes_id.name,b.genes_id.cust_name,b.genes_id.sex])

            t_count,u_count=self.pdf_copy(cr,uid,pdf_path,d_path,files)

            vals={
                "upload":u_count,
            }
            if obj.files==u_count:
                vals["state"]="upload"
            self.write(cr,uid,i,vals,context=context)
            #生成印刷版的发货单
            self.export_excel_to_print(d_path,files)

    def export_excel_to_print(self,d_path,files):
        w = xlwt.Workbook(encoding='utf-8')
        for k,v in files.items():
            ws = w.add_sheet(k)
            row=0
            batch=v.keys()
            batch.sort()
            for k1 in batch:
                for i in v[k1]:
                    ws.write(row,0,k)
                    ws.write(row,1,i[1])
                    ws.write(row,2,i[2])
                    ws.write(row,3,u"男" if i[3]=="M" else u"女" )
                    row +=1
        w.save(os.path.join(d_path,u"易感发货单(印刷)")+".xls")

#发货单批次明细对象
class rhwl_picking_line(osv.osv):
    _name = "rhwl.genes.new.picking.line"

    def _get_detail_qty(self,cr,uid,ids,field_names,arg,context=None):
        res=dict.fromkeys(ids,0)
        for k in res.keys():
            res[k] = self.pool.get("rhwl.genes.new.picking.line.detail").search_count(cr,uid,[("line_id.id","=",k)])
        return res

    _order = "seq"
    _columns={
        "picking_id":fields.many2one("rhwl.genes.new.picking",u"发货单号",ondelete="restrict"),
        "seq":fields.integer(u"序号",required=True),
        "product_name":fields.char(u"货品名称",size=20),
        "batch_no":fields.char(u"批号",size=15,required=True),
        "batch_kind":fields.selection([("normal",u"普通"),("resend",u"破损重印")],u"类型"),
        "qty":fields.function(_get_detail_qty,arg="batch_no",type="integer",string=u"数量"),
        "note":fields.char(u"备注",size=200),
        "detail":fields.one2many("rhwl.genes.new.picking.line.detail","line_id","Detail"),

    }
    _defaults={
        "product_name":u"检测报告",
        "batch_kind":"normal",

    }
    _sql_constraints = [
        ('rhwl_genes_picking_seq_uniq', 'unique(picking_id,seq)', u'发货明细序号不能重复!'),
    ]

    @api.onchange("batch_kind")
    def _onchange_batch_kind(self):
        if self.batch_kind=="resend":
            self.batch_no="破损重印"
        else:
            self.batch_no=""

    def create(self,cr,uid,val,context=None):
        if val.get("seq",0)<=0:
            raise osv.except_osv(u'错误',u'发货明细的序号必须大于0')
        if val.get("batch_kind")=="normal":
            ids=self.pool.get("rhwl.easy.genes.new").search(cr,uid,[("batch_no","=",val.get("batch_no"))],context=context)
            if not ids:
                raise osv.except_osv(u"错误",u"批次号不存在，请输入正确的批次号码。")
            else:
                val["detail"]=[]
                for i in ids:
                    val["detail"].append([0,0,{"genes_id":i}])

        line_id = super(rhwl_picking_line,self).create(cr,uid,val,context=context)

        return line_id

class rhwl_picking_detail(osv.osv):
    _name="rhwl.genes.new.picking.line.detail"
    _columns={
        "line_id":fields.many2one("rhwl.genes.new.picking.line",u"批号",ondelete="cascade"),
        "genes_id":fields.many2one("rhwl.easy.genes.new",u"样本编号",ondelete="restrict",required=True),
        "name":fields.related("genes_id","cust_name",type="char",string=u"会员姓名"),

    }

class rhwl_picking_box(osv.osv):
    _name = "rhwl.genes.new.picking.box"
    _columns={
        "picking_id":fields.many2one("rhwl.genes.new.picking",u"发货单号",ondelete="restrict"),
        "partner_id":fields.many2one("res.partner",string=u"收件方",),
        "partner_text":fields.char(u"收件方",size=100),
        "address":fields.char(u"详细地址",size=150),
        "mobile": fields.char(u"手机号码", size=20),
        "qty":fields.integer(u"数量"),
        "express_id":fields.many2one("stock.picking.express",u"快递单",ondelete="restrict")
    }