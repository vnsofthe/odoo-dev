# -*- coding: utf-8 -*-

import threading
from openerp.osv import osv,fields
import base64
from tempfile import NamedTemporaryFile
import xlrd,os
import datetime
import logging
import rhwl_gene_check
import xlwt
_logger = logging.getLogger(__name__)
class rhwl_import(osv.osv_memory):
    _name = 'rhwl.genes.import'
    _columns = {
        "file_bin":fields.binary(string=u"样本信息文件名"),
        "file_bin2":fields.binary(string=u"质检结果文件"),
        "file_bin3":fields.binary(string=u"位点结果文件"),
        "is_over":fields.boolean(u"是否覆盖已转入数据?"),
        "hospital":fields.many2one("res.partner",u"送检机构",domain="[('is_company', '=', True), ('customer', '=', True)]"),
        "cust_prop":fields.selection([("hospital",u"医院"),("insurance",u"保险"),("internal",u"内部员工"),("custom",u"公司客户"),("other",u"其它")],string=u"客户属性"),
        "is_second":fields.boolean(u"重提DAN库存"),
    }
    _defaults={
        "is_over":False,
        "is_second":False
    }

    def date_trun(self,val):
        if not val:
            return fields.date.today()
        if isinstance(val,str):val=val.replace(".","/")
        if list(str(val)).count("/")==0:
            d=xlrd.xldate_as_tuple(int(val),0)
            return "%s/%s/%s"%(d[0],d[1],d[2])
        if list(str(val)).count("/")==1:
            val=val.split("/")[0]
            return val[:4]+'/'+val[4:6]+'/'+val[6:8]
        else:
            return val.replace(".","/")

    def datetime_trun(self,val):
        if list(str(val)).count("/")==0:
            d=xlrd.xldate_as_tuple(val,0)
            return "%s/%s/%s %s:%s:%s"%(d[0],d[1],d[2],d[3],d[4],d[5])
        else:
            return val

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

            try:
                bk = xlrd.open_workbook(xlsname+".xls")
                sh = bk.sheet_by_index(0)
            except:
               raise osv.except_osv(u"打开出错",u"请确认文件格式是否为正确的报告标准格式。")
            nrows = sh.nrows
            ncols = sh.ncols
            batch_no={}
            if ncols>=7 and sh.cell_value(2,7)==u"产品类别":
                for i in range(3,nrows):
                    if not sh.cell_value(i,0):continue
                    date_col=self.date_trun(sh.cell_value(i,0))
                    idt=sh.cell_value(i,4)
                    val={
                        "date":date_col,
                        "cust_name":sh.cell_value(i,1).encode("utf-8").replace(".","·").replace("▪","·"),
                        "sex": 'T' if sh.cell_value(i,2)==u"男" else 'F',
                        "name":sh.cell_value(i,3),
                        "identity":idt,
                        "is_child":True if len(idt)==18 and int(idt[6:10])>=(datetime.datetime.today().year-12) and int(idt[6:10])<(datetime.datetime.today().year) else False,
                        "receiv_date":self.datetime_trun(sh.cell_value(i,5)),
                        "package":sh.cell_value(i,8)
                    }
                    if idt and len(idt)==18:
                        try:
                            val["birthday"] = datetime.datetime.strptime(idt[6:14],"%Y%m%d").strftime("%Y/%m/%d")
                        except:
                            pass
                    if not batch_no.has_key(date_col):
                        batch_no[date_col]={}
                    if batch_no.get(date_col).get(val["package"]):
                        val["batch_no"]=batch_no.get(date_col).get(val["package"])
                    else:
                        cr.execute("select max(batch_no) from rhwl_easy_genes where cust_prop in ('tjs','tjs_vip') and package='%s' "%(val["package"]))
                        max_no=val["package"]+"-000"
                        for no in cr.fetchall():
                            max_no = no[0]
                        if val["package"]=="01":
                            max_no=str(int(max_no)+1).zfill(3)
                        else:
                            max_no=max_no[0:3]+str(int(max_no[3:])+1).zfill(3)
                        batch_no[date_col][val["package"]]=max_no
                        val["batch_no"]=max_no
                    self.pool.get("rhwl.easy.genes").create(cr,uid,val,context=context)
            else:
                for i in range(2,nrows+1):
                    if not sh.cell_value(i-1,0):continue
                    date_col=self.date_trun(sh.cell_value(i-1,0))
                    idt=sh.cell_value(i-1,4)
                    val={
                        "date":date_col,
                        "cust_name":sh.cell_value(i-1,1).encode("utf-8").replace(".","·").replace("▪","·"),
                        "sex": 'T' if sh.cell_value(i-1,2)==u"男" else 'F',
                        "name":sh.cell_value(i-1,3),
                        "identity":idt,
                        "is_child":True if len(idt)==18 and int(idt[6:10])>=(datetime.datetime.today().year-12) and int(idt[6:10])<(datetime.datetime.today().year) else False,
                        "receiv_date":self.datetime_trun(sh.cell_value(i-1,5))
                    }
                    if idt and len(idt)==18:
                        try:
                            val["birthday"] = datetime.datetime.strptime(idt[6:14],"%Y%m%d").strftime("%Y/%m/%d")
                        except:
                            pass
                    if batch_no.get(date_col):
                        val["batch_no"]=batch_no.get(date_col)
                    else:
                        cr.execute("select max(batch_no) from rhwl_easy_genes where cust_prop='tjs' and package='01'")
                        max_no="0"
                        for no in cr.fetchall():
                            max_no = no[0]
                        max_no=str(int(max_no)+1).zfill(3)
                        batch_no[date_col]=max_no
                        val["batch_no"]=max_no
                    self.pool.get("rhwl.easy.genes").create(cr,uid,val,context=context)

        finally:
            f.close()
            os.remove(xlsname+'.xls')
        v_id=self.pool.get('ir.ui.view').search(cr,uid,[('name', '=', "rhwl.easy.genes.view.tree")])

        return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                "view_id":v_id,
                'res_model': 'rhwl.easy.genes',
                "context":{'search_default_type_draft':1,'search_default_type_exceptconfirm':1},
                'view_mode': 'tree'}

    def import_report2(self, cr, uid, ids, context=None):
        """接收质检数据"""
        if context is None:
            context = {}
        this = self.browse(cr, uid, ids[0])

        fileobj = NamedTemporaryFile('w+',delete=True)
        xlsname =  fileobj.name
        f=open(xlsname+'.xls','wb')
        fileobj.close()
        try:
            #fileobj.write(base64.decodestring(this.file_bin.decode('base64')))
            b=this.file_bin2.decode('base64')
            f.write(b)
            f.close()

            try:
                bk = xlrd.open_workbook(xlsname+".xls")
                sh = bk.sheet_by_index(0)
            except:
               raise osv.except_osv(u"打开出错",u"请确认质检数据文件格式是否为正确的报告标准格式。")
            nrows = sh.nrows
            genes_ids=[]
            for i in range(2,nrows):
                no=sh.cell_value(i,1)
                if not no:continue
                if type(no)==type(1.0):no = no.__trunc__()
                id=self.pool.get("rhwl.easy.genes").search(cr,uid,[("name","=",no)],context=context)
                if not id:
                    raise osv.except_osv(u"错误",u"基因编号[%s]不存在."%(no,))
                if genes_ids.count(id[0])>0:
                    raise osv.except_osv(u"错误",u"基因编号[%s]在Excel中存在多笔。"%(no,))
                genes_ids.append(id[0])
                self.pool.get("rhwl.easy.genes").write(cr,uid,id,{"log":[[0,0,{"note":u"导入质检数据","data":"DNA"}]]},context=context)
                obj_ids = self.pool.get("rhwl.easy.genes.check").search(cr,uid,[("genes_id.name",'=',no)],context=context)
                if obj_ids:
                    self.pool.get("rhwl.easy.genes.check").write(cr,uid,obj_ids,{"active":False})
                t1=sh.cell_value(i,4)
                t2=sh.cell_value(i,5)
                t3=sh.cell_value(i,6)
                t4=sh.cell_value(i,8)
                if not t4:t4=0
                val={
                        "genes_id":id[0],
                        "date":self.date_trun(sh.cell_value(i,0)),
                        "dna_date":self.date_trun(sh.cell_value(i,2)),
                        "concentration":round(t1,2),
                        "lib_person":sh.cell_value(i,3),
                        "od260_280":round(t2,2),
                        "od260_230":round(t3,2),
                        "chk_person":sh.cell_value(i,7),
                        "data_loss":str(round(t4,4)*100)+"%",
                        "loss_person":sh.cell_value(i,9),
                        "loss_date":self.date_trun(sh.cell_value(i,10)),
                        "active":True,
                    }

                self.pool.get("rhwl.easy.genes.check").create(cr,uid,val,context=context)

                if (t4>0.01):
                    self.pool.get("rhwl.easy.genes").action_state_dna(cr,uid,id,context=context)
                else:
                    genes_obj = self.pool.get("rhwl.easy.genes").browse(cr,uid,id,context=context)
                    if genes_obj.state in ('except_confirm','confirm'):
                        self.pool.get("rhwl.easy.genes").action_state_dnaok(cr,uid,id,context=context)

        finally:
            f.close()
            os.remove(xlsname+'.xls')

        return

    def import_report3(self, cr, uid, ids, context=None):
        """接收检测点位数据"""
        if context is None:
            context = {}
        this = self.browse(cr, uid, ids[0])
        over_no=[] #记录重复转入的样本号
        fileobj = NamedTemporaryFile('w+',delete=True)
        xlsname =  fileobj.name
        f=open(xlsname+'.xls','wb')
        fileobj.close()
        try:
            #fileobj.write(base64.decodestring(this.file_bin.decode('base64')))
            b=this.file_bin3.decode('base64')
            f.write(b)
            f.close()
            try:
                bk = xlrd.open_workbook(xlsname+".xls")
                sh = bk.sheet_by_index(0)
            except:
               raise osv.except_osv(u"打开出错",u"请确认位点数据文件格式是否为正确的报告标准格式。")
            nrows = sh.nrows
            ncols = sh.ncols
            snp={}
            for i in range(1,ncols):
                v=sh.cell_value(0,i)
                if not v:continue
                #if not rhwl_gene_check.snp_check.has_key(v):
                    #raise osv.except_osv(u"错误",u"转入数据中的位点名称[%s]不正确。" %(v,))
                snp[i]=v

            genes_ids=[]
            for i in range(1,nrows):
                no=sh.cell_value(i,0)
                if not no:continue
                id=self.pool.get("rhwl.easy.genes").search(cr,uid,[("name","=",no)],context=context)
                if not id:
                    raise osv.except_osv(u"错误",u"基因样本编码[%s]不存在。"%(no,))
                if genes_ids.count(id[0])>0:
                    raise osv.except_osv(u"错误",u"基因编号[%s]在Excel中存在多笔。"%(no,))
                genes_ids.append(id[0])
                self.pool.get("rhwl.easy.genes").write(cr,uid,id,{"log":[[0,0,{"note":u"导入位点数据","data":"SNP"}]]},context=context)
                type_ids = self.pool.get("rhwl.easy.genes.type").search(cr,uid,[("genes_id","=",id[0])],context=context)
                old_type={}
                if type_ids:
                    over_no.append(no)
                    for t in self.pool.get("rhwl.easy.genes.type").browse(cr,uid,type_ids,context=context):
                        old_type[t.snp]=t.typ
                is_ok=True #判断全部位点是否有值
                for k in snp.keys():
                    v=str(sh.cell_value(i,k)).split(".")[0].replace("/","")
                    if old_type.has_key(snp.get(k)):
                        if old_type[snp.get(k)]=="N/A":
                            old_type[snp.get(k)]=v
                        if v=="N/A":
                            v=old_type[snp.get(k)]
                        if this.is_over==False and old_type[snp.get(k)] != v:
                            raise osv.except_osv(u"错误",u"基因样本编码[%s]位点[%s]原来的值为[%s],现在的值为[%s],请确认原因。"%(no,snp.get(k),old_type[snp.get(k)],v))
                    # for s in list(v.replace("/","")):
                    #     if rhwl_gene_check.snp_check[snp.get(k)].count(s)==0:
                    #         raise osv.except_osv(u"错误",u"基因样本编码[%s]的位点[%s]数据是[%s]，不能通过检验。"%(no,snp.get(k),v))
                    # if snp.get(k) in ('GSTM1','GSTT1') and len(v)!=1:
                    #     raise osv.except_osv(u"错误",u"基因样本编码[%s]的位点[%s]数据是[%s]，不能通过检验。"%(no,snp.get(k),v))
                    # if snp.get(k) not in ('GSTM1','GSTT1') and len(v)!=2:
                    #     raise osv.except_osv(u"错误",u"基因样本编码[%s]的位点[%s]数据是[%s]，不能通过检验。"%(no,snp.get(k),v))

                    val={
                        "genes_id":id[0],
                        "snp":snp.get(k),
                        "typ": v.replace("/",""),
                    }
                    self.pool.get("rhwl.easy.genes.type").create(cr,uid,val,context=context)
                    if v=="N/A":is_ok=False
                self.pool.get("rhwl.easy.genes").action_state_ok(cr,uid,id,context=context)
                if type_ids:
                    self.pool.get("rhwl.easy.genes.type").write(cr,uid,type_ids,{"active":False},context=context)
            if this.is_over==False and over_no:
                raise osv.except_osv(u"错误",u"基因样本编码[%s]的位点数据有重复。"%(','.join(over_no)))

        finally:
            f.close()
            os.remove(xlsname+'.xls')

        return

    def import_report4(self,cr,uid,ids,context=None):
        self.import_report2(cr,uid,ids,context=context)
        self.import_report3(cr,uid,ids,context=context)
        return

    def import_report10(self, cr, uid, ids, context=None):
        """接收检测点位数据"""
        if context is None:
            context = {}
        this = self.browse(cr, uid, ids[0])
        over_no=[] #记录重复转入的样本号
        fileobj = NamedTemporaryFile('w+',delete=True)
        xlsname =  fileobj.name
        f=open(xlsname+'.xls','wb')
        fileobj.close()
        try:
            #fileobj.write(base64.decodestring(this.file_bin.decode('base64')))
            b=this.file_bin.decode('base64')
            f.write(b)
            f.close()
            try:
                bk = xlrd.open_workbook(xlsname+".xls")
                sh = bk.sheet_by_index(0)
            except:
               raise osv.except_osv(u"打开出错",u"请确认位点数据文件格式是否为正确的报告标准格式。")
            nrows = sh.nrows
            ncols = sh.ncols
            snp={}
            for i in range(1,ncols):
                v=sh.cell_value(0,i)
                if not v:continue
                snp[i]=v
            is_checked_package=[]
            genes_ids=[]
            for i in range(1,nrows):
                no=sh.cell_value(i,0)
                if not no:continue
                id=self.pool.get("rhwl.easy.genes.new").search(cr,uid,[("name","=",no)],context=context)
                if not id:
                    raise osv.except_osv(u"错误",u"基因样本编码[%s]不存在。"%(no,))
                if genes_ids.count(id[0])>0:
                    raise osv.except_osv(u"错误",u"基因编号[%s]在Excel中存在多笔。"%(no,))
                genes_ids.append(id[0])
                #检查套餐所需要的位点在本次是否全部导入
                genes_obj = self.pool.get("rhwl.easy.genes.new").browse(cr,uid,id[0],context=context)
                if is_checked_package.count(genes_obj.package_id.id)==0:

                    loss_snp = self.pool.get("rhwl.genes.base.package")._check_snp(cr,uid,genes_obj.package_id.id,snp.values(),context=context)
                    if loss_snp:
                        raise osv.except_osv(u"错误",u"样本[%s]检测套餐[%s]所需检测位点[%s]在本次导入不存在。"%(genes_obj.name,genes_obj.package_id.name,u",".join(loss_snp)))
                    is_checked_package.append(genes_obj.package_id.id)

                self.pool.get("rhwl.easy.genes.new").write(cr,uid,id,{"log":[[0,0,{"note":u"导入位点数据","data":"SNP"}]]},context=context)
                type_ids = self.pool.get("rhwl.easy.genes.new.type").search(cr,uid,[("genes_id","=",id[0])],context=context)
                old_type={}
                if type_ids:
                    over_no.append(no)
                    for t in self.pool.get("rhwl.easy.genes.new.type").browse(cr,uid,type_ids,context=context):
                        old_type[t.snp]=t.typ
                is_ok=True #判断全部位点是否有值
                for k in snp.keys():
                    v=str(sh.cell_value(i,k)).split(".")[0].replace("/","")
                    if old_type.has_key(snp.get(k)):
                        if old_type[snp.get(k)]=="N/A":
                            old_type[snp.get(k)]=v
                        if v=="N/A":
                            v=old_type[snp.get(k)]
                        if this.is_over==False and old_type[snp.get(k)] != v:
                            raise osv.except_osv(u"错误",u"基因样本编码[%s]位点[%s]原来的值为[%s],现在的值为[%s],请确认原因。"%(no,snp.get(k),old_type[snp.get(k)],v))

                    val={
                        "genes_id":id[0],
                        "snp":snp.get(k),
                        "typ": v.replace("/",""),
                    }
                    self.pool.get("rhwl.easy.genes.new.type").create(cr,uid,val,context=context)
                    if v=="N/A":is_ok=False
                self.pool.get("rhwl.easy.genes.new").write(cr,uid,id,{"batch_no":"YG"+datetime.datetime.now().strftime("%y%m%d")},context=context)
                self.pool.get("rhwl.easy.genes.new").action_state_ok(cr,uid,id,context=context)
                if type_ids:
                    self.pool.get("rhwl.easy.genes.new.type").write(cr,uid,type_ids,{"active":False},context=context)
            if this.is_over==False and over_no:
                raise osv.except_osv(u"错误",u"基因样本编码[%s]的位点数据有重复。"%(','.join(over_no)))

        finally:
            f.close()
            os.remove(xlsname+'.xls')

        return

    def import_report5(self,cr,uid,ids,context=None):
        if context is None:
            context = {}
        this = self.browse(cr, uid, ids[0])
        if not this.hospital:
            raise osv.except_osv(u"出错",u"送检机构不能为空。")
        if not this.cust_prop:
            raise osv.except_osv(u"出错",u"客户属性不能为空。")

        fileobj = NamedTemporaryFile('w+',delete=True)
        xlsname =  fileobj.name
        f=open(xlsname+'.xls','wb')
        fileobj.close()
        try:
            #fileobj.write(base64.decodestring(this.file_bin.decode('base64')))
            b=this.file_bin.decode('base64')
            f.write(b)
            f.close()

            try:
                bk = xlrd.open_workbook(xlsname+".xls")
                sh = bk.sheet_by_index(0)
            except:
               raise osv.except_osv(u"打开出错",u"请确认文件格式是否为正确的报告标准格式。")
            nrows = sh.nrows
            ncols = sh.ncols
            batch_no={}
            """检测项目，姓名，性别，联系电话，样本编码，身份证号，采样日期，收货分支"""
            for i in range(1,nrows):
                if not sh.cell_value(i,1):continue

                name_col=sh.cell_value(i,1)
                idt=sh.cell_value(i,5)
                package_name = sh.cell_value(i,0)
                package_ids = self.pool.get("rhwl.genes.base.package").search(cr,uid,[("is_product","=",True),("name","=",package_name)])
                if not package_ids:
                    raise osv.except_osv(u"出错",u"检测项目[%s]不存在。"%(package_name,))
                mobile = sh.cell_value(i,3)
                if type(mobile)==type(1.0):mobile = mobile.__trunc__()
                receiv_dept=""
                if ncols>7:receiv_dept = sh.cell_value(i,7)
                val={
                    "cust_name":name_col.encode("utf-8").replace(".","·").replace("▪","·"),
                    "sex": 'M' if sh.cell_value(i,2).rstrip()==u"男" else 'F',
                    "mobile":mobile,
                    "name":sh.cell_value(i,4),
                    "identity":idt,
                    "date":self.date_trun(sh.cell_value(i,6)),
                    "hospital":this.hospital.id,
                    "cust_prop":this.cust_prop,
                    "package_id":package_ids[0],
                    "receiv_dept":receiv_dept
                }
                if idt and len(idt)==18:
                    try:
                        val["birthday"] = datetime.datetime.strptime(idt[6:14],"%Y%m%d").strftime("%Y/%m/%d")
                    except:
                        pass
                if self.pool.get("rhwl.easy.genes.new").search_count(cr,uid,[("name","=",val["name"])])>0:
                    raise osv.except_osv(u"出错",u"样本编码[%s]已经存在，不可重新导入。"%(val["name"]))
                self.pool.get("rhwl.easy.genes.new").create(cr,uid,val,context=context)

        finally:
            f.close()
            os.remove(xlsname+'.xls')
        v_id=self.pool.get('ir.ui.view').search(cr,uid,[('name', '=', "rhwl.easy.genes.new.view.tree")])

        return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                "view_id":v_id,
                'res_model': 'rhwl.easy.genes.new',
                "context":{'search_default_type_draft':1},
                'view_mode': 'tree'}

    def import_report6(self,cr,uid,ids,context=None):
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

            try:
                bk = xlrd.open_workbook(xlsname+".xls")
                sh = bk.sheet_by_index(0)
            except:
               raise osv.except_osv(u"打开出错",u"请确认文件格式是否为正确的报告标准格式。")
            nrows = sh.nrows

            w = xlwt.Workbook(encoding='utf-8')
            ws = w.add_sheet("Sheet1")

            for i in range(0,nrows):
                gene_no = sh.cell_value(i,0)
                if not gene_no:continue
                gene_ids = self.pool.get("rhwl.easy.genes.new").search(cr,uid,[("name","=",gene_no)])
                if not gene_ids:
                    ws.write(i,1,u"无此样本编号")
                else:
                    gene_obj = self.pool.get("rhwl.easy.genes.new").browse(cr,uid,gene_ids[0],context=context)
                    ws.write(i,0,gene_no)
                    ws.write(i,1,gene_obj.package_id.name)
                    ws.write(i,2,gene_no+gene_obj.package_id.lib_code)
            w.save(xlsname+"_lib.xls")
            f=open(xlsname+"_lib.xls",'rb')
            id=self.pool.get('rhwl.gene.export.excel').create(cr,uid,{"file":base64.encodestring(f.read()),"name":u"样本编码转换结果.xls","state":"excel"})
            f.close()
            os.remove(xlsname+"_lib.xls")
            os.remove(xlsname+".xls")

            return {
                'type': 'ir.actions.act_window',
                'res_model': 'rhwl.gene.export.excel',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': id,
                'views': [(False, 'form')],
                'target': 'new',
                'name':u"实验编码转换"
            }
        finally:
            f.close()
            if os.path.exists(xlsname+'.xls'):os.remove(xlsname+'.xls')

    def import_report7(self, cr, uid, ids, context=None):
        """接收质检数据"""
        if context is None:
            context = {}
        this = self.browse(cr, uid, ids[0])

        fileobj = NamedTemporaryFile('w+',delete=True)
        xlsname =  fileobj.name
        f=open(xlsname+'.xls','wb')
        fileobj.close()
        try:
            #fileobj.write(base64.decodestring(this.file_bin.decode('base64')))
            b=this.file_bin2.decode('base64')
            f.write(b)
            f.close()

            try:
                bk = xlrd.open_workbook(xlsname+".xls")
                sh = bk.sheet_by_index(0)
            except:
               raise osv.except_osv(u"打开出错",u"请确认质检数据文件格式是否为正确的报告标准格式。")
            nrows = sh.nrows
            genes_ids=[]
            for i in range(2,nrows):
                no=sh.cell_value(i,1)
                if not no:continue
                if type(no)==type(1.0):no = no.__trunc__()
                id=self.pool.get("rhwl.easy.genes.new").search(cr,uid,[("name","=",no)],context=context)
                if not id:
                    raise osv.except_osv(u"错误",u"基因编号[%s]不存在."%(no,))
                if genes_ids.count(id[0])>0:
                    raise osv.except_osv(u"错误",u"基因编号[%s]在Excel中存在多笔。"%(no,))
                genes_ids.append(id[0])
                self.pool.get("rhwl.easy.genes.new").write(cr,uid,id,{"log":[[0,0,{"note":u"导入质检数据","data":"DNA"}]]},context=context)
                obj_ids = self.pool.get("rhwl.easy.genes.new.check").search(cr,uid,[("genes_id.name",'=',no)],context=context)
                if obj_ids:
                    self.pool.get("rhwl.easy.genes.new.check").write(cr,uid,obj_ids,{"active":False})
                t1=sh.cell_value(i,4)
                t2=sh.cell_value(i,5)
                t3=sh.cell_value(i,6)
                t4=sh.cell_value(i,8)
                if not t4:t4=0
                val={
                        "genes_id":id[0],
                        "date":self.date_trun(sh.cell_value(i,0)),
                        "dna_date":self.date_trun(sh.cell_value(i,2)),
                        "concentration":round(t1,2),
                        "lib_person":sh.cell_value(i,3),
                        "od260_280":round(t2,2),
                        "od260_230":round(t3,2),
                        "chk_person":sh.cell_value(i,7),
                        "data_loss":str(round(t4,4)*100)+"%",
                        "loss_person":sh.cell_value(i,9),
                        "loss_date":self.date_trun(sh.cell_value(i,10)),
                        "active":True,
                    }

                self.pool.get("rhwl.easy.genes.new.check").create(cr,uid,val,context=context)

                if (t4>0.01):
                    self.pool.get("rhwl.easy.genes.new").action_state_dna(cr,uid,id,context=context)
                else:
                    genes_obj = self.pool.get("rhwl.easy.genes.new").browse(cr,uid,id,context=context)
                    if genes_obj.state in ('except_confirm','confirm'):
                        self.pool.get("rhwl.easy.genes.new").action_state_dnaok(cr,uid,id,context=context)

        finally:
            f.close()
            os.remove(xlsname+'.xls')

        return

    def import_report11(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        this = self.browse(cr, uid, ids[0])
        is_second = this.is_second
        fileobj = NamedTemporaryFile('w+',delete=True)
        xlsname =  fileobj.name
        f=open(xlsname+'.xls','wb')
        fileobj.close()
        try:
            #fileobj.write(base64.decodestring(this.file_bin.decode('base64')))
            b=this.file_bin.decode('base64')
            f.write(b)
            f.close()

            try:
                bk = xlrd.open_workbook(xlsname+".xls")
                sh = bk.sheet_by_index(0)
            except:
               raise osv.except_osv(u"打开出错",u"请确认文件格式是否为正确的报告标准格式。")
            nrows = sh.nrows
            ncols = sh.ncols
            batch_no={}
            for i in range(1,nrows):
                no=sh.cell_value(i,0) #样本编号
                if not no:continue

                no = no.__trunc__().__str__() if isinstance(no,(long,int,float)) else no
                gene_id = self.pool.get("rhwl.easy.genes").search(cr,uid,[("name","=",no)])
                if not gene_id:
                    raise osv.except_osv(u"出错",u"找不到样本编号[%s]"%(no,))
                hole_no = sh.cell_value(i,2) #孔号
                hole_no = hole_no.__trunc__().__str__() if isinstance(hole_no,(long,int,float)) else hole_no
                if is_second:
                    second_note = sh.cell_value(i,5)
                    if (not second_note) or second_note not in (u"重提",u"样本已用完"):
                        raise osv.except_osv(u"出错",u"重提样本库存转入时，必须指定重提原因，并且重提原因只能是[重提]或[样本已用完]。")
                    if second_note==u"样本已用完":
                        line_id = self.pool.get("rhwl.gene.stock.dna.line").search(cr,uid,[("name","=",gene_id[0]),("is_first","=",True)])
                        if not line_id:
                            raise osv.except_osv(u"出错",u"样本编号[%s]没有首提的库存记录，不能转入重提库存记录。"%(no))
                        if sh.cell_value(i,4)==u"样本已用完":
                            self.pool.get("rhwl.gene.stock.dna.line").write(cr,uid,line_id,{"box_no":"","hole_no":"","note":u"样本已用完"},context=context)
                        else:
                            continue
                val={
                    "name":gene_id[0],
                    "box_no":sh.cell_value(i,1), #盒号
                    "hole_no": hole_no,
                    "user_name":sh.cell_value(i,3).encode("utf-8").replace(".","·").replace("▪","·"), #操作人
                    "note":sh.cell_value(i,4), #备注
                    "is_first":not is_second,
                }
                line_id =self.pool.get("rhwl.gene.stock.dna.line").search(cr,uid,[("name","=",gene_id[0]),("is_first","=",True)])
                if line_id:
                    self.pool.get("rhwl.gene.stock.dna.line").write(cr,uid,line_id,val,context=context)
                else:
                    self.pool.get("rhwl.gene.stock.dna.line").create(cr,uid,val,context=context)
        finally:
            f.close()
            os.remove(xlsname+'.xls')

    def import_report12(self, cr, uid, ids, context=None):
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

            try:
                bk = xlrd.open_workbook(xlsname+".xls")
                sh = bk.sheet_by_index(0)
            except:
               raise osv.except_osv(u"打开出错",u"请确认文件格式是否为正确的报告标准格式。")
            nrows = sh.nrows
            ncols = sh.ncols
            batch_no={}
            for i in range(1,nrows):
                no=sh.cell_value(i,0) #样本编号
                if not no:continue

                no = no.__trunc__().__str__() if isinstance(no,(long,int,float)) else no
                gene_id = self.pool.get("rhwl.easy.genes").search(cr,uid,[("name","=",no)])
                if not gene_id:
                    raise osv.except_osv(u"出错",u"找不到样本编号[%s]"%(no,))
                hole_no = sh.cell_value(i,2) #孔号
                hole_no = hole_no.__trunc__().__str__() if isinstance(hole_no,(long,int,float)) else hole_no

                val={
                    "name":gene_id[0],
                    "box_no":sh.cell_value(i,1), #盒号
                    "hole_no": hole_no,
                    "user_name":sh.cell_value(i,3).encode("utf-8").replace(".","·").replace("▪","·"), #操作人

                }
                line_id =self.pool.get("rhwl.gene.stock.dna.original").search(cr,uid,[("name","=",gene_id[0])])
                if line_id:
                    self.pool.get("rhwl.gene.stock.dna.original").write(cr,uid,line_id,val,context=context)
                else:
                    self.pool.get("rhwl.gene.stock.dna.original").create(cr,uid,val,context=context)
        finally:
            f.close()
            os.remove(xlsname+'.xls')
