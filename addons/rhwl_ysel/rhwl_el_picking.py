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
    _name="rhwl.genes.el.picking"

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
        "line":fields.one2many("rhwl.genes.el.picking.line","picking_id","Detail"),
        "box":fields.one2many("rhwl.genes.el.picking.box","picking_id",string="Box",readonly=True),
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
            self.pool.get("rhwl.genes.el").write(cr,uid,genes_id,{"state":stat[val["state"]]},context=context)
        return id

    def pdf_copy(self,cr,uid,pdf_path,d_path,files):
        u_count = 0
        t_count = 0

        for k,v in files.items():
            t_count += len(v)
            for i in v:
                if os.path.exists(os.path.join(pdf_path,i[0])):
                    f_path = os.path.join(d_path,k)
                    if (not os.path.exists(os.path.join(f_path,i[0]))) or os.stat(os.path.join(pdf_path,i[0])).st_size != os.stat(os.path.join(f_path,i[0])).st_size:
                        shutil.copy(os.path.join(pdf_path,i[0]),os.path.join(f_path,i[0]))

                    u_count += 1
        return (t_count,u_count)

    #根据发货单，生成需要上传的目录结构，并复制pdf文件到相应的目录中。
    def report_upload(self,cr,uid,context=None):
        for i in self.search(cr,uid,[("state","=","draft")],context=context):
            self.action_pdf_upload(cr,uid,i,context=context)

    def action_pdf_upload(self,cr,uid,id,context=None):
        upload_path = os.path.join(os.path.split(__file__)[0], "static/local/upload/ys")
        pdf_path = os.path.join(os.path.split(__file__)[0], "static/local/report/ys")

        if isinstance(id,(long,int)):
            id=[id]

        for i in id:
            obj=self.browse(cr,uid,i,context=context)
            d=obj.name #发货单需创建的目录名称
            d_path=os.path.join(upload_path,d)
            files={}
            if not os.path.exists(d_path):
                os.mkdir(d_path)
            for l in obj.line:
                if l.qty==0:continue

                for b in l.detail:
                    if b.genes_id.is_single_post:
                        k1 = u"单独邮寄"
                    else:
                        k1 = b.genes_id.hospital.name
                    if not files.has_key(k1):
                        files[k1]=[]
                    box_path=os.path.join(d_path,k1)
                    if not os.path.exists(box_path):
                        os.mkdir(box_path)

                    pdf_file = b.genes_id.name+".pdf"
                    files[k1].append([pdf_file,b.genes_id.name,b.genes_id.cust_name,b.genes_id.sex,b.genes_id.tel,"".join([x for x in [b.genes_id.state_id.name,b.genes_id.city_id.name,b.genes_id.area_id.name,b.genes_id.address] if x]),b.genes_id.hospital.name,b.genes_id.date])

            t_count,u_count=self.pdf_copy(cr,uid,pdf_path,d_path,files)

            vals={
                "upload":u_count,
            }
            if obj.files==u_count:
                vals["state"]="upload"
            self.write(cr,uid,i,vals,context=context)
            #生成印刷版的发货单
            self.export_excel_to_print(obj.name,obj.date,d_path,files)

    def export_excel_to_print(self,no,send_date,d_path,files):
        w = xlwt.Workbook(encoding='utf-8')
        single_dict = files.get(u"单独邮寄",[])
        if single_dict:
            files.remove(u"单独邮寄")

        #12号字,水平居中,垂直居中
        title_style = xlwt.XFStyle()
        title_style.font = xlwt.Font()
        title_style.font.name=u"宋体"
        title_style.font.height = 240
        title_style.alignment = xlwt.Alignment()
        title_style.alignment.horz = xlwt.Alignment.HORZ_CENTER
        title_style.alignment.vert = xlwt.Alignment.VERT_CENTER

        #11号字,水平居中,垂直居中
        style = xlwt.XFStyle()
        style.font = xlwt.Font()
        style.font.name=u"宋体"
        style.font.height = 220
        style.alignment = xlwt.Alignment()
        style.alignment.horz = xlwt.Alignment.HORZ_CENTER
        style.alignment.vert = xlwt.Alignment.VERT_CENTER

        #18号字,水平居中,垂直居中,画线
        title_style1 = xlwt.XFStyle()
        title_style1.font = xlwt.Font()
        title_style1.font.name=u"宋体"
        title_style1.font.height = 360
        title_style1.alignment = xlwt.Alignment()
        title_style1.alignment.horz = xlwt.Alignment.HORZ_CENTER
        title_style1.alignment.vert = xlwt.Alignment.VERT_CENTER
        title_style1.borders = xlwt.Borders() # Add Borders to Style
        title_style1.borders.left = xlwt.Borders.MEDIUM # May be: NO_LINE, THIN, MEDIUM, DASHED, DOTTED, THICK, DOUBLE, HAIR, MEDIUM_DASHED, THIN_DASH_DOTTED, MEDIUM_DASH_DOTTED, THIN_DASH_DOT_DOTTED, MEDIUM_DASH_DOT_DOTTED, SLANTED_MEDIUM_DASH_DOTTED, or 0x00 through 0x0D.
        title_style1.borders.right = xlwt.Borders.MEDIUM
        title_style1.borders.top = xlwt.Borders.MEDIUM
        title_style1.borders.bottom = xlwt.Borders.MEDIUM
        title_style1.borders.left_colour = 0x40
        title_style1.borders.right_colour = 0x40
        title_style1.borders.top_colour = 0x40
        title_style1.borders.bottom_colour = 0x40

        #12号字,水平居中,垂直居中,画线
        style2 = xlwt.XFStyle()
        style2.font = xlwt.Font()
        style2.font.name=u"宋体"
        style2.font.height = 240
        style2.alignment = xlwt.Alignment()
        style2.alignment.horz = xlwt.Alignment.HORZ_CENTER
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

        #发货单
        ws0 = w.add_sheet(u"发货单")
        ws0.col(1).width = 4300
        ws0.col(2).width = 10750
        ws0.col(4).width = 5000
        ws0.write_merge(1,1,0,3,u"耳聋检测报告送货清单(日期:%s)" %(send_date,),style=title_style1)
        ws0.write(1,4,no,style=title_style1)
        ws0.write(2,0,u"序号",style=style2)
        ws0.write(2,1,u"货品名称",style=style2)
        ws0.write(2,2,u"送检机构",style=style2)
        ws0.write(2,3,u"包裹数量",style=style2)
        ws0.write(2,4,u"报告数量（份）",style=style2)
        row=3
        total_pack=0
        total_report=0
        for k,v in files.items():
            ws0.write(row,0,row-2,style=style2)
            ws0.write(row,1,u"检测报告",style=style2)
            ws0.write(row,2,k,style=style2)
            ws0.write(row,3,1,style=style2)
            ws0.write(row,4,len(v),style=style2)
            row +=1
            total_pack +=1
            total_report += len(v)

        if single_dict:
            ws0.write(row,0,row-2)
            ws0.write(row,1,u"检测报告",style=style2)
            ws0.write(row,2,u"单独邮寄",style=style2)
            ws0.write(row,3,len(single_dict),style=style2)
            ws0.write(row,4,len(single_dict),style=style2)
            total_pack +=len(single_dict)
            total_report += len(single_dict)
            row +=1
        ws0.write_merge(row,row,0,2,u"合计件数",style=style2)
        ws0.write(row,3,total_pack,style=style2)
        ws0.write(row,4,total_report,style=style2)

        for k,v in files.items():
            ws = w.add_sheet(k)
            ws.col(0).width = 3200 #1000 = 3.715(Excel)
            ws.col(3).width = 3200
            ws.write_merge(0,0,0,3,k+u"耳聋报告清单",style=title_style)
            row=1

            ws.write(row,0,u"样本编号",style=style)
            ws.write(row,1,u"姓名",style=style)
            ws.write(row,2,u"性别",style=style)
            ws.write(row,3,u"送检日期",style=style)
            row +=1
            for i in v:
                ws.write(row,0,i[1],style=style)
                ws.write(row,1,i[2],style=style)
                ws.write(row,2,u"男" if i[3]=="M" else u"女" ,style=style)
                ws.write(row,3,i[7],style=style)
                row +=1
        if single_dict:
            ws2 = w.add_sheet(u"单独邮寄")
            ws2.col(0).width = 6200
            ws2.col(1).width = 3200
            ws2.col(4).width = 3200
            ws2.col(5).width = 4200
            ws2.col(6).width = 8200
            ws2.write_merge(0,0,0,6,u"单独邮寄耳聋报告清单",style=title_style)
            row=1
            ws2.write(row,0,u"送检机构",style=style)
            ws2.write(row,1,u"样本编号",style=style)
            ws2.write(row,2,u"姓名",style=style)
            ws2.write(row,3,u"性别",style=style)
            ws2.write(row,4,u"送检日期",style=style)
            ws2.write(row,5,u"电话",style=style)
            ws2.write(row,6,u"邮寄地址",style=style)
            row +=1
            for i in single_dict:
                ws2.write(row,0,i[6],style=style)
                ws2.write(row,1,i[1],style=style)
                ws2.write(row,2,i[2],style=style)
                ws2.write(row,3,u"男" if i[3]=="M" else u"女" ,style=style)
                ws2.write(row,4,i[7] ,style=style)
                ws2.write(row,5,i[4] ,style=style)
                ws2.write(row,6,i[5] ,style=style)
                row +=1
        w.save(os.path.join(d_path,no+u"耳聋发货单")+".xls")

    def action_box_detail(self,cr,uid,id,context=None):
        if isinstance(id,(list,tuple)):
            id=id[0]
        #判断装箱明细中是否已经有产生快递单
        box_ids = self.pool.get("rhwl.genes.el.picking.box").search(cr,uid,[("picking_id","=",id),("express_id.id","!=",False)])
        if box_ids:
            raise osv.except_osv("Error",u"装箱明细中已经有产生对应的快递单，不可以重复产生。")
        box_ids = self.pool.get("rhwl.genes.el.picking.box").search(cr,uid,[("picking_id","=",id)])
        if box_ids:
            self.pool.get("rhwl.genes.el.picking.box").unlink(cr,uid,box_ids)
        genes_ids = self.pool.get("rhwl.genes.el.picking.line.detail").search(cr,uid,[("line_id.picking_id.id","=",id)],context=context)
        if genes_ids:
            box_dict={}
            for g in self.pool.get("rhwl.genes.el.picking.line.detail").browse(cr,uid,genes_ids,context=context):
                if g.genes_id.is_single_post:
                    self.pool.get("rhwl.genes.el.picking.box").create(cr,uid,{"picking_id":id,
                                                                               "partner_text":g.genes_id.cust_name,
                                                                               "address":g.genes_id.address,
                                                                               "mobile":g.genes_id.mobile,
                                                                               "qty":1,
                                                                               "state_id":g.genes_id.state_id,
                                                                               "city_id":g.genes_id.city_id,
                                                                               "area_id":g.genes_id.area_id,
                                                                               "detail_no":g.genes_id.name},context=context)
                else:
                    if box_dict.has_key(g.genes_id.hospital.id):
                        box_dict[g.genes_id.hospital.id]["qty"] +=1
                        box_dict[g.genes_id.hospital.id]["detail_no"].append(g.genes_id.name)
                    else:
                        if g.genes_id.hospital.el_report:
                            p_id = g.genes_id.hospital.el_report.id
                        else:
                            p_id = g.genes_id.hospital.user_id.partner_id.id
                        if not p_id:
                            raise osv.except_osv("error",u"送检机构没有设置耳聋报告收件人，同时也没有对应的销售人员。")

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
                    self.pool.get("rhwl.genes.el.picking.box").create(cr,uid,b,context=context)

    def action_export_excel(self,cr,uid,id,context=None):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rhwl.gene.export.excel',
            'view_mode': 'form',
            'view_type': 'form',
            #'res_id': id,
            "context":{'func_name': 'gene_el_picking',"active_id":id,},
            'views': [(False, 'form')],
            'target': 'new',
            'name':u"导出发货单数据Excel"
        }
