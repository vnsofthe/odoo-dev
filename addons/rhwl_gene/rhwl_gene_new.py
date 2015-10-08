# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID, api
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import datetime,time
import logging
import os
import shutil
import re
from openerp import tools
from lxml import etree
_logger = logging.getLogger(__name__)
REMOTE_SNP_PATH="static/remote/yg/snp"
REMOTE_REPORT_PATH="static/remote/yg/report"
LOCAL_REPORT_PATH="static/local/report/yg"
class rhwl_gene(osv.osv):
    STATE_SELECT_LIST=[
        ('draft', u'草稿'),
        ('cancel', u'检测取消'),
        ('except', u'信息异常'),
        ('except_confirm', u'异常已确认'),
        ('confirm', u'信息已确认'),
        ('dna_except', u'DNA质检不合格'),
        ('dna_ok',u"DNA质检合格"),
        ('ok', u'位点数据已导入'),
        ('report', u'生成报告中'),
        ('report_done', u"报告已生成"),
        ("result_done", u"风险报告确认"),
        ("deliver", u"印刷厂已接收"),
        ('done', u'客户已收货')
    ]
    STATE_SELECT = dict(STATE_SELECT_LIST)

    _name = "rhwl.easy.genes.new"
    _order = "date desc,name asc"

    def _genes_type_get(self, cr, uid, ids, field_names, arg, context=None):
        res = {}
        maps = {}
        for id in ids:
            res[id] = {}.fromkeys(field_names, "")
            type_ids = self.pool.get("rhwl.easy.genes.new.type").search(cr, uid, [("genes_id.id", '=', id)],
                                                                    context=context)
            for i in self.pool.get("rhwl.easy.genes.new.type").browse(cr, uid, type_ids, context=context):
                res[id][maps.get(i.snp, i.snp)] = i.typ
        return res


    _columns = {
        "batch_no": fields.char(u"批次",select=True,help=u"实验位点导入时会自动产生。"),
        "name": fields.char(u"基因样本编号", required=True, size=10),
        "date": fields.date(u"送检日期", required=True),
        "cust_name": fields.char(u"会员姓名", required=True, size=50),
        "name_pinying":fields.char(u"姓名(拼音)",size=20),
        "sex": fields.selection([('M', u"男"), ('F', u"女")], u"性别", required=True),
        "height":fields.integer(u"身高cm"),
        "width":fields.float(u"体重kg"),
        "mingzhu":fields.char(u"民族",size=20),
        "identity": fields.char(u"身份证号", size=18),
        "mobile": fields.char(u"手机号码", size=15),
        "contact":fields.char(u"紧急联系人",size=20),
        "contact_tel":fields.char(u"联系人电话",size=20),
        "Permanent_city":fields.char(u"常住城市",size=20),
        "state_id": fields.many2one("res.country.state",string=u'省'),
        "city_id": fields.many2one("res.country.state.city",string=u'市',domain="[('state_id','=',state_id)]"),
        "area_id":fields.many2one("res.country.state.city.area",string=u"区/县",domain="[('city_id','=',city_id)]"),
        "address":fields.char(u"详细地址",size=100),
        "email":fields.char(u"电子邮箱",size=50),
        "weixin":fields.char(u"微信号",size=20),
        "hospital":fields.many2one('res.partner', string=u'送检机构',domain="[('is_company', '=', True), ('customer', '=', True)]", required=True),
        "birthday": fields.date(u"出生日期"),
        "receiv_date": fields.datetime(u"接收时间"),
        "is_reuse":fields.boolean(u"重采"),
        "is_single_post":fields.boolean(u"单独邮寄"),
        "is_free":fields.boolean(u"免费"),
        "urgency":fields.selection([("0",u"正常"),("1",u"加急")],u"紧急程度"),
        "has_sms":fields.boolean(u"短信已通知",readonly=True),
        "hospital_seq":fields.char(u"档案流水号",size=20,readonly=True),
        "has_invoice":fields.boolean(u"是否开发票"),
        "except_note": fields.text(u"信息异常内容"),
        "confirm_note": fields.text(u"信息异常反馈"),
        "except_type":fields.selection([('custom',u"客户填写不清楚"),("employee",u"录入错误")],u"异常原因"),
        "cust_prop":fields.selection([("hospital",u"医院"),("insurance",u"保险"),("internal",u"内部员工"),("custom",u"公司客户"),("other",u"其它")],string=u"客户属性",required=True),
        "prop_note":fields.char(u"其它说明",size=20),
        "package_id":fields.many2one("rhwl.genes.base.package",string="套餐", required=True,ondelete="restrict"),
        "state": fields.selection(STATE_SELECT_LIST, u"状态"),
        "note": fields.text(u"备注"),
        "img_atta":fields.many2one("ir.attachment","IMG"),
        "img_new":fields.related("img_atta","datas",type="binary"),
        "log": fields.one2many("rhwl.easy.genes.new.log", "genes_id", "Log"),
        "typ": fields.one2many("rhwl.easy.genes.new.type", "genes_id", "Type"),
        "dns_chk": fields.one2many("rhwl.easy.genes.new.check", "genes_id", "DNA_Check"),
        "export_img":fields.boolean("Export Img"),
        "pdf_file": fields.char(u"检测报告", size=100),
        "q1_0":fields.boolean(u"无"),
        "q1_1":fields.boolean(u"肿瘤"),
        "q1_2":fields.boolean(u"糖尿病"),
        "q1_3":fields.boolean(u"呼吸性疾病"),
        "q1_4":fields.boolean(u"心脑血管疾病"),
        "q1_5":fields.boolean(u"消化道溃疡"),
        "q1_6":fields.boolean(u"妇科病"),
        "q1_7":fields.boolean(u"过敏史"),
        "q2_0":fields.boolean(u"无"),
        "q2_1":fields.boolean(u"有"),
        "q2_2":fields.char(u"说明",size=20),
        "q3_0":fields.boolean(u"无"),
        "q3_1":fields.boolean(u"抗感染药"),
        "q3_2":fields.boolean(u"抗神经精神类药"),
        "q3_3":fields.boolean(u"抗心血管疾病药"),
        "q3_4":fields.boolean(u"抗肿瘤药物"),
        "q3_5":fields.boolean(u"激素类药"),
        "q3_6":fields.boolean(u"抗代谢及免疫抑制类药"),
        "q4_0":fields.boolean(u"无"),
        "q4_1":fields.boolean(u"吸烟"),
        "q4_2":fields.boolean(u"酗酒"),
        "q4_3":fields.boolean(u"常年服药"),
        "q4_4":fields.boolean(u"常年规律运动"),
        "q4_5":fields.boolean(u"经常群体社交活动"),
        "q5_0":fields.boolean(u"无"),
        "q5_1":fields.boolean(u"消化不良"),
        "q5_2":fields.boolean(u"经常便秘"),
        "q5_3":fields.boolean(u"偶尔有腹泻"),
        "q5_4":fields.boolean(u"胃痛"),
        "q5_5":fields.boolean(u"胸前灼烧感"),
        "q6_0":fields.boolean(u"无"),
        "q6_1":fields.boolean(u"失眠"),
        "q6_2":fields.boolean(u"偶尔头痛"),
        "q6_3":fields.boolean(u"记忆力下降"),
        "q6_4":fields.boolean(u"注意力不集中"),
        "q6_5":fields.boolean(u"耳聋耳鸣"),
        "q7_0":fields.boolean(u"无"),
        "q7_1":fields.boolean(u"头晕"),
        "q7_2":fields.boolean(u"手脚冰凉"),
        "q7_3":fields.boolean(u"低血压"),
        "q7_4":fields.boolean(u"高血压"),
        "q8_0":fields.boolean(u"无"),
        "q8_1":fields.boolean(u"肌肉关节痛"),
        "q8_2":fields.boolean(u"腰背痛"),
        "q8_3":fields.boolean(u"关节伸、缩、旋转等受限"),
        "q8_4":fields.boolean(u"关节变形"),
        "q9_0":fields.boolean(u"无"),
        "q9_1":fields.boolean(u"皮肤易过敏"),
        "q9_2":fields.boolean(u"易患感冒"),
        "q9_3":fields.boolean(u"双颊红斑"),
        "q9_4":fields.boolean(u"四肢无力"),
        "q10_0":fields.boolean(u"无"),
        "q10_1":fields.boolean(u"月经异常"),
        "q10_2":fields.boolean(u"容易长斑"),
        "q10_3":fields.boolean(u"甲状腺肿大"),
        "q10_4":fields.boolean(u"四肢无力"),
        "q11_0":fields.boolean(u"无"),
        "q11_1":fields.boolean(u"鼻炎"),
        "q11_2":fields.boolean(u"打鼾"),
        "q11_3":fields.boolean(u"哮喘"),
        "q11_4":fields.boolean(u"胸痛"),
        "q11_5":fields.boolean(u"呼吸困难"),
        "q12_0":fields.boolean(u"无"),
        "q12_1":fields.boolean(u"尿频"),
        "q12_2":fields.boolean(u"尿急"),
        "q12_3":fields.boolean(u"尿痛"),
        "q12_4":fields.boolean(u"夜尿增多"),
        "q12_5":fields.boolean(u"晨起眼睑浮肿"),
    }
    _sql_constraints = [
        ('rhwl_easy_genes_name_uniq', 'unique(name)', u'样本编号不能重复!'),
    ]
    _defaults = {
        "state": 'draft',
        "cust_prop": "hospital",
        "is_risk":False,
        "is_child":False,
        "export_img":False,
        "q1_0":False,
        "q1_1":False,
        "q1_2":False,
        "q1_3":False,
        "q1_4":False,
        "q1_5":False,
        "q1_6":False,
        "q1_7":False,
        "q2_0":False,
        "q2_1":False,
        "q2_2":False,
        "q3_0":False,
        "q3_1":False,
        "q3_2":False,
        "q3_3":False,
        "q3_4":False,
        "q3_5":False,
        "q3_6":False,
        "q4_0":False,
        "q4_1":False,
        "q4_2":False,
        "q4_3":False,
        "q4_4":False,
        "q4_5":False,
        "q5_0":False,
        "q5_1":False,
        "q5_2":False,
        "q5_3":False,
        "q5_4":False,
        "q5_5":False,
        "q6_0":False,
        "q6_1":False,
        "q6_2":False,
        "q6_3":False,
        "q6_4":False,
        "q6_5":False,
        "q7_0":False,
        "q7_1":False,
        "q7_2":False,
        "q7_3":False,
        "q7_4":False,
        "q8_0":False,
        "q8_1":False,
        "q8_2":False,
        "q8_3":False,
        "q8_4":False,
        "q9_0":False,
        "q9_1":False,
        "q9_2":False,
        "q9_3":False,
        "q9_4":False,
        "q10_0":False,
        "q10_1":False,
        "q10_2":False,
        "q10_3":False,
        "q10_4":False,
        "q11_0":False,
        "q11_1":False,
        "q11_2":False,
        "q11_3":False,
        "q11_4":False,
        "q11_5":False,
        "q12_0":False,
        "q12_1":False,
        "q12_2":False,
        "q12_3":False,
        "q12_4":False,
        "q12_5":False,
    }

    def _get_hospital_seq(self,cr,uid,hospital,context=None):
        hospital_obj = self.pool.get("res.partner").browse(cr,uid,hospital,context)
        cr.execute("select hospital_seq from rhwl_easy_genes_new where hospital_seq like '%s' order by id desc " % ("YG"+hospital_obj.partner_unid + '-%',))
        max_id=""
        for unid in cr.fetchall():
            max_id = unid[0]
            break
        if max_id:
            max_id = max_id.split('-')[0]+'-'+str(int(max_id.split('-')[1])+1)
        else:
            max_id = "YG"+hospital_obj.partner_unid+'-1'
        return max_id

    def create(self, cr, uid, val, context=None):
        val["log"] = [[0, 0, {"note": u"资料新增", "data": "create"}]]
        val["hospital_seq"] = self._get_hospital_seq(cr,uid,val["hospital"],context)
        self.pool.get("stock.picking.express.detail").confirm_receive(cr,uid,val["name"],context=context)
        return super(rhwl_gene, self).create(cr, uid, val, context=context)

    def write(self, cr, uid, id, val, context=None):
        if not context:
            context={}
        if val.get("state","") in ("confirm",):
            obj = self.browse(cr,SUPERUSER_ID,id,context=context)
            identity = val.get("identity",obj.identity)
            if identity and len(identity)==18:
                try:
                    birthday = datetime.datetime.strptime(identity[6:14],"%Y%m%d")
                    day = datetime.datetime.today() - birthday
                    if day.days<0 or day.days>54750:
                        raise osv.except_osv(u"错误",u"身份证号码中的年月日不在合理范围。")
                except:
                    raise osv.except_osv(u"错误",u"身份证号码中的年月日格式错误。")
        if val.get("identity"):
            val["birthday"]=datetime.datetime.strptime(val.get("identity")[6:14],"%Y%m%d")

        if val.has_key("state"):
            val["log"] = [
                [0, 0, {"note": u"状态变更为:" + self.STATE_SELECT.get(val.get("state")), "data": val.get("state"),"user_id":context.get("user_id",uid)}]]

        return super(rhwl_gene, self).write(cr, uid, id, val, context=context)

    def read_group(self, cr, uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False, lazy=True):
        if groupby.count("date")>0 and not orderby:
            orderby="date desc"

        res=super(rhwl_gene,self).read_group(cr,uid,domain,fields,groupby,offset,limit,context=context,orderby=orderby,lazy=lazy)
        return res

    def unlink(self, cr, uid, ids, context=None):
        if isinstance(ids, (long, int)):
            ids = [ids]
        if uid != SUPERUSER_ID: ids = self.search(cr, uid, [("id", "in", ids), ("state", "=", "draft")],
                                                  context=context)
        return super(rhwl_gene, self).unlink(cr, uid, ids, context=context)

    def _post_images(self,cr,uid,id,img,context=None):
        val={}
        val["log"] = [[0, 0, {"note": u"图片变更", "data": "img"}]]

        if context.has_key("name"):
            obj_name = context["name"]
        else:
            obj = self.browse(cr,SUPERUSER_ID,id,context=context)
            obj_name = obj.name

        vals={
            "name":obj_name,
            "datas_fname":obj_name+".jpg",
            "description":obj_name+" information to IMG",
            "res_model":self._name,
            "res_id":id[0],
            "create_date":fields.datetime.now,
            "create_uid":SUPERUSER_ID,
            "datas":img,
        }
        atta_obj = self.pool.get('ir.attachment')
        atta_id = atta_obj.create(cr,SUPERUSER_ID,vals)
        val["img_atta"]=atta_id

        return self.write(cr,uid,id,val,context=context)

    #取得指定id列表的所有位点数据
    def get_gene_type_list(self,cr,uid,ids,context=None):
        data={}
        for i in self.browse(cr,uid,ids,context=context):
            package_code=i.package_id.code.encode("utf-8")
            key = i.name.encode("utf-8")
            if not data.has_key(package_code):
                data[package_code]={}
            if not data[package_code].has_key(key):
                data[package_code][key]={"name":key,
                           "cust_name":i.cust_name.encode("utf-8").replace(" ",""),
                           "sex":i.sex.encode("utf-8"),
                           "hospital":i.hospital.name.encode("utf-8")
                           }

            for t in i.typ:
                k = t.snp.encode("utf-8")
                data[package_code][key][k]=(t.typ).encode("utf-8").replace("/","")

        return data

    #导出样本位点数据到报告生成服务器
    def export_gene_to_report(self, cr, uid, ids, context=None):
        ids = self.search(cr, uid, [("state", "=", "ok"),("typ","!=",False)], order="batch_no,name",limit=200,context=context)
        if not ids:return

        if isinstance(ids, (long, int)):
            ids = [ids]
        data = self.get_gene_type_list(cr,uid,ids,context=context)
        for k,v in data.items():
            snp_name = k+"_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            fpath = os.path.join(os.path.split(__file__)[0], REMOTE_SNP_PATH)
            fname = os.path.join(fpath, snp_name + ".txt")
            header=[]
            f = open(fname, "w+")

            data_list=data[k].keys()
            data_list.sort()
            for k1 in data_list:
                line_row=[data[k][k1]["name"],data[k][k1]["cust_name"],data[k][k1]["sex"],data[k][k1]["hospital"]]
                if not header:
                    header = data[k][k1].keys()
                    header.remove("name")
                    header.remove("cust_name")
                    header.remove("sex")
                    header.remove("hospital")
                    header.sort()
                    f.write("编号\t姓名\t性别\t送检机构\t" + "\t".join(header) + '\n')
                for i in header:
                    line_row.append(data[k][k1][i])
                f.write("\t".join(line_row) + '\n')
            f.close()
        self.action_state_report(cr, uid, ids, context=context)

    #接收风险报告
    def get_gene_pdf_file(self, cr, uid, context=None):
        #_logger.warn("cron job get_gene_pdf_file")
        model_path=os.path.split(__file__)[0]
        fpath = os.path.join(model_path, REMOTE_REPORT_PATH)
        tpath = os.path.join(model_path, LOCAL_REPORT_PATH)
        pdf_count = 0
        last_week = time.time() - 60*60*24*3

        for f in os.listdir(fpath):
            newfile = os.path.join(fpath, f)
            if not os.path.isdir(newfile):continue
            for f1 in os.listdir(newfile):
                name_list = re.split("[_\.]",f1) #分解文件名称

                if len(name_list)==2:
                    f2 = ".".join(name_list)
                    shutil.move(os.path.join(newfile, f1), os.path.join(tpath, f2))
                    ids = self.search(cr, uid, [("name", "=", f2.split(".")[0])])
                    if ids:
                        self.write(cr, uid, ids,
                                   {"pdf_file": "rhwl_gene/"+LOCAL_REPORT_PATH+"/" + f2, "state": "report_done"})
                        pdf_count += 1
                elif len(name_list)==3:
                    f2 = ".".join([name_list[0],name_list[2]])
                    shutil.move(os.path.join(newfile, f1), os.path.join(tpath, f2))
                    ids = self.search(cr, uid, [("name", "=", f2.split(".")[0])])
                    if ids:
                        self.write(cr, uid, ids,
                                   {"pdf_file": "rhwl_gene/"+LOCAL_REPORT_PATH+"/" + f2, "state": "report_done"})
                        pdf_count += 1


            if os.path.getmtime(newfile) < last_week:
                os.rmdir(newfile)


    def action_state_except(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'res_model': 'rhwl.easy.genes.popup',
            'view_mode': 'form',
            'name': u"异常说明",
            'target': 'new',
            'context': {'col': 'except_note',"tab":"rhwl.easy.genes.new"},
            'flags': {'form': {'action_buttons': False}}}

    def action_state_except_confirm(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'res_model': 'rhwl.easy.genes.popup',
            'view_mode': 'form',
            'name': u"确认说明",
            'target': 'new',
            'context': {'col': 'confirm_note',"tab":"rhwl.easy.genes.new"},
            'flags': {'form': {'action_buttons': False}}}

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



    #根据中间日期计算本周期的起迄日期
    def date_between(self,days=20):
        today = datetime.datetime.today()
        if today.day<=days:
            s_date = today-datetime.timedelta(days=today.day+1)
            s_date = datetime.datetime(s_date.year,s_date.month,days+1)
            e_date = today
        else:
            s_date = datetime.datetime(today.year,today.month,days+1)
            e_date = today
        return s_date,e_date



