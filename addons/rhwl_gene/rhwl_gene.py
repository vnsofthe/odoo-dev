# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID, api
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import datetime,time
import logging
import os
import shutil
from openerp import tools

_logger = logging.getLogger(__name__)

class rhwl_gene(osv.osv):
    STATE_SELECT = {
        'draft': u'草稿',
        'except': u'信息异常',
        'except_confirm': u'异常确认',
        'confirm': u'信息确认',
        'dna_except': u'DNA质检不合格',
        'dna_ok':u"DNA质检合格",
        'cancel': u'取消',
        'ok': u'检测完成',
        'report': u'生成报告中',
        'report_done': u"报告已生成",
        "result_done": u"风险报告确认",
        "deliver": u"已出货",
        'done': u'完成'
    }
    _name = "rhwl.easy.genes"
    _order = "date desc,name asc"

    def _genes_type_get(self, cr, uid, ids, field_names, arg, context=None):
        res = {}
        maps = {}
        for id in ids:
            res[id] = {}.fromkeys(field_names, "")
            type_ids = self.pool.get("rhwl.easy.genes.type").search(cr, uid, [("genes_id.id", '=', id)],
                                                                    context=context)
            for i in self.pool.get("rhwl.easy.genes.type").browse(cr, uid, type_ids, context=context):
                res[id][maps.get(i.snp, i.snp)] = i.typ
        return res

    def _get_risk_detail(self,cr,uid,ids,field_names,arg,context=None):
        res={}
        for id in ids:
            res[id] = {}.fromkeys(field_names,"")
            obj = self.pool.get("rhwl.easy.genes").browse(cr,uid,id,context=context)
            for o in obj.risk:
                res[id][o.disease_id.code]=o.risk
        return res


    def _get_risk(self,cr,uid,ids,field_names,arg,context=None):
        res={}
        for id in ids:
            res[id]={"risk_count":0,"risk_text":""}
            risk_id = self.pool.get("rhwl.easy.gene.risk").search(cr,uid,[("genes_id.id","=",id),'|',("risk","=","高风险"),("risk","=","低能力")])
            res[id]["risk_count"]=risk_id.__len__()

            t=[]
            for i in self.pool.get("rhwl.easy.gene.risk").browse(cr,uid,risk_id,context=context):
                t.append(i.disease_id.name)
            res[id]["risk_text"]=u"、".join(t)

        return res


    _columns = {
        "batch_no": fields.char(u"批次",select=True),
        "name": fields.char(u"基因样本编号", required=True, size=10),
        "date": fields.date(u"送检日期", required=True),
        "cust_name": fields.char(u"会员姓名", required=True, size=10),
        "sex": fields.selection([('T', u"男"), ('F', u"女")], u"性别", required=True),
        "identity": fields.char(u"身份证号", size=18),
        "mobile": fields.char(u"手机号码", size=15),
        "birthday": fields.date(u"出生日期"),
        "receiv_date": fields.datetime(u"接收时间"),
        "except_note": fields.text(u"信息异常内容"),
        "confirm_note": fields.text(u"信息异常反馈"),
        "state": fields.selection(STATE_SELECT.items(), u"状态"),
        "note": fields.text(u"备注"),
        "gene_id": fields.char(u"基因编号", size=20),
        "cust_prop": fields.selection([("tjs", u"泰济生普通客户"), ("tjs_vip",u"泰济生VIP客户"),("employee", u"内部员工"), ("vip", u"内部VIP客户"), ("extra", u"外部人员")],
                                      string=u"客户属性"),
        "img": fields.binary(u"图片"),
        "img_atta":fields.many2one("ir.attachment","IMG"),
        "img_new":fields.related("img_atta","datas",type="binary"),
        "log": fields.one2many("rhwl.easy.genes.log", "genes_id", "Log"),
        "typ": fields.one2many("rhwl.easy.genes.type", "genes_id", "Type"),
        "dns_chk": fields.one2many("rhwl.easy.genes.check", "genes_id", "DNA_Check"),
        "risk": fields.one2many("rhwl.easy.gene.risk", "genes_id", "Risk"),
        "pdf_file": fields.char(u"风险报告", size=100),
        "is_risk":fields.boolean(u"是高风险"),
        "is_child":fields.boolean(u"是儿童"),
        "risk_count": fields.function(_get_risk, type="integer", string=u'高风险疾病数', multi='risk'),
        "risk_text": fields.function(_get_risk, type="char", string=u'高风险疾病', multi='risk'),
        "A1":fields.function(_get_risk_detail,type="char",string="A1",multi="risk_detail"),
        "A2":fields.function(_get_risk_detail,type="char",string="A2",multi="risk_detail"),
        "A3":fields.function(_get_risk_detail,type="char",string="A3",multi="risk_detail"),
        "A4":fields.function(_get_risk_detail,type="char",string="A4",multi="risk_detail"),
        "A5":fields.function(_get_risk_detail,type="char",string="A5",multi="risk_detail"),
        "A6":fields.function(_get_risk_detail,type="char",string="A6",multi="risk_detail"),
        "A7":fields.function(_get_risk_detail,type="char",string="A7",multi="risk_detail"),
        "A8":fields.function(_get_risk_detail,type="char",string="A8",multi="risk_detail"),
        "A9":fields.function(_get_risk_detail,type="char",string="A9",multi="risk_detail"),
        "A10":fields.function(_get_risk_detail,type="char",string="A10",multi="risk_detail"),
        "A11":fields.function(_get_risk_detail,type="char",string="A11",multi="risk_detail"),
        "A12":fields.function(_get_risk_detail,type="char",string="A12",multi="risk_detail"),
        "A13":fields.function(_get_risk_detail,type="char",string="A13",multi="risk_detail"),
        "A14":fields.function(_get_risk_detail,type="char",string="A14",multi="risk_detail"),
        "A15":fields.function(_get_risk_detail,type="char",string="A15",multi="risk_detail"),
        "A16":fields.function(_get_risk_detail,type="char",string="A16",multi="risk_detail"),
        "A17":fields.function(_get_risk_detail,type="char",string="A17",multi="risk_detail"),
        "A18":fields.function(_get_risk_detail,type="char",string="A18",multi="risk_detail"),
        "A19":fields.function(_get_risk_detail,type="char",string="A19",multi="risk_detail"),
        "A20":fields.function(_get_risk_detail,type="char",string="A20",multi="risk_detail"),
        "A21":fields.function(_get_risk_detail,type="char",string="A21",multi="risk_detail"),
        "A22":fields.function(_get_risk_detail,type="char",string="A22",multi="risk_detail"),
        "A23":fields.function(_get_risk_detail,type="char",string="A23",multi="risk_detail"),
        "B1":fields.function(_get_risk_detail,type="char",string="B1",multi="risk_detail"),
        "B2":fields.function(_get_risk_detail,type="char",string="B2",multi="risk_detail"),
        "B3":fields.function(_get_risk_detail,type="char",string="B3",multi="risk_detail"),
        "B4":fields.function(_get_risk_detail,type="char",string="B4",multi="risk_detail"),
        "B5":fields.function(_get_risk_detail,type="char",string="B5",multi="risk_detail"),
        "B6":fields.function(_get_risk_detail,type="char",string="B6",multi="risk_detail"),
        "B7":fields.function(_get_risk_detail,type="char",string="B7",multi="risk_detail"),
        "B8":fields.function(_get_risk_detail,type="char",string="B8",multi="risk_detail"),
        "B9":fields.function(_get_risk_detail,type="char",string="B9",multi="risk_detail"),
        "B10":fields.function(_get_risk_detail,type="char",string="B10",multi="risk_detail"),
        "B11":fields.function(_get_risk_detail,type="char",string="B11",multi="risk_detail"),
        "B12":fields.function(_get_risk_detail,type="char",string="B12",multi="risk_detail"),
        "B13":fields.function(_get_risk_detail,type="char",string="B13",multi="risk_detail"),
        "B14":fields.function(_get_risk_detail,type="char",string="B14",multi="risk_detail"),
        "B15":fields.function(_get_risk_detail,type="char",string="B15",multi="risk_detail"),
        "B16":fields.function(_get_risk_detail,type="char",string="B16",multi="risk_detail"),
        "C1":fields.function(_get_risk_detail,type="char",string="C1",multi="risk_detail"),
        "C2":fields.function(_get_risk_detail,type="char",string="C2",multi="risk_detail"),
        "C3":fields.function(_get_risk_detail,type="char",string="C3",multi="risk_detail"),
        "C4":fields.function(_get_risk_detail,type="char",string="C4",multi="risk_detail"),
        "C5":fields.function(_get_risk_detail,type="char",string="C5",multi="risk_detail"),
        "C6":fields.function(_get_risk_detail,type="char",string="C6",multi="risk_detail"),
        "C7":fields.function(_get_risk_detail,type="char",string="C7",multi="risk_detail"),
        "C8":fields.function(_get_risk_detail,type="char",string="C8",multi="risk_detail"),
        "C9":fields.function(_get_risk_detail,type="char",string="C9",multi="risk_detail"),
        "C10":fields.function(_get_risk_detail,type="char",string="C10",multi="risk_detail"),
        "C11":fields.function(_get_risk_detail,type="char",string="C11",multi="risk_detail"),
        "C12":fields.function(_get_risk_detail,type="char",string="C12",multi="risk_detail"),
        "D1":fields.function(_get_risk_detail,type="char",string="D1",multi="risk_detail"),
        "D2":fields.function(_get_risk_detail,type="char",string="D2",multi="risk_detail"),
        "D3":fields.function(_get_risk_detail,type="char",string="D3",multi="risk_detail"),
        "D4":fields.function(_get_risk_detail,type="char",string="D4",multi="risk_detail"),
        "D5":fields.function(_get_risk_detail,type="char",string="D5",multi="risk_detail"),
        "D6":fields.function(_get_risk_detail,type="char",string="D6",multi="risk_detail"),
        "D7":fields.function(_get_risk_detail,type="char",string="D7",multi="risk_detail"),
        "D8":fields.function(_get_risk_detail,type="char",string="D8",multi="risk_detail"),
        "D9":fields.function(_get_risk_detail,type="char",string="D9",multi="risk_detail"),
        "D10":fields.function(_get_risk_detail,type="char",string="D10",multi="risk_detail"),
        "D11":fields.function(_get_risk_detail,type="char",string="D11",multi="risk_detail"),
        "D12":fields.function(_get_risk_detail,type="char",string="D12",multi="risk_detail"),
		"D13":fields.function(_get_risk_detail,type="char",string="D13",multi="risk_detail"),
        "D14":fields.function(_get_risk_detail,type="char",string="D14",multi="risk_detail"),
        "E1":fields.function(_get_risk_detail,type="char",string="E1",multi="risk_detail"),
        "E2":fields.function(_get_risk_detail,type="char",string="E2",multi="risk_detail"),
        "E3":fields.function(_get_risk_detail,type="char",string="E3",multi="risk_detail"),
        "F1":fields.function(_get_risk_detail,type="char",string="F1",multi="risk_detail"),
        "F2":fields.function(_get_risk_detail,type="char",string="F2",multi="risk_detail"),
    }
    _sql_constraints = [
        ('rhwl_easy_genes_name_uniq', 'unique(name)', u'样本编号不能重复!'),
    ]
    _defaults = {
        "state": 'draft',
        "cust_prop": "tjs",
        "is_risk":False,
        "is_child":False,
    }

    def init(self, cr):
        ids = self.search(cr,SUPERUSER_ID,[("img","!=",False),("img_atta","=",False)])
        for i in ids:
            obj = self.browse(cr,SUPERUSER_ID,i)
            val={
                "name":obj.name,
                "datas_fname":obj.name+".jpg",
                "description":obj.name+" information to IMG",
                "res_model":"rhwl.easy.genes",
                "res_id":obj.id,
                "create_date":fields.datetime.now,
                "create_uid":SUPERUSER_ID,
                "datas":obj.img,
            }
            atta_id = self.pool.get('ir.attachment').create(cr,SUPERUSER_ID,val)
            self.write(cr,SUPERUSER_ID,obj.id,{"img_atta":atta_id})

        ids = self.search(cr,SUPERUSER_ID,[("birthday","=",False)])
        for i in ids:
            obj = self.browse(cr,SUPERUSER_ID,i)
            if obj.identity and len(obj.identity)==18:
                try:
                    d=datetime.datetime.strptime(obj.identity[6:14],"%Y%m%d").strftime("%Y/%m/%d")
                    self.write(cr,SUPERUSER_ID,i,{"birthday":d})
                except:
                    pass

    def create(self, cr, uid, val, context=None):
        val["log"] = [[0, 0, {"note": u"资料新增", "data": "create"}]]
        if not val.get("batch_no",None):
            val["batch_no"]=datetime.datetime.strftime(datetime.datetime.today(),"%m-%d")
        return super(rhwl_gene, self).create(cr, uid, val, context=context)

    def write(self, cr, uid, id, val, context=None):
        if not context:
            context={}
        if val.has_key("state"):
            val["log"] = [
                [0, 0, {"note": u"状态变更为:" + self.STATE_SELECT.get(val.get("state")), "data": val.get("state"),"user_id":context.get("user_id",uid)}]]
        if val.has_key("img"):
            val["log"] = [[0, 0, {"note": u"图片变更", "data": "img"}]]
            obj = self.browse(cr,SUPERUSER_ID,id,context=context)
            vals={
                "name":obj.name,
                "datas_fname":obj.name+".jpg",
                "description":obj.name+" information to IMG",
                "res_model":"rhwl.easy.genes",
                "res_id":obj.id,
                "create_date":fields.datetime.now,
                "create_uid":SUPERUSER_ID,
                "datas":val.get("img"),
            }
            if obj.img_atta:
                self.pool.get('ir.attachment').unlink(cr,SUPERUSER_ID,obj.img_atta.id)
            atta_id = self.pool.get('ir.attachment').create(cr,SUPERUSER_ID,vals)
            val["img_atta"]=atta_id
            val.pop("img")

        return super(rhwl_gene, self).write(cr, uid, id, val, context=context)

    def unlink(self, cr, uid, ids, context=None):
        if isinstance(ids, (long, int)):
            ids = [ids]
        if uid != SUPERUSER_ID: ids = self.search(cr, uid, [("id", "in", ids), ("state", "=", "draft")],
                                                  context=context)
        return super(rhwl_gene, self).unlink(cr, uid, ids, context=context)

    def action_state_except(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        if context.get("view_type") == "tree":
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'res_model': 'rhwl.easy.genes.popup',
                'view_mode': 'form',
                'name': u"异常说明",
                'target': 'new',
                'context': {'col': 'except_note'},
                'flags': {'form': {'action_buttons': False}}}

        return self.write(cr, uid, ids, {"state": "except"})

    def action_state_except_confirm(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        if context.get("view_type") == "tree":
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'res_model': 'rhwl.easy.genes.popup',
                'view_mode': 'form',
                'name': u"回馈说明",
                'target': 'new',
                'context': {'col': 'confirm_note'},
                'flags': {'form': {'action_buttons': False}}}

        return self.write(cr, uid, ids, {"state": "except_confirm"})


    def action_state_confirm(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {"state": "confirm"})

    def action_state_cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {"state": "cancel"})

    def action_state_dna(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {"state": "dna_except"})

    def action_state_dnaok(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {"state": "dna_ok"})

    def action_state_ok(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {"state": "ok"})

    def action_state_reset(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {"state": "draft"})

    def action_state_report(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {"state": "report"})

    def action_state_result_done(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {"state": "result_done"})

    def action_view_pdf(self, cr, uid, ids, context=None):
        return {'type': 'ir.actions.act_url',
                'url': context.get("file_name", "/"),
                'target': 'new'}

    #取得指定id列表的所有位点数据
    def get_gene_type_list(self,cr,uid,ids,context=None):
        data={}
        for i in self.browse(cr,uid,ids,context=context):
            key = i.name.encode("utf-8")
            if not data.has_key(key):
                data[key]={"name":key,
                           "cust_name":i.cust_name.encode("utf-8").replace(" ",""),
                           "sex":i.sex.encode("utf-8") if i.sex.encode("utf-8") == 'F' else 'M'}

            for t in i.typ:
                k = t.snp.encode("utf-8")
                data[key][k]=(t.typ).encode("utf-8").replace("/","")

        return data

    #导出样本信息图片
    def export_genes_img(self,cr,uid,context=None):
        upload_path = os.path.join(os.path.split(__file__)[0], "static/local/upload")
        d=os.path.join(upload_path,u"样本信息图片")
        if not os.path.exists(d):
            os.mkdir(d)
        all_ids = self.search(cr,uid,[("cust_prop","in",["tjs","tjs_vip"])],context=context)
        pic_ids = self.search(cr,uid,[("cust_prop","in",["tjs","tjs_vip"]),("log.data","=","expimg")],context=context)
        for i in pic_ids:
            all_ids.remove(i)
        filestore=tools.config.filestore(cr.dbname)
        for i in self.browse(cr,uid,all_ids,context=context):
            if not i.img_atta:continue
            if len(i.date.split("/"))>1:
                tname = ".".join(i.date.split('/')[1:]) + u"会_图片"
            else:
                tname = ".".join(i.date.split('-')[1:]) + u"会_图片"
            tname = os.path.join(d,tname)
            if not os.path.exists(tname):
                os.mkdir(tname)
            att_obj = self.pool.get('ir.attachment').browse(cr,uid,i.img_atta.id,context=context)
            if (not os.path.exists(os.path.join(tname,i.name+u"_"+i.cust_name+u".jpg"))) or os.stat(os.path.join(filestore,att_obj.store_fname)).st_size != os.stat(os.path.join(tname,i.name+u"_"+i.cust_name+u".jpg")).st_size:
                shutil.copy(os.path.join(filestore,att_obj.store_fname),os.path.join(tname,i.name+u"_"+i.cust_name+u".jpg"))
            self.write(cr,uid,i.id,{"log":[[0,0,{"note":u"图片导出","data":"expimg"}]]})

    #导出样本位点数据到报告生成服务器
    def create_gene_type_file(self, cr, uid, ids, context=None):
        self.pool.get("rhwl.genes.picking").export_box_genes(cr,uid,context=context) #先导出已经分箱的样本
        self.export_genes_img(cr,uid,context=context) #导出图片信息
        ids = self.search(cr, uid, [("state", "=", "ok"),("typ","!=",False)], context=context)
        if not ids:return

        if isinstance(ids, (long, int)):
            ids = [ids]
        data = self.get_gene_type_list(cr,uid,ids,context=context)

        fpath = os.path.join(os.path.split(__file__)[0], "static/remote/snp")
        fname = os.path.join(fpath, "snp_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ".txt")
        header=[]
        f = open(fname, "w+")
        for k in data.keys():
            line_row=[data[k]["name"],data[k]["cust_name"],data[k]["sex"]]
            if not header:
                header = data[k].keys()
                header.remove("name")
                header.remove("cust_name")
                header.remove("sex")
                header.sort()
                f.write("编号\t姓名\t性别\t" + "\t".join(header) + '\n')
            for i in header:
                line_row.append(data[k][i])
            f.write("\t".join(line_row) + '\n')
        f.close()
        self.action_state_report(cr, uid, ids, context=context)
        js={
            "first":"易感样本检测结果转报告生成：",
            "keyword1":"即时",
            "keyword2":"本次转出样本%s笔，等待生成报告。" %(len(ids),),
            "keyword3":fields.datetime.now(),
            "remark":"以上数据仅供参考，详细情况请登录Odoo查询。"
        }
        self.pool.get("rhwl.weixin.base").send_template2(cr,uid,js,"is_jobmanager",context=context)

    def pdf_error(self,cr,uid,file,context=None):
        js={
            "first":"易感样本报告接收出错：",
            "keyword1":"即时",
            "keyword2":"样本报告%s文件大小不正确。" %(file,),
            "keyword3":fields.datetime.now(),
            "remark":"以上数据仅供参考，详细情况请登录服务器查询。"
        }
        self.pool.get("rhwl.weixin.base").send_template2(cr,uid,js,"is_jobmanager",context=context)

    #接收风险报告
    def get_gene_pdf_file(self, cr, uid, context=None):
        #_logger.warn("cron job get_gene_pdf_file")
        model_path=os.path.split(__file__)[0]
        fpath = os.path.join(model_path, "static/remote/report")
        tpath = os.path.join(model_path, "static/local/report")
        pdf_count = 0
        last_week = time.time() - 60*60*24*3
        for f in os.listdir(fpath):
            newfile = os.path.join(fpath, f)
            if os.path.isdir(newfile):
                for f1 in os.listdir(newfile):
                    f2 = f1.split("_")[0] + ".pdf"
                    s=os.stat(os.path.join(newfile, f1)).st_size
                    if s/1024/1024<16 or s/1024/1024>20:
                        self.pdf_error(cr,uid,f1,context=context)
                        continue

                    shutil.move(os.path.join(newfile, f1), os.path.join(tpath, f2))
                    ids = self.search(cr, uid, [("name", "=", f2.split(".")[0])])
                    if ids:
                        self.write(cr, uid, ids,
                                   {"pdf_file": "rhwl_gene/static/local/report/" + f2, "state": "report_done"})
                        pdf_count += 1

                if os.path.getmtime(newfile) < last_week:
                    os.rmdir(newfile)
        cr.commit()
        if pdf_count>0:
            js={
                "first":"易感样本报告接收：",
                "keyword1":"即时",
                "keyword2":"本次接收样本报告%s本。" %(pdf_count,),
                "keyword3":fields.datetime.now(),
                "remark":"以上数据仅供参考，详细情况请登录Odoo查询。"
            }
            self.pool.get("rhwl.weixin.base").send_template2(cr,uid,js,"is_jobmanager",context=context)

        #分析风险数据
        fpath = os.path.join(model_path, "static/remote/excel")
        tpath = os.path.join(model_path, "static/local/excel")
        for f in os.listdir(fpath):
            if f.split(".")[-1]!="xls":continue
            if f.split("_")[0]=="box":continue
            if os.path.isfile(os.path.join(tpath, f)):os.remove(os.path.join(tpath, f)) #删除目标位置相同的文件
            shutil.move(os.path.join(fpath, f), os.path.join(tpath, f))
            fs = open(os.path.join(tpath, f),"r")
            res = fs.readlines()
            fs.close()
            risk = res[0].replace("\n","").split("\t")[3:]
            disease = self.pool.get("rhwl.gene.disease")
            disease_dict={} #疾病在表中的id
            dict_index=3
            #检查风险报告中的疾病基本数据
            for r in risk:
                if not r:continue
                r_id = disease.search(cr,uid,[("name","=",r.decode("utf-8"))])
                if not r_id:
                    shutil.move(os.path.join(tpath, f),os.path.join(fpath, f))
                    _logger.warn(u"疾病名称[%s]在基本数据中不存在。" %(r.decode("utf-8"),))
                    return
                disease_dict[dict_index]=[r,r_id[0]]
                dict_index +=1

            for l in res[1:]:
                is_risk=False
                l = l.replace("\n","").split("\t")
                gene_id = self.pool.get("rhwl.easy.genes").search(cr,uid,[("name","=",l[0].decode("utf-8"))])
                if not gene_id:
                    _logger.warn(u"样本编号[%s]在基本数据中不存在。" %(l[0].decode("utf-8"),))
                else:
                    risk_id=self.pool.get("rhwl.easy.gene.risk").search(cr,uid,[("genes_id","in",gene_id)])
                    if risk_id:
                        self.pool.get("rhwl.easy.gene.risk").write(cr,uid,risk_id,{"active":False})
                    val=[]
                    for k in disease_dict.keys():
                        val.append([0, 0, {"disease_id": disease_dict[k][1], "risk": l[k]}])
                        if l[k]=="高风险" or l[k]=="低能力":is_risk=True
                    self.pool.get("rhwl.easy.genes").write(cr,uid,gene_id,{"is_risk":is_risk,"risk":val})
        self.pool.get("rhwl.genes.picking").create_box(cr,uid,context=context) #接收完风险数据以后，重新调用分箱

    #样本状态数据微信通知
    def weixin_notice_template2(self,cr,uid,context=None):
        today = datetime.datetime.today()
        if today.day<=20:
            s_date = today-datetime.timedelta(days=today.day+1)
            s_date = datetime.datetime(s_date.year,s_date.month,21)
            e_date = today
        else:
            s_date = datetime.datetime(today.year,today.month,21)
            e_date = today

        ids = self.search(cr,uid,[("date",">=",s_date),("date","<=",e_date)],context=context)
        v_count0=0
        v_count1=0
        v_count2=0
        v_count3=0
        v_count4=0
        v_count5 = 0
        for i in self.browse(cr,uid,ids,context=context):
            if i.state=='draft':
                v_count0 += 1 #待收件
            elif i.state in ['except','except_confirm','confirm']:
                v_count1 += 1 #待检测
            elif i.state in ['dna_ok','ok','report']:
                v_count2 += 1 #待生成报告
            elif i.state == 'dna_except':
                v_count3 += 1 #质检异常
            elif i.state in ['report_done',"result_done","deliver",]:
                v_count4 += 1 #待送货
            elif i.state in ['done']:
                v_count5 += 1 #已完成
        js={
            "first":"易感样本状况统计：",
            "keyword1":"本期从(%s-%s)"%(s_date.strftime("%Y/%m/%d"),e_date.strftime("%Y/%m/%d")),
            "keyword2":"待收件%s笔，待检测%s笔，等待报告产生%s笔，已出报告%s笔(质检不合格%s笔)，待送货%s笔，已完成%s笔。总计%s笔。" %(v_count0,v_count1,v_count2,v_count4+v_count3+v_count5,v_count3,v_count4,v_count5,len(ids)),
            "keyword3":(datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime("%Y/%m/%d %H:%M:%S"),
            "remark":"以上数据仅供参考，详细情况请登录Odoo查询。"
        }
        self.pool.get("rhwl.weixin.base").send_template2(cr,uid,js,"is_notice",context=context)

#样本对象操作日志
class rhwl_gene_log(osv.osv):
    _name = "rhwl.easy.genes.log"
    _order = "date desc"
    _columns = {
        "genes_id": fields.many2one("rhwl.easy.genes", "Genes ID"),
        "date": fields.datetime(u"时间"),
        "user_id": fields.many2one("res.users", u"操作人员"),
        "note": fields.text(u"作业说明"),
        "data": fields.char("Data")
    }

    _defaults = {
        "date": fields.datetime.now,
        "user_id": lambda obj, cr, uid, context: uid,
    }

#疾病检测结果对象
class rhwl_gene_check(osv.osv):
    _name = "rhwl.easy.genes.check"
    _columns = {
        "genes_id": fields.many2one("rhwl.easy.genes", "Genes ID"),
        "date": fields.date(u"收样日期"),
        "dna_date": fields.date(u"提取日期"),
        "concentration": fields.char(u"浓度", size=5, help=u"参考值>=10"),
        "lib_person": fields.char(u"实验操作人", size=10),
        "od260_280": fields.char("OD260/OD280", size=5, help=u"参考值1.8-2.0"),
        "od260_230": fields.char("OD260/OD230", size=5, help=u"参考值>=2.0"),
        "chk_person": fields.char(u"检测人", size=10),
        "data_loss": fields.char(u"数据缺失率", size=6, help=u"参考值<1%"),
        "loss_person": fields.char(u"判读人", size=10),
        "loss_date": fields.date(u"判读日期"),
        "active": fields.boolean("Active"),
    }

    _defaults = {
        "active": True
    }

#疾病位点数据对象
class rhwl_gene_type(osv.osv):
    _name = "rhwl.easy.genes.type"
    _columns = {
        "genes_id": fields.many2one("rhwl.easy.genes", "Genes ID"),
        "snp": fields.char("SNP", size=20),
        "typ": fields.char("Type", size=10),
        "active": fields.boolean("Active"),
    }
    _defaults = {
        "active": True
    }

#疾病风险对象
class rhwl_gene_risk(osv.osv):
    _name = "rhwl.easy.gene.risk"
    _columns = {
        "genes_id": fields.many2one("rhwl.easy.genes", "Genes ID"),
        "disease_id": fields.many2one("rhwl.gene.disease", string=u"疾病名"),
        "risk": fields.char(u"风险", size=20),
        "active": fields.boolean("Active"),
    }
    _defaults = {
        "active": True
    }

#疾病分类对象
class rhwl_gene_disease_type(osv.osv):
    _name = "rhwl.gene.disease.type"
    _columns = {
        "name": fields.char(u"分类名称", size=100),
        "line": fields.one2many("rhwl.gene.disease", "type_id", string=u"疾病名称")
    }

#疾病明细对象
class rhwl_gene_disease(osv.osv):
    _name = "rhwl.gene.disease"
    _columns = {
        "name": fields.char(u"疾病名称", size=50),
        "type_id": fields.many2one("rhwl.gene.disease.type", string=u"分类名称"),
        "code":fields.char("Code",size=5),
    }


class rhwl_gene_popup(osv.osv_memory):
    _name = "rhwl.easy.genes.popup"
    _columns = {
        "note": fields.text(u"说明")
    }

    def action_ok(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids, context)
        s = {
            "confirm_note": "except_confirm",
            "except_note": "except"
        }
        col = context.get('col')
        if not context:
            context={}
        context["user_id"]=uid
        self.pool.get("rhwl.easy.genes").write(cr, SUPERUSER_ID, context.get("active_id", 0),
                                               {col: obj.note, "state": s.get(col)},context=context)
