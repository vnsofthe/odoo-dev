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
import rhwl_reportlab
_logger = logging.getLogger(__name__)

#样本发货单对象
class rhwl_picking(osv.osv):
    _name="rhwl.genes.picking"

    BOX_TO_PICKING={}
    BATCH_TO_PICKING={}

    BOX_TO_BATCH={}

    def _get_picking_from_genes(self,cr,uid,gene_no,context=None):
        id=self.pool.get("rhwl.genes.picking.box.line").search(cr,uid,[("genes_id.name","=",gene_no)],context=context)
        if not id:
            return None
        obj=self.pool.get("rhwl.genes.picking.box.line").browse(cr,uid,id,context=context)
        if self.BOX_TO_PICKING.has_key(obj.box_id.id):
            return self.BOX_TO_PICKING.get(obj.box_id.id)
        if self.BATCH_TO_PICKING.has_key(obj.box_id.line_id.id):
            return self.BATCH_TO_PICKING.get(obj.box_id.line_id.id)
        no = obj.box_id.line_id.picking_id.name
        self.BOX_TO_PICKING[obj.box_id.id]=no
        self.BATCH_TO_PICKING[obj.box_id.line_id.id]=no
        return no

    def _get_batch_from_genes(self,cr,uid,picking,gene_no,context=None):
        id=self.pool.get("rhwl.genes.picking.box.line").search(cr,uid,[("genes_id.name","=",gene_no),("box_id.line_id.picking_id.name","=",picking)],context=context)
        if not id:
            return None
        obj=self.pool.get("rhwl.genes.picking.box.line").browse(cr,uid,id,context=context)
        if self.BOX_TO_BATCH.has_key(obj.box_id.id):
            return self.BOX_TO_BATCH.get(obj.box_id.id)
        no = obj.box_id.line_id.batch_no
        self.BOX_TO_BATCH[obj.box_id.id] = no
        return no

    def _clear_picking_dict(self):
        self.BOX_TO_PICKING={}
        self.BATCH_TO_PICKING={}
        self.BOX_TO_BATCH={}

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
        "line":fields.one2many("rhwl.genes.picking.line","picking_id","Detail"),
        "is_merge":fields.boolean(u"是否拼版"),
    }
    _defaults={
        "date":fields.date.today,
        "state":"draft",
        "is_merge":False,
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
            self.pool.get("rhwl.easy.genes").write(cr,uid,genes_id,{"state":stat[val["state"]]},context=context)
        return id

    def pdf_copy(self,cr,uid,pdf_path,files):
        u_count = 0
        t_count = 0
        lines=[]
        for k,v in files.items():
            t_count += len(v)
            for i in v:
                if os.path.exists(os.path.join(pdf_path,i[0])):
                    if (not os.path.exists(os.path.join(k,i[0]))) or os.stat(os.path.join(pdf_path,i[0])).st_size != os.stat(os.path.join(k,i[0])).st_size:
                        shutil.copy(os.path.join(pdf_path,i[0]),os.path.join(k,i[0]))
                    if lines.count(i[1])==0:
                        lines.append(i[1])
                        u_count += 1
        if lines:
            self.pool.get("rhwl.genes.picking.box.line").write(cr,uid,lines,{"has_pdf":True})
        return (t_count,u_count)

    #根据发货单，生成需要上传的目录结构，并复制pdf文件到相应的目录中。
    def report_upload(self,cr,uid,context=None):
        for i in self.search(cr,uid,[("state","=","draft")],context=context):
            self.report_upload_picking(cr,uid,i,context=context)

    def report_upload_picking(self,cr,uid,id,context=None):
        upload_path = os.path.join(os.path.split(__file__)[0], "static/local/upload/tjs")
        pdf_path = os.path.join(os.path.split(__file__)[0], "static/local/report")
        dict_level={
            "H":u"高风险",
            "L":u"低风险",
        }
        if isinstance(id,(long,int)):
            id=[id]
        #hardcode=[]
        is_upload=True


        for i in id: #循环处理发货单内容
            obj=self.browse(cr,uid,i,context=context)
            d=obj.date.replace("/","").replace("-","") #发货单需创建的目录名称
            d_path=os.path.join(upload_path,d)
            files={}
            if not os.path.exists(d_path):
                os.mkdir(d_path)
            for l in obj.line:#循环处理发货单下每个批次明细
                if not l.box_line:is_upload=False
                if l.qty==0:continue
                #if not l.export:is_upload=False
                #处理批号
                sheet_data={} #用于保存每个批次的装箱数据，给印刷厂查看
                if l.batch_kind=="normal":
                    line_path=os.path.join(d_path,l.batch_no+"-"+str(l.qty))
                    if not os.path.exists(line_path):
                        os.mkdir(line_path)
                    for b in l.box_line:#循环处理批次明细下每个箱号
                        box_path=os.path.join(line_path,dict_level[b.level])
                        if not os.path.exists(box_path):
                            os.mkdir(box_path)
                        box_path=os.path.join(box_path,str(l.seq)+"-"+b.name)
                        sheet_data[str(l.seq)+"-"+b.name]=[]
                        if not os.path.exists(box_path):
                            os.mkdir(box_path)
                        if not files.has_key(box_path):files[box_path]=[]
                        for bl in b.detail:#循环处理每个箱号下的样本
                            pdf_file = bl.genes_id.name+".pdf"
                            files[box_path].append([pdf_file,bl.id])
                            if bl.genes_id.language!="CN":
                                files[box_path].append([bl.genes_id.name+"_EN.pdf",bl.id])
                            if bl.genes_id.language not in ("CN","EN"):
                                files[box_path].append([bl.genes_id.name+"_"+bl.genes_id.language+".pdf",bl.id])
                            sheet_data[str(l.seq)+"-"+b.name].append([bl.genes_id.name,bl.genes_id.cust_name,bl.genes_id.sex,dict_level[b.level],bl.genes_id.date,bl.genes_id.batch_no])
                elif l.batch_kind=="resend":
                    line_path=os.path.join(d_path,u"重新印刷")
                    if not os.path.exists(line_path):
                        os.mkdir(line_path)
                    for b in l.box_line:
                        box_path=line_path
                        box_path=os.path.join(box_path,"R"+b.name)
                        if not os.path.exists(box_path):
                            os.mkdir(box_path)
                        sheet_data["R"+b.name]=[]
                        if not files.has_key(box_path):files[box_path]=[]
                        for bl in b.detail:
                            pdf_file = bl.genes_id.name+".pdf"
                            files[box_path].append([pdf_file,bl.id])
                            if bl.genes_id.language!="CN":
                                files[box_path].append([bl.genes_id.name+"_EN.pdf",bl.id])
                            if bl.genes_id.language not in ("CN","EN"):
                                files[box_path].append([bl.genes_id.name+"_"+bl.genes_id.language+".pdf",bl.id])
                            sheet_data["R"+b.name].append([bl.genes_id.name,bl.genes_id.cust_name,bl.genes_id.sex,u"重新印刷","",""])
                elif l.batch_kind=="vip":
                    line_path=os.path.join(d_path,u"会员部VIP")
                    if not os.path.exists(line_path):
                        os.mkdir(line_path)
                    for b in l.box_line:
                        box_path=line_path
                        box_path=os.path.join(box_path,"V"+b.name)
                        if not os.path.exists(box_path):
                            os.mkdir(box_path)
                        sheet_data["V"+b.name]=[]
                        if not files.has_key(box_path):files[box_path]=[]
                        for bl in b.detail:
                            pdf_file = bl.genes_id.name+".pdf"
                            files[box_path].append([pdf_file,bl.id])
                            if bl.genes_id.language!="CN":
                                files[box_path].append([bl.genes_id.name+"_EN.pdf",bl.id])
                            if bl.genes_id.language not in ("CN","EN"):
                                files[box_path].append([bl.genes_id.name+"_"+bl.genes_id.language+".pdf",bl.id])
                            sheet_data["V"+b.name].append([bl.genes_id.name,bl.genes_id.cust_name,bl.genes_id.sex,u"会员部VIP","",""])
                self.create_sheet_excel(line_path,sheet_data)
                self.picking_export_pdf(line_path,sheet_data)
            t_count,u_count=self.pdf_copy(cr,uid,pdf_path,files)
            if obj.is_merge:
                u_count += self.report_pdf_merge(cr,uid,obj.name,d,context=context)
                if t_count!=u_count/2:is_upload=False
            else:
                if t_count!=u_count:is_upload=False
            vals={
                "upload":u_count,
            }
            if is_upload:
                vals["state"]="upload"
            self.write(cr,uid,i,vals,context=context)
            self.excel_upload(cr,uid,i,False,context=context)
            if vals.get("state","")=="upload":
                self.report_pdf_zip(cr,uid,obj.name,d,context=context)

    #产生每个箱号下面的装箱单PDF
    def picking_export_pdf(self,line_path,data):
        report_lab = rhwl_reportlab.rhwl() #建立装箱单PDF对象
        pdf_path = os.path.join(line_path,u"装箱单")
        if not os.path.exists(pdf_path):
            os.mkdir(pdf_path)
        risk_name=""
        footer_name=""

        for k,v in data.items():
            if len(v)==0:continue
            risk_name = v[0][3].encode("utf-8")
            if len(k.split("-"))==2:
                #pdf_path = os.path.join(os.path.join(line_path,v[0][3]),k)
                footer_name = ".".join(v[0][4].split("-")[1:])
                footer_name += "会"+v[0][5]+"批"
            else:
                #pdf_path = os.path.join(line_path,k)
                footer_name = ""

            datas=[]
            seq=1
            for i in v:
                datas.append([seq,k,i[0].encode("utf-8"),i[1].encode("utf-8"),"男" if i[2]=="T" else "女" ])
                seq +=1
            report_lab.export_pdf(risk_name,datas,footer_name,os.path.join(pdf_path,k+"装箱单.pdf"))

    #复制发货单下面的所有拼版报告
    def report_pdf_merge(self,cr,uid,name,d,context=None):
        upload_path = os.path.join(os.path.split(__file__)[0], "static/local/upload/tjs")
        pdf_path = os.path.join(os.path.split(__file__)[0], "static/local/report")
        pdf_count=0
        source_path = os.path.join(pdf_path,name)
        if not os.path.exists(source_path):return 0

        for f in os.listdir(source_path):
            new_pdf = os.path.join(source_path,f)
            name_list = re.split("[_\.]",f) #分解文件名称

            batch_name =  self._get_batch_from_genes(cr,uid,name,name_list[2],context=context)
            target_path = os.path.join(upload_path,d)
            if not os.path.exists(target_path):
                os.mkdir(target_path)
            target_path = os.path.join(target_path,u"拼版")
            if not os.path.exists(target_path):
                os.mkdir(target_path)
            target_path = os.path.join(target_path,batch_name)
            if not os.path.exists(target_path):
                os.mkdir(target_path)

            #文件名分为六种模式
            #1. 398877432.pdf
            #2. 399834245_张三.pdf
            #3. 1-2_H_384778393.pdf
            #4. 1-4_H_394834949_王五_男.pdf
            #5. 2-5_H_494839848_2-9_H_49384345.pdf
            #6. 2-3_H_394857583_张三_2-3_H_40348934_李四_男.pdf
            if len(name_list)==4 or len(name_list)==6 or (len(name_list)==7 and name_list[0]!=name_list[3]) or (len(name_list)==10 and name_list[0]!=name_list[4]):
                #单拼
                tpath=os.path.join(target_path,u"单拼")
                if not os.path.exists(tpath):
                    os.mkdir(tpath)
                if not os.path.exists(os.path.join(tpath,f)):
                    shutil.copy(new_pdf,os.path.join(tpath,f))
                self.pool.get("rhwl.genes.picking.box.line").update_merge_flag(cr,uid,name,name_list[2],context=context)
                if len(name_list)==10:
                    self.pool.get("rhwl.genes.picking.box.line").update_merge_flag(cr,uid,name,name_list[6],context=context)
                pdf_count += 1 if len(name_list) in [4,6] else 2
            elif (len(name_list)==7 and name_list[0]==name_list[3]) or (len(name_list)==10 and name_list[0]==name_list[4]):
                tpath=os.path.join(target_path,name_list[0])
                if not os.path.exists(tpath):
                    os.mkdir(tpath)
                if not os.path.exists(os.path.join(tpath,f)):
                    shutil.copy(new_pdf,os.path.join(tpath,f))
                self.pool.get("rhwl.genes.picking.box.line").update_merge_flag(cr,uid,name,name_list[2],context=context)
                if len(name_list)==10:
                    self.pool.get("rhwl.genes.picking.box.line").update_merge_flag(cr,uid,name,name_list[6],context=context)
                pdf_count += 2
        return pdf_count

    def report_pdf_zip(self,cr,uid,name,d,context=None):
        upload_path = os.path.join(os.path.split(__file__)[0], "static/local/upload/tjs")
        target_path = os.path.join(upload_path,d)
        if not os.path.exists(target_path):
            return
        zip_path = os.path.join(target_path,u"拼版压缩")
        if not os.path.exists(zip_path):
            os.mkdir(zip_path)
        target_path = os.path.join(target_path,u"拼版")

        if not os.path.exists(target_path):
            return
        for d in os.listdir(target_path):
            d_path = os.path.join(target_path,d)
            if not os.path.isdir(d_path):continue
            zip_batch_path = os.path.join(zip_path,d)
            if not os.path.exists(zip_batch_path):
                os.mkdir(zip_batch_path)

            for b in os.listdir(d_path):
                if not os.path.isdir(os.path.join(d_path,b)):continue
                f = open(os.path.join(zip_batch_path,b+"_"+(datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime("%Y%m%d%H%M%S")+".zip"),'wb')
                openerp.tools.osutil.zip_dir(os.path.join(d_path,b), f, include_dir=False)
                f.close()

    def action_excel_upload(self,cr,uid,ids,context=None):
        self.excel_upload(cr,uid,ids,False,context=context)
        self.risk_excel(cr,uid,ids,context=context)

    #生成批次下的excel，方便印刷厂查阅
    def create_sheet_excel(self,line_path,data):
        w = xlwt.Workbook(encoding='utf-8')
        ws = w.add_sheet(os.path.split(line_path)[1])
        row=0
        batch=data.keys()
        batch1 = [i for i in batch if i.count("-")>0]
        batch2 = [i for i in batch if i.count("-")==0]
        batch1.sort(cmp=(lambda x,y: cmp([int(i) for i in x.split("-")],[int(j) for j in y.split("-")])))
        batch2.sort()
        batch = batch1 + batch2
        for k in batch:
            for i in data[k]:
                ws.write(row,0,k)
                ws.write(row,1,i[0])
                ws.write(row,2,i[1])
                ws.write(row,3,u"男" if i[2]=="T" else u"女" )
                row +=1
        w.save(os.path.join(line_path,os.path.split(line_path)[1])+".xls")

    #生成发货单Excel
    def excel_upload(self,cr,uid,ids,isvip=False,context=None):
        upload_path = os.path.join(os.path.split(__file__)[0], "static/local/upload/tjs")
        cust_path = os.path.join(upload_path,u"发货单及横版报告")
        if not os.path.exists(cust_path):
            os.mkdir(cust_path)

        obj = self.browse(cr,uid,ids,context=context)
        datastr=obj.date.replace("/","").replace("-","")
        cust_path = os.path.join(cust_path,datastr)
        if not os.path.exists(cust_path):
            os.mkdir(cust_path)

        if isvip:
            excel_path = os.path.join(upload_path,datastr+"/"+datastr+u"-发货单vip.xls")
            cust_excel_path = os.path.join(cust_path,datastr+u"-发货单vip.xls")
        else:
            excel_path = os.path.join(upload_path,datastr+"/"+datastr+u"-发货单.xls")
            cust_excel_path = os.path.join(cust_path,datastr+u"-发货单.xls")

        delete_list={}
        #shutil.copy(template,excel_path)
        #11号字
        style = xlwt.XFStyle()
        style.font = xlwt.Font()
        style.font.name=u"宋体"
        style.font.height = 220

        #11号字,水平居中,垂直居中
        style6 = xlwt.XFStyle()
        style6.font = xlwt.Font()
        style6.font.name=u"宋体"
        style6.font.height = 220
        style6.alignment = xlwt.Alignment()
        style6.alignment.horz = xlwt.Alignment.HORZ_CENTER
        style6.alignment.vert = xlwt.Alignment.VERT_CENTER

        #18号字，加边框，水平居中，垂直居中
        style1 = xlwt.XFStyle()
        style1.font = xlwt.Font()
        style1.font.name=u"宋体"
        style1.font.height = 360
        style1.alignment = xlwt.Alignment()
        style1.alignment.horz = xlwt.Alignment.HORZ_CENTER
        style1.alignment.vert = xlwt.Alignment.VERT_CENTER
        style1.borders = xlwt.Borders() # Add Borders to Style
        style1.borders.left = xlwt.Borders.MEDIUM # May be: NO_LINE, THIN, MEDIUM, DASHED, DOTTED, THICK, DOUBLE, HAIR, MEDIUM_DASHED, THIN_DASH_DOTTED, MEDIUM_DASH_DOTTED, THIN_DASH_DOT_DOTTED, MEDIUM_DASH_DOT_DOTTED, SLANTED_MEDIUM_DASH_DOTTED, or 0x00 through 0x0D.
        style1.borders.right = xlwt.Borders.MEDIUM
        style1.borders.top = xlwt.Borders.MEDIUM
        style1.borders.bottom = xlwt.Borders.MEDIUM
        style1.borders.left_colour = 0x40
        style1.borders.right_colour = 0x40
        style1.borders.top_colour = 0x40
        style1.borders.bottom_colour = 0x40

        #18号字，加边框，水平靠右，垂直居中
        style2 = xlwt.XFStyle()
        style2.font = xlwt.Font()
        style2.font.name=u"宋体"
        style2.font.height = 360
        style2.alignment = xlwt.Alignment()
        style2.alignment.horz = xlwt.Alignment.HORZ_RIGHT
        style2.alignment.vert = xlwt.Alignment.VERT_CENTER
        style2.borders = xlwt.Borders() # Add Borders to Style
        style2.borders.left = xlwt.Borders.MEDIUM # May be: NO_LINE, THIN, MEDIUM, DASHED, DOTTED, THICK, DOUBLE, HAIR, MEDIUM_DASHED, THIN_DASH_DOTTED, MEDIUM_DASH_DOTTED, THIN_DASH_DOT_DOTTED, MEDIUM_DASH_DOT_DOTTED, SLANTED_MEDIUM_DASH_DOTTED, or 0x00 through 0x0D.
        style2.borders.right = xlwt.Borders.MEDIUM
        style2.borders.top = xlwt.Borders.MEDIUM
        style2.borders.bottom = xlwt.Borders.MEDIUM
        style2.borders.left_colour = 0x40
        style2.borders.right_colour = 0x40
        style2.borders.top_colour = 0x40
        style2.borders.bottom_colour = 0x40

        #11号字，加边框，水平居中，重直居中
        style3 = xlwt.XFStyle() # Create Style
        style3.alignment = xlwt.Alignment()
        style3.font.name=u"宋体"
        style3.alignment.horz = xlwt.Alignment.HORZ_CENTER
        style3.alignment.vert = xlwt.Alignment.VERT_CENTER
        style3.borders = xlwt.Borders() # Add Borders to Style
        style3.borders.left = xlwt.Borders.MEDIUM # May be: NO_LINE, THIN, MEDIUM, DASHED, DOTTED, THICK, DOUBLE, HAIR, MEDIUM_DASHED, THIN_DASH_DOTTED, MEDIUM_DASH_DOTTED, THIN_DASH_DOT_DOTTED, MEDIUM_DASH_DOT_DOTTED, SLANTED_MEDIUM_DASH_DOTTED, or 0x00 through 0x0D.
        style3.borders.right = xlwt.Borders.MEDIUM
        style3.borders.top = xlwt.Borders.MEDIUM
        style3.borders.bottom = xlwt.Borders.MEDIUM
        style3.borders.left_colour = 0x40
        style3.borders.right_colour = 0x40
        style3.borders.top_colour = 0x40
        style3.borders.bottom_colour = 0x40
        style3.font = xlwt.Font()
        style3.font.height = 220

        #11号字，加边框，水平靠左，重直居中
        style4 = xlwt.XFStyle() # Create Style
        style4.borders = xlwt.Borders() # Add Borders to Style
        style4.borders.left = xlwt.Borders.MEDIUM # May be: NO_LINE, THIN, MEDIUM, DASHED, DOTTED, THICK, DOUBLE, HAIR, MEDIUM_DASHED, THIN_DASH_DOTTED, MEDIUM_DASH_DOTTED, THIN_DASH_DOT_DOTTED, MEDIUM_DASH_DOT_DOTTED, SLANTED_MEDIUM_DASH_DOTTED, or 0x00 through 0x0D.
        style4.borders.right = xlwt.Borders.MEDIUM
        style4.borders.top = xlwt.Borders.MEDIUM
        style4.borders.bottom = xlwt.Borders.MEDIUM
        style4.borders.left_colour = 0x40
        style4.borders.right_colour = 0x40
        style4.borders.top_colour = 0x40
        style4.borders.bottom_colour = 0x40
        style4.font = xlwt.Font()
        style4.font.height = 220
        style4.font.name=u"宋体"
        style4.alignment = xlwt.Alignment()
        style4.alignment.horz = xlwt.Alignment.HORZ_LEFT
        style4.alignment.vert = xlwt.Alignment.VERT_CENTER

        #11号字，加边框，水平靠右，垂直居中
        style5 = xlwt.XFStyle()
        style5.font = xlwt.Font()
        style5.font.height = 220
        style5.font.name=u"宋体"
        style5.alignment = xlwt.Alignment()
        style5.alignment.horz = xlwt.Alignment.HORZ_RIGHT
        style5.alignment.vert = xlwt.Alignment.VERT_CENTER
        style5.borders = xlwt.Borders() # Add Borders to Style
        style5.borders.left = xlwt.Borders.MEDIUM # May be: NO_LINE, THIN, MEDIUM, DASHED, DOTTED, THICK, DOUBLE, HAIR, MEDIUM_DASHED, THIN_DASH_DOTTED, MEDIUM_DASH_DOTTED, THIN_DASH_DOT_DOTTED, MEDIUM_DASH_DOT_DOTTED, SLANTED_MEDIUM_DASH_DOTTED, or 0x00 through 0x0D.
        style5.borders.right = xlwt.Borders.MEDIUM
        style5.borders.top = xlwt.Borders.MEDIUM
        style5.borders.bottom = xlwt.Borders.MEDIUM
        style5.borders.left_colour = 0x40
        style5.borders.right_colour = 0x40
        style5.borders.top_colour = 0x40
        style5.borders.bottom_colour = 0x40

        w = xlwt.Workbook(encoding='utf-8')
        ws = w.add_sheet(u'发货单')
        ws.col(0).width = 1380
        ws.col(1).width = 2727
        ws.col(2).width = 2888
        ws.col(3).width = 2692
        ws.col(4).width = 3399
        ws.col(5).width = 2692
        ws.col(6).width = 4950 #1000 = 3.715(Excel)
        ws.col(7).width = 2692
        ws.col(8).width = 4950 #1000 = 3.715(Excel)
        ws.col(9).width = 6554
        ws.row(7).height_mismatch = True
        ws.row(7).height = 500
        ws.row(8).height_mismatch = True
        ws.row(8).height = 500
        ws.row(9).height_mismatch = True
        ws.row(9).height = 500
        ws.write_merge(0,0, 0, 1, u'收件单位：',style)
        ws.write_merge(1,1,0,1,u"收件人：",style)
        ws.write_merge(2,2,0,1,u"联系电话：",style)
        ws.write_merge(3,3,0,1,u"地址：",style)
        if isvip:
            ws.write_merge(0,0, 2, 4,u'天狮集团泰济生健康事业部会员管理处',style)
            ws.write_merge(1,1,2,4,u"孙媛",style)
            ws.write_merge(2,2,2,4,u"022-8213-6607",style)
            ws.write_merge(3,3,2,4,u"天津市武清开发区新源道18号天狮国际健康产业园泰济生医院",style)
        else:
            ws.write_merge(0,0, 2, 4,u'天狮集团泰济生国际医院会员管理处',style)
            ws.write_merge(1,1,2,4,u"韩磊",style)
            ws.write_merge(2,2,2,4,u"15002230510",style)
            ws.write_merge(3,3,2,4,u"天津市武清开发区新源道18号",style)

        ws.write(0,7,u"寄件单位：",style)
        ws.write_merge(0,0, 8, 9, u"人和未来生物科技（长沙）有限公司",style)
        ws.write(1,7,u"寄件人：",style)
        ws.write_merge(1,1, 8, 9, u"李慧平",style)
        ws.write(2,7,u"联系电话：",style)
        ws.write_merge(2,2, 8, 9, u"18520590515",style)
        ws.write(3,7,u"地址：",style)
        ws.write_merge(3,3, 8, 9, u"湖南长沙市开福区太阳山路青竹湖镇湖心岛2栋",style)

        ws.write_merge(6,6,0,7,u"易感检测报告书送货清单",style1)
        ws.write_merge(6,6,8,9,u"NO."+obj.name,style2)

        ws.write_merge(7,7,0,5,u"客户名称：泰济生国际医院（韩磊）",style4)
        ws.write_merge(7,7,6,9,u"日期：  "+obj.date,style5)
        ws.write_merge(8,9,0,0,u"序号",style3)
        ws.write_merge(8,9,1,1,u"货品名称",style3)
        ws.write_merge(8,9,2,2,u"批号",style3)
        ws.write_merge(8,9,3,3,u"箱数",style3)
        ws.write_merge(8,9,4,4,u"数量（本）",style3)
        ws.write_merge(8,8,5,6,u"装箱-高风险",style3)
        ws.write(9,5,u"箱数",style3)
        ws.write(9,6,u"箱号",style3)
        ws.write_merge(8,8,7,8,u"装箱-低风险",style3)
        ws.write(9,7,u"箱数",style3)
        ws.write(9,8,u"箱号",style3)
        ws.write_merge(8,9,9,9,u"备注",style3)
        excel_row = 10
        total_box = 0
        total_qty = 0
        for l in obj.line:
            if (isvip and l.batch_kind!="vip") or (isvip==False and l.batch_kind=="vip"):
                continue
            ws.write(excel_row,0,l.seq,style3)
            ws.write(excel_row,1,l.product_name,style3)


            if l.batch_kind=="normal":
                gene_id = self.pool.get("rhwl.easy.genes").search(cr,uid,[("batch_no","=",l.batch_no),("cust_prop","=","tjs")])
                gene_obj=self.pool.get("rhwl.easy.genes").browse(cr,uid,gene_id[0],context=context)
                ws.write(excel_row,2,u".".join(gene_obj.date.split("-")[1:])+u"会",style3)
            elif l.batch_kind=="resend":
                ws.write(excel_row,2,l.batch_no,style3)
            else:
                ws.write(excel_row,2,l.batch_no,style3)
            ws.write(excel_row,3,l.box_qty,style3)
            ws.write(excel_row,4,l.qty,style3)
            total_box += l.box_qty
            total_qty += l.qty
            if l.batch_kind=="normal":
                ws.write(excel_row,5,l.box_h_qty,style3)
            else:
                ws.write(excel_row,5,"",style3)
            if l.box_h_qty>0 and l.batch_kind=="normal":
                ws.write(excel_row,6,u"【"+str(l.seq)+u"-1】至【"+str(l.seq)+u"-"+str(l.box_h_qty)+u"】",style3)
            else:
                ws.write(excel_row,6,"",style3)
            if l.batch_kind=="normal":
                ws.write(excel_row,7,l.box_l_qty,style3)
            else:
                ws.write(excel_row,7,"",style3)
            if l.box_l_qty>0 and l.batch_kind=="normal":
                ws.write(excel_row,8,u"【"+str(l.seq)+u"-"+str(l.box_h_qty+1)+u"】至【"+str(l.seq)+u"-"+str(l.box_qty)+u"】",style3)
            else:
                ws.write(excel_row,8,"",style3)
            ws.write(excel_row,9,"",style3)
            ws.row(excel_row).height_mismatch = True
            ws.row(excel_row).height = 500
            excel_row += 1
            #处理批号明细
            if l.batch_kind=="normal":
               w1 = w.add_sheet(u".".join(gene_obj.date.split("-")[1:])+u"会"+l.batch_no+u"批",cell_overwrite_ok=True)
            elif l.batch_kind=="resend":
               w1 = w.add_sheet(l.batch_no,cell_overwrite_ok=True)
            else:
               w1 = w.add_sheet(l.batch_no,cell_overwrite_ok=True)
            sheet_count=1
            #w1 = w.add_sheet(gene_obj.date)
            w1.col(0).width = 2960
            w1.col(1).width = 3160
            w1.col(2).width = 2960
            w1.col(3).width = 2960
            w1.col(4).width = 5800

            w1.write(0,0,u"箱号",style6)
            w1.write(0,1,u"基因编码",style6)
            w1.write(0,2,u"姓名",style)
            w1.write(0,3,u"性别",style6)
            w1.write(0,4,u"身份证号码",style)
            if l.batch_kind=="resend":
                w1.write(0,5,u"重印说明",style)
                w1.col(5).width = 5560
                w1.write(0,6,u"病症数量",style6)
                w1.write(0,7,u"病症名称",style)
                w1.col(6).width = 2960
                w1.col(7).width = 9000
            else:
                w1.write(0,5,u"病症数量",style6)
                w1.write(0,6,u"病症名称",style)
                w1.col(5).width = 2960
                w1.col(6).width = 9000
            sheet_row=1
            for b in l.box_line:
                for bl in b.detail:
                    if l.batch_kind=="vip":
                        w1.write(sheet_row,0,"V"+b.name,style6)
                    elif l.batch_kind=="resend":
                        w1.write(sheet_row,0,"R"+b.name,style6)
                    else:
                        w1.write(sheet_row,0,str(l.seq)+"-"+b.name,style6)
                    w1.write(sheet_row,1,bl.genes_id.name,style6)
                    w1.write(sheet_row,2,bl.genes_id.cust_name,style)
                    w1.write(sheet_row,3,u"女" if bl.genes_id.sex=="F" else u"男",style6)
                    w1.write(sheet_row,4,bl.genes_id.identity,style)
                    if l.batch_kind=="resend":
                        w1.write(sheet_row,5,l.note,style)
                        w1.write(sheet_row,6,str(bl.genes_id.risk_count)+(u"(儿童)" if bl.genes_id.is_child else u""),style6)
                        w1.write(sheet_row,7,bl.genes_id.risk_text,style)
                    else:
                        w1.write(sheet_row,5,str(bl.genes_id.risk_count)+(u"(儿童)" if bl.genes_id.is_child else u""),style6)
                        w1.write(sheet_row,6,bl.genes_id.risk_text,style)
                    sheet_row += 1
                    sheet_count +=1

            if l.batch_kind=="normal":
                line_ids = self.pool.get("rhwl.genes.picking.line").search(cr,uid,[("picking_id","=",l.picking_id.id),("batch_kind","=","vip")],context=context)
                for ll in self.pool.get("rhwl.genes.picking.line").browse(cr,uid,line_ids,context=context):
                    for vip_b in ll.box_line:
                        for vip_bl in vip_b.detail:
                            if vip_bl.genes_id.batch_no==l.batch_no:
                                w1.write(sheet_row,0,"V"+vip_b.name,style6)
                                w1.write(sheet_row,1,vip_bl.genes_id.name,style6)
                                w1.write(sheet_row,2,vip_bl.genes_id.cust_name,style)
                                w1.write(sheet_row,3,u"女" if vip_bl.genes_id.sex=="F" else u"男",style6)
                                w1.write(sheet_row,4,vip_bl.genes_id.identity,style)
                                w1.write(sheet_row,5,str(vip_bl.genes_id.risk_count)+(u"(儿童)" if vip_bl.genes_id.is_child else u""),style6)
                                w1.write(sheet_row,6,vip_bl.genes_id.risk_text,style)
                                sheet_row += 1
                                sheet_count +=1
            delete_list[w1.name] = [sheet_count,0]


            #统计质检不合格数据
            vip_batchno=[]

            if isvip:
                vip_ids = self.pool.get("rhwl.genes.picking.line").search(cr,uid,[("picking_id","=",l.picking_id.id),("batch_kind","=","normal")])
                for ii in self.pool.get("rhwl.genes.picking.line").browse(cr,uid,vip_ids):
                    vip_batchno.append(ii.batch_no)
                gene_id = self.pool.get("rhwl.easy.genes").search(cr,uid,[("batch_no","in",vip_batchno),("cust_prop","=","tjs_vip"),("state","=","dna_except")])
            else:
                vip_batchno.append(l.batch_no)
                gene_id = self.pool.get("rhwl.easy.genes").search(cr,uid,[("batch_no","in",vip_batchno),("cust_prop","in",["tjs","tjs_vip"]),("state","=","dna_except")])

            if gene_id:
                if isvip:
                    gene_all_id = self.pool.get("rhwl.easy.genes").search(cr,uid,[("batch_no","in",vip_batchno),("cust_prop","=","tjs_vip")])
                else:
                    gene_all_id = self.pool.get("rhwl.easy.genes").search(cr,uid,[("batch_no","in",vip_batchno),("cust_prop","in",["tjs","tjs_vip"])])
                sheet_row += 1
                w1.write_merge(sheet_row,sheet_row,0,4,u"实收"+str(len(gene_all_id))+u"个，无编号未确认，质检不合格"+str(len(gene_id))+u"个，实发"+str(len(gene_all_id)-len(gene_id))+u"本",style)
                sheet_row += 1
                for s in self.pool.get("rhwl.easy.genes").browse(cr,uid,gene_id,context=context):
                    w1.write(sheet_row,0,u"质检不合格",style)
                    w1.write(sheet_row,1,s.name,style6)
                    w1.write(sheet_row,2,s.cust_name,style)
                    w1.write(sheet_row,3,u"女" if s.sex=="F" else u"男",style6)
                    w1.write(sheet_row,4,s.identity,style)
                    sheet_row += 1
                    delete_list[w1.name][1] = delete_list[w1.name][1]+1



        ws.row(excel_row).height_mismatch = True
        ws.row(excel_row).height = 500
        ws.row(excel_row+1).height_mismatch = True
        ws.row(excel_row+1).height = 500
        ws.write_merge(excel_row,excel_row,0,2,u"合计件数",style3)
        ws.write(excel_row,3,total_box,style3)
        ws.write(excel_row,4,total_qty,style3)
        ws.write_merge(excel_row,excel_row,5,9,"",style3)
        ws.write_merge(excel_row+1,excel_row+1,0,4,u"收货人签字：",style4)
        ws.write_merge(excel_row+1,excel_row+1,5,9,u"收货日期：",style4)

        w.save(cust_excel_path)

        for s in w._Workbook__worksheets:
            if not delete_list.get(s.name):continue
            for r in range(1,delete_list.get(s.name)[0]+1):
                s.write(r-1,4,"")
                s.write(r-1,5,"")
                s.write(r-1,6,"")
                s.write(r-1,7,"")
            for r in range(delete_list.get(s.name)[0]+3,delete_list.get(s.name)[0]+3+delete_list.get(s.name)[1]+1):
                s.write(r-1,4,"")
                s.write(r-1,5,"")
                s.write(r-1,6,"")
                s.write(r-1,7,"")
        w.save(excel_path)

        if not isvip:
            self.excel_upload(cr,uid,ids,True,context=context)

    def risk_excel_header(self,cr,uid,context=None):
        hd={
            0:[u"人员信息",[u"姓名",u"性别",u"出生日期",u"身份证号",u"体检编号",u"基因编码"]]
        }
        k=1
        ids = self.pool.get("rhwl.gene.disease.type").search(cr,uid,[],order="name",context=context)
        for i in self.pool.get("rhwl.gene.disease.type").browse(cr,uid,ids,context=context):
            hd[k]=[i.name,[]]
            for j in i.line:
                hd[k][1].append(j.name)
            k+=1
        return hd

    #创建发货单的横板excel表
    def risk_excel(self,cr,uid,id,context=None):
        upload_path = os.path.join(os.path.split(__file__)[0], "static/local/upload/tjs")
        cust_path = os.path.join(upload_path,u"发货单及横版报告")
        obj = self.browse(cr,uid,id,context=context)
        d=obj.date.replace("/","").replace("-","") #发货单需创建的目录名称
        d_path=os.path.join(cust_path,d)
        w = xlwt.Workbook(encoding='utf-8')
        ws1 = w.add_sheet(u'总表')
        ws2 = w.add_sheet(u'儿童筛选')
        ws3 = w.add_sheet(u'高值筛选')
        ws1_row=2
        ws2_row=2
        ws1_col=0
        ws2_col=0
        #写表头内容
        for s in [ws1,ws2]:
            for n in range(1,71):
                s.write(0,n+5,n)
        hd = self.risk_excel_header(cr,uid,context=context)
        hd_keys = hd.keys()
        hd_keys.sort()
        for k in hd_keys:
            col_temp = ws1_col
            for v in hd[k][1]:
                ws1.write(ws1_row,ws1_col,v)
                ws2.write(ws2_row,ws2_col,v)
                ws1_col+=1
                ws2_col+=1
            ws1.write_merge(ws1_row-1,ws1_row-1,col_temp,ws1_col-1,hd[k][0])
            ws2.write_merge(ws1_row-1,ws1_row-1,col_temp,ws1_col-1,hd[k][0])
        ws3.write_merge(1,1,0,5,hd[0][0])
        ws3_col=0
        for i in hd[0][1]:
            ws3.write(2,ws3_col,i)
            ws3_col+=1
        ws3.write(2,ws3_col,u"病症数量")
        ws3.write(2,ws3_col+1,u"病症名称")

        #统计需要转出的样本数据
        gene_ids=[]
        for i in obj.line:
            if i.batch_kind=="resend":continue
            for b in i.box_line:
                for bl in b.detail:
                    gene_ids.append(bl.genes_id.id)
        ws1_row = 3
        ws2_row = 3

        cols=["cust_name","sex","birthday","identity","name","batch_no","A1","A2","A3","A4","A5","A6","A7","A8","A9","A10","A11","A12","A13","A14","A15","A16","A17","A18","A19","A20","A21","A22","A23","B1","B2","B3","B4","B5","B6","B7","B8","B9","B10","B11","B12","B13","B14","B15","B16","C1","C2","C3","C4","C5","C6","C7","C8","C9","C10","C11","C12","D1","D2","D3","D4","D5","D6","D7","D8","D9","D10","D11","D12","D13","D14","E1","E2","E3","F1","F2"]
        for i in self.pool.get("rhwl.easy.genes").browse(cr,uid,gene_ids,context=context):
            ws1_col = 0
            ws2_col = 0
            for c in cols:
                if c=="sex":
                    ws1.write(ws1_row,ws1_col,u"男" if i[c]==u"T" else u"女")
                elif c=="batch_no":
                    ws1.write(ws1_row,ws1_col,i.batch_no+"-"+i.name)
                else:
                    ws1.write(ws1_row,ws1_col,i[c] if i[c] else "")
                ws1_col +=1
            ws1_col=0
            for c in cols[0:6]+["risk_count","risk_text"]:
                if c=="sex":
                    ws3.write(ws1_row,ws1_col,u"男" if i[c]==u"T" else u"女")
                elif c=="batch_no":
                    ws3.write(ws1_row,ws1_col,i.batch_no+"-"+i.name)
                elif c=="risk_count":
                    ws3.write(ws1_row,ws1_col,str(i.risk_count)+(u"(儿童)" if i.is_child else ""))
                else:
                    ws3.write(ws1_row,ws1_col,i[c] if i[c] else "")
                ws1_col +=1

            ws1_row += 1

            if i.is_child:
               for c in cols:
                    if c=="sex":
                        ws2.write(ws2_row,ws2_col,u"男" if i[c]==u"T" else u"女")
                    elif c=="batch_no":
                        ws2.write(ws2_row,ws2_col,i.batch_no+"-"+i.name)
                    else:
                        ws2.write(ws2_row,ws2_col,i[c]  if i[c] else "")
                    ws2_col +=1
               ws2_row += 1

        w.save(os.path.join(d_path,d+u"-横版报告.xls"))

    #明细批次分配箱号
    def create_box(self,cr,uid,context=None):
        ids = self.search(cr,uid,[("state","=","draft")])
        if not ids:return
        for i in self.browse(cr,uid,ids,context=context):
            for l in i.line:
                if not l.box_line:
                    self.pool.get("rhwl.genes.picking.line").create_box(cr,uid,l.id,context=context)

    def _list_split(self,list1,list2):
        l1_yu=""
        l2_yu=""
        if len(list1)%2==0:
            l1=list1
        else:
            l1=list1[:-1]
            l1_yu=list1[-1]

        if len(list2)%2==0:
            l2=list2
        else:
            l2=list2[:-1]
            l2_yu=list2[-1]

        l1_split=[[x,l1[l1.index(x)+1]] for x in l1 if l1.index(x)%2==0]
        l2_split=[[x,l2[l2.index(x)+1]] for x in l2 if l2.index(x)%2==0]
        l=l1_split+l2_split
        if l1_yu or l2_yu:
            l = l+[[l1_yu,l2_yu]]
        return l

    #导出已经分配好箱号的样本给报告生成服务器
    def export_box_genes(self,cr,uid,context=None):
        ids = self.search(cr,uid,[("state","=","draft"),("is_merge","=",True)])

        if not ids:return
        for i in ids:
            self.export_box(cr,uid,i,context=context)

    def export_box(self,cr,uid,ids,context=None):
        genes_ids=[] #记录导出的样本
        l_ids=[] #记录已经导出的批次明细
        genes_box={} #记录每个样本的箱号、风险值
        #取所有符合条件的发货单
        pdf_seq_count=0
        pick_obj = self.browse(cr,uid,ids,context=context)
        #hardcode=['2799995306','2799996362','3299999811','3499990556','2799996076','3299995577','3399992519','3399993441','3399996552','3399999137','3499991386']
        for l in pick_obj.line:
            if l.export:continue

            if not l.box_line:continue
            pdf_seq=[[[],[]],[[],[]]] #接版计算用，第一层分男女，第二层分高低风险
            l_ids.append(l.id)
            for b in l.box_line:
                for dl in b.detail:
                    #if hardcode.count(dl.genes_id.name.encode("utf-8"))==0:continue
                    genes_ids.append(dl.genes_id.id)
                    if l.batch_kind=="normal":
                        genes_box[dl.genes_id.name.encode("utf-8")]=[str(l.seq)+"-"+b.name.encode("utf-8"),b.level.encode("utf-8"),dl.genes_id.snp_name.encode("utf-8")]
                    elif l.batch_kind=="vip":
                        genes_box[dl.genes_id.name.encode("utf-8")]=["V"+b.name.encode("utf-8"),b.level.encode("utf-8"),dl.genes_id.snp_name.encode("utf-8")]
                    elif l.batch_kind=="resend":
                        genes_box[dl.genes_id.name.encode("utf-8")]=["R"+b.name.encode("utf-8"),b.level.encode("utf-8"),dl.genes_id.snp_name.encode("utf-8")]

                    #接版
                    idx1=0
                    idx2=0
                    if dl.genes_id.sex=="T":
                        idx1=0
                    else:
                        idx1=1
                    if l.batch_kind=="normal" and b.level=="L":
                        idx2=1
                    else:
                        idx2=0
                    pdf_seq[idx1][idx2].append(dl.genes_id.name.encode("utf-8"))

            #计算每批次的拼版
            for p1 in pdf_seq:
                p_res=self._list_split(p1[0],p1[1])

                for p2 in p_res:
                    pdf_seq_count += 1
                    if p2[0]:
                        genes_box[p2[0]].append(str(pdf_seq_count))
                    if p2[1]:
                        genes_box[p2[1]].append(str(pdf_seq_count))



        data=self.pool.get("rhwl.easy.genes").get_gene_type_list(cr,uid,genes_ids,context=context)
        if not data:return

        fpath = os.path.join(os.path.split(__file__)[0], "static/remote/snp")
        fname = os.path.join(fpath, "box_" + pick_obj.name.encode("utf-8")+"_"+datetime.datetime.now().strftime("%m%d%H%M%S") + ".txt")
        header=[]
        f = open(fname, "w+")
        for s in ["F","M"]:
            if not data.has_key(s):continue
            data_list =data[s].keys()
            data_list.sort()
            for k in data_list:
                line_row=[genes_box[data[s][k]["name"]][0],genes_box[data[s][k]["name"]][1],genes_box[data[s][k]["name"]][3],genes_box[data[s][k]["name"]][2],data[s][k]["name"],data[s][k]["cust_name"],s]
                if not header:
                    header = data[s][k].keys()
                    header.remove("name")
                    header.remove("cust_name")
                    header.sort()
                    f.write("箱号\t风险\t拼版\t批次\t编号\t姓名\t性别\t" + "\t".join(header) + '\n')
                for i in header:
                    line_row.append(data[s][k][i])
                f.write("\t".join(line_row) + '\n')
        f.close()
        if l_ids:
            self.pool.get("rhwl.genes.picking.line").write(cr,uid,l_ids,{"export":True},context=context)

#发货单批次明细对象
class rhwl_picking_line(osv.osv):
    _name = "rhwl.genes.picking.line"

    def _get_box_qty(self,cr,uid,ids,field_names,arg,context=None):
        res=dict.fromkeys(ids,0)
        for k in res.keys():
            id=self.pool.get("rhwl.genes.picking.box").search(cr,uid,[("line_id","=",k)])
            res[k] = len(id)
        return res

    def _get_box_qty_h(self,cr,uid,ids,field_names,arg,context=None):
        res=dict.fromkeys(ids,0)
        for k in res.keys():
            id=self.pool.get("rhwl.genes.picking.box").search(cr,uid,[("line_id","=",k),("level","=","H")])
            res[k] = len(id)
        return res

    def _get_box_qty_l(self,cr,uid,ids,field_names,arg,context=None):
        res=dict.fromkeys(ids,0)
        for k in res.keys():
            id=self.pool.get("rhwl.genes.picking.box").search(cr,uid,[("line_id","=",k),("level","=","L")])
            res[k] = len(id)
        return res

    def _get_detail_qty(self,cr,uid,ids,field_names,arg,context=None):
        res=dict.fromkeys(ids,0)
        for k in res.keys():
            res[k] = self.pool.get("rhwl.genes.picking.box.line").search_count(cr,uid,[("box_id.line_id.id","=",k)])
        return res

    def _get_detail_qty_pdf(self,cr,uid,ids,field_names,arg,context=None):
        res={}
        for i in ids:
            res[i] = {}.fromkeys(field_names,0)
            res[i]["qty_pdf"] = self.pool.get("rhwl.genes.picking.box.line").search_count(cr,uid,[("box_id.line_id.id","=",i),("has_pdf","=",True)])
            res[i]["qty_merge"] = self.pool.get("rhwl.genes.picking.box.line").search_count(cr,uid,[("box_id.line_id.id","=",i),("has_merge","=",True)])

        return res

    _order = "seq"
    _columns={
        "picking_id":fields.many2one("rhwl.genes.picking",u"发货单号",ondelete="restrict"),
        "seq":fields.integer(u"序号",required=True),
        "product_name":fields.char(u"货品名称",size=20),
        "batch_no":fields.char(u"批号",size=15,required=True),
        "batch_kind":fields.selection([("normal",u"普通"),("vip",u"VIP客户"),("resend",u"破损重印")],u"类型"),
        "box_qty":fields.function(_get_box_qty,type="integer",string=u"箱数"),
        "box_h_qty":fields.function(_get_box_qty_h,type="integer",string=u"高风险箱数"),
        "box_l_qty":fields.function(_get_box_qty_l,type="integer",string=u"低风险箱数"),
        "qty":fields.function(_get_detail_qty,type="integer",string=u"数量"),
        "qty_pdf":fields.function(_get_detail_qty_pdf,type="integer",string=u"已接收单本数量",multi="get_qty_pdf"),
        "qty_merge":fields.function(_get_detail_qty_pdf,type="integer",string=u"已接收拼版数量",multi="get_qty_pdf"),
        "note":fields.char(u"备注",size=200),
        "box_line":fields.one2many("rhwl.genes.picking.box","line_id","Detail"),
        "export":fields.boolean("Export"),
    }
    _defaults={
        "product_name":u"检测报告",
        "batch_kind":"normal",
        "export":False,
    }
    _sql_constraints = [
        ('rhwl_genes_picking_seq_uniq', 'unique(picking_id,seq)', u'发货明细序号不能重复!'),
    ]

    @api.onchange("batch_kind")
    def _onchange_batch_kind(self):
        if self.batch_kind=="resend":
            self.batch_no="破损重印"
        elif self.batch_kind=="vip":
            self.batch_no="VIP客户"
        else:
            self.batch_no=""

    def create(self,cr,uid,val,context=None):
        if val.get("seq",0)<=0:
            raise osv.except_osv(u'错误',u'发货明细的序号必须大于0')
        if val.get("batch_kind")=="normal":
            ids=self.pool.get("rhwl.easy.genes").search(cr,uid,[("batch_no","=",val.get("batch_no"))],context=context)
            if not ids:
                raise osv.except_osv(u"错误",u"批次号不存在，请输入正确的批次号码。")
        if val["batch_kind"] != "resend":
            if val.get("note"):
                val["note"] = val.get("note"," ")+u"【该批次未出完报告，不能分配箱号。】"
            else:
                val["note"] = u"【该批次未出完报告，不能分配箱号。】"

        line_id = super(rhwl_picking_line,self).create(cr,uid,val,context=context)
        self.create_box(cr,uid,line_id,context=context)
        return line_id

    def create_box(self,cr,uid,id,context=None):
        obj=self.browse(cr,uid,id,context=context)
        batchno=[]
        cust_prop=""
        if obj.batch_kind == "normal":
            batchno.append(obj.batch_no)
            cust_prop="tjs"
        elif obj.batch_kind == "vip":
            pid=self.search(cr,uid,[("picking_id","=",obj.picking_id.id),("batch_kind","=","normal")],context=context)
            for d in self.browse(cr,uid,pid,context=context):
                batchno.append(d.batch_no)
            cust_prop="tjs_vip"
        else:
            return
        #如果指定批次下，除去已取消、质检不合格的，如果还有样本没有风险报告，则不分配箱号
        pids = self.pool.get("rhwl.easy.genes").search(cr,uid,[("batch_no","in",batchno),("state","not in",["cancel","dna_except"]),("risk","=",False)])
        if pids:return

        box_no="0"
        ids1=self.pool.get("rhwl.easy.genes").search(cr,uid,[("batch_no","in",batchno),
                                                                ("state","not in",["cancel","dna_except"]),
                                                                ("cust_prop","=",cust_prop),
                                                                ("is_risk","=",True),
                                                                ("is_child","=",False)],order="sex,name")
        ids2=self.pool.get("rhwl.easy.genes").search(cr,uid,[("batch_no","in",batchno),
                                                                ("state","not in",["cancel","dna_except"]),
                                                                ("cust_prop","=",cust_prop),
                                                                #("is_risk","=",True),
                                                                ("is_child","=",True)],order="sex,name")
        ids3=self.pool.get("rhwl.easy.genes").search(cr,uid,[("batch_no","in",batchno),
                                                                ("state","not in",["cancel","dna_except"]),
                                                                ("cust_prop","=",cust_prop),
                                                                ("is_child","=",False),
                                                                ("is_risk","=",False)],order="sex,name")
        if cust_prop=="tjs":
            all_ids = [[ids1,'H'],[ids2,'L'],[ids3,'L']]
        else:
            all_ids = [[ids1+ids2+ids3,'L']]
        for gid in all_ids:
            ids=gid[0]
            while len(ids)>13:
                box_no=str(int(box_no)+1)
                self._insert_box(cr,uid,id,box_no,gid[1],ids[0:13])
                ids=ids[13:]
            else:
                if len(ids)>0:
                    box_no=str(int(box_no)+1)
                    self._insert_box(cr,uid,id,box_no,gid[1],ids)
        self.write(cr,uid,id,{"note":obj.note.split(u"【")[0]},context=context)

    def _insert_box(self,cr,uid,id,box,level,val):
        values=[]
        for i in val:
            values.append([0,0,{"genes_id":i}])
        return self.pool.get("rhwl.genes.picking.box").create(cr,uid,{"line_id":id,"name":box,"level":level,"detail":values})

#发货批次的箱号明细
class rhwl_picking_box(osv.osv):
    _name="rhwl.genes.picking.box"

    def _get_qty(self,cr,uid,ids,field_names,arg,context=None):
        res={}
        for id in ids:
            res[id] = {}.fromkeys(field_names,0)
            obj = self.pool.get("rhwl.genes.picking.box.line")
            res[id]["qty"] = obj.search_count(cr,uid,[("box_id","=",id)],context=context)
            res[id]["qty_pdf"] = obj.search_count(cr,uid,[("box_id","=",id),("has_pdf","=",True)],context=context)
            res[id]["qty_merge"] = obj.search_count(cr,uid,[("box_id","=",id),("has_merge","=",True)],context=context)
        return res

    _columns={
        "line_id":fields.many2one("rhwl.genes.picking.line",u"发货明细",ondelete="cascade"),
        "name":fields.char(u"箱号",size=5,required=True),
        "level":fields.selection([("H",u"高风险"),("L",u"低风险")],u"风险值"),
        "qty":fields.function(_get_qty,type="integer",string=u"样本数量",multi="get_qty"),
        "qty_pdf":fields.function(_get_qty,type="integer",string=u"已接收单本数量",multi="get_qty"),
        "qty_merge":fields.function(_get_qty,type="integer",string=u"已接收拼版数量",multi="get_qty"),
        "detail":fields.one2many("rhwl.genes.picking.box.line","box_id","Detail")
    }
    _sql_constraints = [
        ('rhwl_genes_picking_box_name_uniq', 'unique(line_id,name)', u'发货明细箱号不能重复!'),
    ]

#发货单每箱样本明细
class rhwl_picking_box_line(osv.osv):
    _name="rhwl.genes.picking.box.line"
    _columns={
        "box_id":fields.many2one("rhwl.genes.picking.box",u"箱号",ondelete="cascade"),
        "genes_id":fields.many2one("rhwl.easy.genes",u"基因样本编号",ondelete="restrict",required=True),
        "name":fields.related("genes_id","cust_name",type="char",string=u"会员姓名"),
        "has_pdf":fields.boolean("Has PDF"),
        "has_merge":fields.boolean("Has Merge")
    }

    _defauts={
        "has_pdf":False,
        "has_merge":False
    }

    def update_merge_flag(self,cr,uid,picking,name,context=None):
        id = self.search(cr,uid,[("box_id.line_id.picking_id.name","=",picking),("genes_id.name","=",name)])
        if id:
            self.write(cr,uid,id,{"has_merge":True},context=context)