#样本对象操作日志
class rhwl_gene_log(osv.osv):
    _name = "rhwl.easy.genes.new.log"
    _order = "date desc"
    _columns = {
        "genes_id": fields.many2one("rhwl.easy.genes.new", "Genes ID",select=True),
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
    _name = "rhwl.easy.genes.new.check"
    _columns = {
        "genes_id": fields.many2one("rhwl.easy.genes.new", "Genes ID",select=True),
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
    _name = "rhwl.easy.genes.new.type"
    _columns = {
        "genes_id": fields.many2one("rhwl.easy.genes.new", "Genes ID",select=True),
        "snp": fields.char("SNP", size=20),
        "typ": fields.char("Type", size=10),
        "active": fields.boolean("Active"),
    }
    _defaults = {
        "active": True
    }

class rhwl_reuse(osv.osv):
    _name = "rhwl.easy.genes.new.reuse"
    _inherit = ['ir.needaction_mixin']

    _order = "id desc"

    _columns = {
        "name": fields.many2one("rhwl.easy.genes.new", u"样本单号",required=True,ondelete="restrict"),
        "cust_name": fields.related('name', 'cust_name', type='char', string=u'客户姓名', readonly=1),
        "date": fields.related('name', 'date', type='char', string=u'送检日期', readonly=1),
        "mobile": fields.related('name', 'mobile', type='char', string=u'手机号码', readonly=1),
        "hospital": fields.related('name', 'hospital', relation="res.partner", type='many2one', string=u'送检机构', readonly=1,store=True),
        "notice_user": fields.many2one("res.users", u"通知人员"),
        "notice_date": fields.date(u"通知日期"),
        "reuse_note": fields.char(u"重采原因", size=200),
        "note": fields.text(u"客户说明及备注"),
        "state": fields.selection(
            [("draft", u"未通知"), ("done", u"已通知"), (u"重复通知", u"重复通知"), ("cancel", u"客户放弃"), ("reuse", u"已重采血")], u"状态"),
    }
    _sql_constraints = [
        ('rhwl_easy_genes_new_name_uniq', 'unique(name)', u'样品编号不能重复!'),
    ]
    _defaults = {
        "state": lambda obj, cr, uid, context: "draft",
    }

    def _needaction_domain_get(self, cr, uid, context=None):
        #user = self.pool.get("res.users").browse(cr, uid, uid)
        return [('state','=','draft')]

    def action_done(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'done','notice_user':uid}, context=context)

    def action_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'cancel','notice_user':uid}, context=context)
