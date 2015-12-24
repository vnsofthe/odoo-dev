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
import rhwl_excel_constant as ec
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
                for k in i.detail:
                   genes_id.append(k.genes_id.id)
            self.pool.get("rhwl.easy.genes.new").write(cr,uid,genes_id,{"state":stat[val["state"]]},context=context)
        return id

    def pdf_copy(self,cr,uid,pdf_path,d_path,tname,files):
        u_count = 0
        t_count = 0

        for k,v in files.items():
            for k2,v2 in v.items():
                for k1,v1 in v2.items():
                    t_count += len(v1)
                    for i in v1:
                        if os.path.exists(os.path.join(pdf_path,i[0])):
                            f_path = os.path.join(os.path.join(os.path.join(os.path.join(d_path,k),tname),k2),k1)
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
            d=obj.name #发货单需创建的目录名称
            d_path=os.path.join(upload_path,d)
            files={} #pdf文件目录位置,第一层批号，第二层送检机构，第三层检测项目，第四层报告编号清单
            index_files={} #致词文件
            if not os.path.exists(d_path):
                os.mkdir(d_path) #创建发货单号目录
            for l in obj.line:#遍历发货单下的批次
                if l.qty==0:continue
                k1=l.batch_no+"-"+str(l.qty)
                line_path=os.path.join(d_path,k1)  #批次所在的目录
                if not os.path.exists(line_path):
                    os.mkdir(line_path) #创建批次目录
                index_path = os.path.join(line_path,u"致词页")
                if not os.path.exists(index_path):
                    os.mkdir(index_path)

                line_path = os.path.join(line_path,u"报告")
                if not os.path.exists(line_path):
                    os.mkdir(line_path)

                if not files.has_key(k1):files[k1]={}
                if not index_files.has_key(k1):index_files[k1]={}
                for b in l.detail:
                    hospital_name = b.genes_id.hospital.name
                    hospital_path = os.path.join(line_path,hospital_name)
                    if not os.path.exists(hospital_path):
                        os.mkdir(hospital_path)

                    hospital_index_path = os.path.join(index_path,hospital_name)
                    if not os.path.exists(hospital_index_path):
                        os.mkdir(hospital_index_path)

                    if not files[k1].has_key(hospital_name):files[k1][hospital_name]={}
                    if not index_files[k1].has_key(hospital_name):index_files[k1][hospital_name]={}
                    k2=b.genes_id.package_id.name
                    box_path=os.path.join(hospital_path,k2)
                    if not os.path.exists(box_path):
                        os.mkdir(box_path)
                    box_index_path = os.path.join(hospital_index_path,k2)
                    if not os.path.exists(box_index_path):
                        os.mkdir(box_index_path)
                    if not files[k1][hospital_name].has_key(k2):files[k1][hospital_name][k2]=[]
                    if not index_files[k1][hospital_name].has_key(k2):index_files[k1][hospital_name][k2]=[]
                    pdf_file = b.genes_id.name+".pdf"
                    index_pdf_file = b.genes_id.name+"_index.pdf"
                    address = "".join([x for x in [b.genes_id.state_id.name,b.genes_id.city_id.name,b.genes_id.area_id.name,b.genes_id.address] if x])
                    files[k1][hospital_name][k2].append([pdf_file,b.genes_id.name,b.genes_id.cust_name,b.genes_id.sex,b.genes_id.date,b.genes_id.is_single_post,address,b.genes_id.mobile,b.genes_id.hospital.id])
                    index_files[k1][hospital_name][k2].append([index_pdf_file,b.genes_id.name,b.genes_id.cust_name,b.genes_id.sex,b.genes_id.date,b.genes_id.is_single_post,address,b.genes_id.mobile])

            t_count,u_count=self.pdf_copy(cr,uid,pdf_path,d_path,u"报告",files)
            self.pdf_copy(cr,uid,pdf_path,d_path,u"致词页",index_files)
            os.system("chmod 777 -R "+d_path)
            vals={
                "upload":u_count,
            }
            if obj.files==u_count:
                vals["state"]="upload"
            self.write(cr,uid,i,vals,context=context)
            #生成印刷版的发货单
            self.export_excel_to_print(cr,uid,d_path,files,context=context)

    def export_excel_to_print(self,cr,uid,d_path,files,context=None):
        w = xlwt.Workbook(encoding='utf-8')
        hospital_dict={}
        person_dict={}
        for k,v in files.items():
            ws = w.add_sheet(k)
            row=0
            batch=v.keys()
            batch.sort()
            ws.write(row,0,u"送检机构")
            ws.write(row,1,u"套餐")
            ws.write(row,2,u"样本编号")
            ws.write(row,3,u"收样日期")
            ws.write(row,4,u"姓名")
            ws.write(row,5,u"性别")
            ws.col(0).width = 4950
            row +=1

            for k1 in batch: #遍历送检机构
                if not hospital_dict.has_key(k1):hospital_dict[k1]={}
                for k2,v2 in v[k1].items(): #遍历机构下套餐
                    if not hospital_dict[k1].has_key(k2):hospital_dict[k1][k2]=[]
                    for i in v2:
                        ws.write(row,0,k1)
                        ws.write(row,1,k2)
                        ws.write(row,2,i[1])
                        ws.write(row,3,i[4])
                        ws.write(row,4,i[2])
                        ws.write(row,5,u"男" if i[3]=="M" else u"女" )
                        row +=1

                        if not i[5]:
                            hospital_dict[k1][k2].append(i)
                        else:
                            if not person_dict.has_key(k1):
                                person_dict[k1]={}
                            if not person_dict[k1].has_key(k2):
                                person_dict[k1][k2]=[]
                            person_dict[k1][k2].append(i)
        style_title = ec.get_excel_style(font_size=16,horz=xlwt.Alignment.HORZ_CENTER,border=xlwt.Borders.THIN)
        style1 = ec.get_excel_style(font_size=11,horz=xlwt.Alignment.HORZ_CENTER,border=xlwt.Borders.THIN)
        style2 = ec.get_excel_style(font_size=11,horz=xlwt.Alignment.HORZ_LEFT,border=xlwt.Borders.THIN)
        #处理汇总表内容
        total_package={"1":{},"0":{}}
        for k,v in hospital_dict.items():
            for k1,v1 in v.items():
                if not total_package["1"].has_key(k):
                    total_package["1"][k]={}
                if not total_package["1"][k].has_key(k1):
                    total_package["1"][k][k1]=0
                if not total_package["0"].has_key(k1):
                    total_package["0"][k1]=0
                total_package["1"][k][k1] = total_package["1"][k][k1] + len(v1)
                total_package["0"][k1] = total_package["0"][k1] + len(v1)

        for k,v in person_dict.items():
            for k1,v1 in v.items():
                if not total_package["1"].has_key(k):
                    total_package["1"][k]={}
                if not total_package["1"][k].has_key(k1):
                    total_package["1"][k][k1]=0
                if not total_package["0"].has_key(k1):
                    total_package["0"][k1]=0
                total_package["1"][k][k1] = total_package["1"][k][k1] + len(v1)
                total_package["0"][k1] = total_package["0"][k1] + len(v1)

        w0 = w.add_sheet(u"总表")
        w0.write_merge(0,0,0,2,u"发货单总表",style=style_title)
        row=1
        w0.write(row,0,u"送检机构",style=style1)
        w0.write(row,1,u"检测项目",style=style1)
        w0.write(row,2,u"数量",style=style1)
        w0.col(0).width = 5950
        w0.col(1).width = 4950
        row +=1
        for k,v in total_package["1"].items():
            for k2,v2 in v.items(): #遍历机构下套餐
                w0.write(row,0,k,style=style2)
                w0.write(row,1,k2,style=style2)
                w0.write(row,2,v2,style=style1)
                row +=1
        total_start_row = row
        for k,v in total_package["0"].items():
            w0.write(row,1,k,style=style2)
            w0.write(row,2,v,style=style1)
            row +=1
        w0.write_merge(total_start_row,row-1,0,0,u"汇总",style=style1)

        #处理单个机构的发货单内容
        for k1,v1 in hospital_dict.items():
            w1 = w.add_sheet(u"装箱单-"+k1)
            w1.write_merge(0,0,0,3,u"易感基因检测报告书装箱明细",style=style_title)
            w1.write(1,0,u"套餐",style=style1)
            w1.write(1,1,u"样本编号",style=style1)
            w1.write(1,2,u"姓名",style=style1)
            w1.write(1,3,u"性别",style=style1)
            w1.col(0).width = 5050
            w1.col(1).width = 4050
            w1.col(2).width = 4050
            w1.col(3).width = 4050
            row = 2
            hospital_id = 0
            for k2,v2 in v1.items():
                for i in v2:
                    w1.write(row,0,k2,style=style2)
                    w1.write(row,1,i[1],style=style2)
                    w1.write(row,2,i[2],style=style2)
                    w1.write(row,3,u"男" if i[3]=="M" else u"女",style=style1)
                    hospital_id = i[8]
                    row +=1
            row +=1
            w1.write_merge(row,row,0,3,u"发货汇总表",style=style_title)
            row +=1
            w1.write(row,0,u"序号",style=style1)
            w1.write_merge(row,row,1,2,u"套餐",style=style1)
            w1.write(row,3,u"数量（本）",style=style1)
            row_seq=1
            row +=1
            t_count=0
            for k2,v2 in v1.items():
                w1.write(row,0,row_seq,style=style1)
                w1.write_merge(row,row,1,2,k2,style=style2)
                w1.write(row,3,len(v2),style=style1)
                t_count += len(v2)
                row+=1
                row_seq +=1
            w1.write(row,0,u"汇总",style=style2)
            w1.write_merge(row,row,1,2,"",style=style2)
            w1.write(row,3,t_count,style=style1)
            row += 1
            if hospital_id:
                hospital_obj = self.pool.get("res.partner").browse(cr,uid,hospital_id,context=context)
                if hospital_obj.yg_report:
                    w1.write_merge(row,row,0,3,u"收件人：%s,%s"%(hospital_obj.yg_report.name,hospital_obj.yg_report.mobile),style=style2)
                    w1.write_merge(row+1,row+1,0,3,u"收货地址："+self.pool.get("res.partner").get_detail_address(cr,uid,hospital_obj.yg_report.id,context=context),style=style2)
                else:
                    w1.write_merge(row,row,0,3,u"收件人：",style=style2)
                    w1.write_merge(row+1,row+1,0,3,u"收货地址：",style=style2)
            else:
                w1.write_merge(row,row,0,3,u"收件人：",style=style2)
                w1.write_merge(row+1,row+1,0,3,u"收货地址：",style=style2)
        #处理单独邮寄的发货单
        if person_dict.values():
            w1 = w.add_sheet(u"装箱单-个人单独邮寄")
            w1.write(0,0,u"送检机构")
            w1.write(0,1,u"套餐")
            w1.write(0,2,u"样本编号")
            w1.write(0,3,u"收样日期")
            w1.write(0,4,u"姓名")
            w1.write(0,5,u"性别")
            w1.write(0,6,u"邮寄地址")
            w1.write(0,7,u"电话")
            row = 1
            for k1,v1 in person_dict.items():
                for k2,v2 in v1.items():
                    for i in v2:
                        w1.write(row,0,k1)
                        w1.write(row,1,k2)
                        w1.write(row,2,i[1])
                        w1.write(row,3,i[4])
                        w1.write(row,4,i[2])
                        w1.write(row,5,u"男" if i[3]=="M" else u"女")
                        w1.write(row,6,i[6])
                        w1.write(row,7,i[7])
                        row +=1
        w.save(os.path.join(d_path,u"易感发货单(印刷)")+".xls")

    def action_box_detail(self,cr,uid,id,context=None):
        if isinstance(id,(list,tuple)):
            id=id[0]
        #判断装箱明细中是否已经有产生快递单
        box_ids = self.pool.get("rhwl.genes.new.picking.box").search(cr,uid,[("picking_id","=",id),("express_id.id","!=",False)])
        if box_ids:
            raise osv.except_osv("Error",u"装箱明细中已经有产生对应的快递单，不可以重复产生。")
        box_ids = self.pool.get("rhwl.genes.new.picking.box").search(cr,uid,[("picking_id","=",id)])
        if box_ids:
            self.pool.get("rhwl.genes.new.picking.box").unlink(cr,uid,box_ids)
        genes_ids = self.pool.get("rhwl.genes.new.picking.line.detail").search(cr,uid,[("line_id.picking_id.id","=",id)],context=context)
        if genes_ids:
            box_dict={}
            for g in self.pool.get("rhwl.genes.new.picking.line.detail").browse(cr,uid,genes_ids,context=context):
                if g.genes_id.is_single_post:
                    self.pool.get("rhwl.genes.new.picking.box").create(cr,uid,{"picking_id":id,
                                                                               "partner_text":g.genes_id.cust_name,
                                                                               "address":g.genes_id.address,
                                                                               "mobile":g.genes_id.mobile,
                                                                               "qty":1,
                                                                               "state_id":g.genes_id.state_id,
                                                                               "city_id":g.genes_id.city_id,
                                                                               "area_id":g.genes_id.area_id},context=context)
                else:
                    if box_dict.has_key(g.genes_id.hospital.id):
                        box_dict[g.genes_id.hospital.id]["qty"] +=1
                        box_dict[g.genes_id.hospital.id]["detail_no"].append(g.genes_id.name)
                    else:
                        if g.genes_id.hospital.yg_report:
                            p_id = g.genes_id.hospital.yg_report.id
                        else:
                            p_id = g.genes_id.hospital.user_id.partner_id.id
                        if not p_id:
                            raise osv.except_osv("error",u"送检机构没有设置易感报告收件人，同时也没有对应的销售人员。")

                        add_dict = self.pool.get("res.partner").get_detail_address_dict(cr,uid,p_id,context=context)
                        partner_obj = self.pool.get("res.partner").browse(cr,uid,p_id,context=context)
                        box_dict[g.genes_id.hospital.id]={
                            "picking_id":id,
                            "partner_id":g.genes_id.hospital.id,
                           "partner_text":partner_obj.name,
                           "qty":1,
                           "state_id":add_dict["state_id"],
                           "city_id":add_dict["city_id"],
                           "area_id":add_dict["area_id"],
                           "address":"".join([x for x in [add_dict["street"],add_dict["street2"]] if x]),
                           "mobile":partner_obj.mobile,
                            "detail_no":[g.genes_id.name]
                        }
            if box_dict:
                for b in box_dict.values():
                    b["detail_no"] = ",".join(b["detail_no"])
                    self.pool.get("rhwl.genes.new.picking.box").create(cr,uid,b,context=context)

    def action_export_excel(self,cr,uid,id,context=None):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rhwl.gene.export.excel',
            'view_mode': 'form',
            'view_type': 'form',
            #'res_id': id,
            "context":{'func_name': 'gene_new_picking',"active_id":id,},
            'views': [(False, 'form')],
            'target': 'new',
            'name':u"导出发货单数据Excel"
        }
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
        "partner_id":fields.many2one("res.partner",string=u"收件机构",),
        "partner_text":fields.char(u"收件人",size=100),
        "address":fields.char(u"详细地址",size=150),
        "mobile": fields.char(u"手机号码", size=20),
        "qty":fields.integer(u"数量"),
        "state_id": fields.many2one("res.country.state",string=u'省'),
        "city_id": fields.many2one("res.country.state.city",string=u'市',domain="[('state_id','=',state_id)]"),
        "area_id":fields.many2one("res.country.state.city.area",string=u"区/县",domain="[('city_id','=',city_id)]"),
        "express_id":fields.many2one("stock.picking.express",u"快递单",ondelete="restrict"),
        "detail_no":fields.text("Detail No")
    }

    def action_create_express(self,cr,uid,id,context=None):
        obj = self.browse(cr,uid,id,context=context)
        product_id = self.pool.get("product.product").search(cr,uid,[("default_code","=","YGREPORT")])
        val={
            "expres_type":'1',
            "receive_type":"external",
            "receiv_user_text":obj.partner_text,
            "receiv_addr":"".join([x for x in [obj.state_id.name,obj.city_id.name,obj.area_id.name,obj.address] if x]),
            "mobile":obj.mobile,
            "state_id":obj.state_id.id,
            "city_id":obj.city_id.id,
            "area_id":obj.area_id.id,
            "product_id":product_id[0],
            "product_qty":obj.qty,
            "receiv_real_qty":obj.qty
        }
        express_id = self.pool.get("stock.picking.express").create(cr,uid,val,context=context)
        self.write(cr,uid,obj.id,{"express_id":express_id},context=context)
        if obj.detail_no:
            for d in obj.detail_no.split(","):
                self.pool.get("stock.picking.express.detail").create(cr,uid,{"parent_id":express_id,"number_seq":d},context=context)

    def action_open_express(self,cr,uid,id,context=None):
        obj = self.browse(cr,uid,id,context=context)

        mod_obj = self.pool.get('ir.model.data')
        dummy, action_id = tuple(mod_obj.get_object_reference(cr, uid, 'l10n_cn_express_track', 'action_stock_express'))
        action = self.pool.get('ir.actions.act_window').read(cr, uid, action_id, context=context)
        action['context'] = {}

        res = mod_obj.get_object_reference(cr, uid, 'rhwl', 'rhwl_stock_picking_express_form')
        action['views'] = [(res and res[1] or False, 'form')]
        action['res_id'] = obj.express_id.id and obj.express_id.id or False

        return action