#发货单批次明细对象
class rhwl_picking_line(osv.osv):
    _name = "rhwl.genes.el.picking.line"

    def _get_detail_qty(self,cr,uid,ids,field_names,arg,context=None):
        res=dict.fromkeys(ids,0)
        for k in res.keys():
            res[k] = self.pool.get("rhwl.genes.el.picking.line.detail").search_count(cr,uid,[("line_id.id","=",k)])
        return res

    _order = "seq"
    _columns={
        "picking_id":fields.many2one("rhwl.genes.el.picking",u"发货单号",ondelete="restrict"),
        "seq":fields.integer(u"序号",required=True),
        "product_name":fields.char(u"货品名称",size=20),
        "batch_no":fields.char(u"批号",size=15,required=True),
        "batch_kind":fields.selection([("normal",u"普通"),("resend",u"破损重印")],u"类型"),
        "qty":fields.function(_get_detail_qty,arg="batch_no",type="integer",string=u"数量"),
        "note":fields.char(u"备注",size=200),
        "detail":fields.one2many("rhwl.genes.el.picking.line.detail","line_id","Detail"),

    }
    _defaults={
        "product_name":u"检测报告",
        "batch_kind":"normal",

    }
    _sql_constraints = [
        ('rhwl_genes_el_picking_seq_uniq', 'unique(picking_id,seq)', u'发货明细序号不能重复!'),
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
            ids=self.pool.get("rhwl.genes.el").search(cr,uid,[("batch_no","=",val.get("batch_no"))],context=context)
            if not ids:
                raise osv.except_osv(u"错误",u"批次号不存在，请输入正确的批次号码。")
            else:
                val["detail"]=[]
                for i in ids:
                    val["detail"].append([0,0,{"genes_id":i}])

        line_id = super(rhwl_picking_line,self).create(cr,uid,val,context=context)

        return line_id

class rhwl_picking_detail(osv.osv):
    _name="rhwl.genes.el.picking.line.detail"
    _columns={
        "line_id":fields.many2one("rhwl.genes.el.picking.line",u"批号",ondelete="cascade"),
        "genes_id":fields.many2one("rhwl.genes.el",u"样本编号",ondelete="restrict",required=True),
        "name":fields.related("genes_id","cust_name",type="char",string=u"客户姓名"),

    }

class rhwl_picking_box(osv.osv):
    _name = "rhwl.genes.el.picking.box"
    _columns={
        "picking_id":fields.many2one("rhwl.genes.el.picking",u"发货单号",ondelete="restrict"),
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
        product_id = self.pool.get("product.product").search(cr,uid,[("default_code","=","ELREPORT")])
        val={
            "express_type":'1',
            "receive_type":"external",
            "receiv_user_text":obj.partner_text,
            "receiv_addr":"".join([x for x in [obj.state_id.name,obj.city_id.name,obj.area_id.name,obj.address] if x]),
            "mobile":obj.mobile,
            "state_id":obj.state_id.id,
            "city_id":obj.city_id.id,
            "area_id":obj.area_id.id,
            "product_id":product_id[0],
            "product_qty":obj.qty,
            "receiv_real_qty":obj.qty,
            "receiv_partner":obj.partner_id.id
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