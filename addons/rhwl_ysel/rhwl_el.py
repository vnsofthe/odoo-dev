# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID,api
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import datetime,time
import requests
import logging
import os
import re
import shutil

REMOTE_SERVER_PATH="static/remote/el/snp"
REMOTE_REPORT_PATH="static/remote/el/report"
LOCAL_REPORT_PATH="static/local/report/el"
class rhwl_ys(osv.osv):
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
    _name="rhwl.genes.el"
    _description = "耳聋项目信息维护"
    _order = "date desc"
    _columns={
        "name": fields.char(u"样品编号", required=True, size=20),
        "batch_no":fields.char(u"批次",size=10),
        "hospital":fields.many2one('res.partner', string=u'送检医院',domain="[('is_company', '=', True), ('customer', '=', True)]", required=True),
        "doctor":fields.many2one('res.partner', string=u'送检医生',domain="[('is_company', '=', False), ('customer', '=', True),('parent_id','=',hospital)]"),
        "user_id":fields.many2one("res.users",string=u"销售员",),
        "room":fields.char(u"科室",size=20),
        "date":fields.date(u"采样日期", required=True),
        "cust_name":fields.char(u"客户姓名", required=True, size=20),
        "cust_pinying":fields.char(u"客户姓名(拼音)", size=20),
        "sex":fields.selection([("F",u"女"),("M",u"男")],string=u"性别",required=True),
        "birthday":fields.date(u"出生日期"),
        "fdjfr":fields.selection([("M",u"父亲"),("F",u"母亲")],string=u"法定监护人"),
        "fdjfr_name":fields.char(u"法定监护人姓名",size=20),
        "age":fields.integer(u"年龄(周岁)"),
        "is_jksc":fields.boolean(u"健康筛查"),
        "is_both":fields.boolean(u"父母均为耳聋患者"),
        "is_father":fields.boolean(u"父亲耳聋"),
        "is_mother":fields.boolean(u"母亲耳聋"),
        "is_brother":fields.boolean(u"父母健康、兄弟姐妹有耳聋"),
        "tel":fields.char(u"联系电话",size=20),
        "contact":fields.char(u"紧急联系人",size=20),
        "contact_tel":fields.char(u"紧急联系人电话",size=20),
        "identity": fields.char(u"身份证号", size=18),
        "state_id": fields.many2one("res.country.state",string=u'省'),
        #"city_id": fields.many2one("res.country.state.city", string=u"样品区域（市)",domain="[('state_id','=',state_id)]"),
        "city_id": fields.many2one("res.country.state.city",string=u'市',domain="[('state_id','=',state_id)]"),
        "area_id":fields.many2one("res.country.state.city.area",string=u"区/县",domain="[('city_id','=',city_id)]"),
        "address":fields.char(u"详细地址",size=100),
        "note":fields.char(u"备注",size=100),
        "state":fields.selection(STATE_SELECT_LIST,string=u"状态"),
        "img_atta":fields.many2one("ir.attachment","IMG"),
        "img_new":fields.related("img_atta","datas",type="binary"),
        "log":fields.one2many("rhwl.genes.el.log","parent_id",string=u"日志",readonly=True),
        "snp": fields.one2many("rhwl.genes.el.snp", "parent_id", "SNP"),
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
        "pdf_file": fields.char(u"检测报告", size=100),
    }
    _sql_constraints = [
        ('rhwl_genes_el_uniq', 'unique(name)', u'样本编号不能重复!'),
    ]
    _defaults={
        "state":"draft",
        "sex":"F"
    }

    @api.onchange("hospital")
    def onchange_hospital(self):
        if self.hospital:
            self.user_id = self.hospital.user_id

    def _get_hospital_seq(self,cr,uid,hospital,context=None):
        hospital_obj = self.pool.get("res.partner").browse(cr,uid,hospital,context)
        cr.execute("select hospital_seq from rhwl_genes_el where hospital_seq like '%s' order by id desc " % ("EL"+hospital_obj.partner_unid + '-%',))
        max_id=""
        for unid in cr.fetchall():
            max_id = unid[0]
            break
        if max_id:
            max_id = max_id.split('-')[0]+'-'+str(int(max_id.split('-')[1])+1)
        else:
            max_id = "EL"+hospital_obj.partner_unid+'-1'
        return max_id

    def create(self, cr, uid, val, context=None):
        val["log"] = [[0, 0, {"note": u"资料新增", "data": "create"}]]
        val["hospital_seq"] = self._get_hospital_seq(cr,uid,val["hospital"],context)
        self.pool.get("stock.picking.express.detail").confirm_receive(cr,uid,val["name"],context=context)
        return super(rhwl_ys, self).create(cr, uid, val, context=context)

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

        if val.has_key("state"):
            if not val.has_key("log"):
                val["log"]=[]
            sel = dict(fields.selection.reify(cr,uid,self,self._columns['state'],context=context))
            val["log"].append([0, 0, {"note": u"状态变更为:" + sel.get(val.get("state")), "data": val.get("state"),"user_id":context.get("user_id",uid)}])

        return super(rhwl_ys, self).write(cr, uid, id, val, context=context)

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
            'context': {'col': 'except_note',"tab":self._name},
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
            'context': {'col': 'confirm_note',"tab":self._name},
            'flags': {'form': {'action_buttons': False}}}

    def action_state_confirm(self,cr,uid,id,context=None):
        self.write(cr,uid,id,{"state":"confirm"},context=None)

    def action_state_snp(self,cr,uid,id,context=None):
        self.write(cr,uid,id,{"state":"library"},context=None)

    def action_view_pdf(self, cr, uid, ids, context=None):
        return {'type': 'ir.actions.act_url',
                'url': context.get("file_name", "/"),
                'target': 'new'}

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
            "res_model":"rhwl.genes.el",
            "res_id":id[0],
            "create_date":fields.datetime.now,
            "create_uid":SUPERUSER_ID,
            "datas":img,
        }
        atta_obj = self.pool.get('ir.attachment')
        atta_id = atta_obj.create(cr,SUPERUSER_ID,vals)
        val["img_atta"]=atta_id

        return self.write(cr,uid,id,val,context=context)


    def get_gene_type_list(self,cr,uid,ids,context=None):
        data={}
        for i in self.browse(cr,uid,ids,context=context):
            data[i.name]={"cust_name":i.cust_name.encode("utf-8"),"sex":i.sex.encode("utf-8")}

            for s in i.snp:
                data[i.name][s.snp.encode("utf-8")] = s.typ.encode("utf-8").replace("/","")

        return data

    def export_gene_to_report(self,cr,uid,ids,context=None):
        ids = self.search(cr, uid, [("state", "=", "ok"),("snp","!=",False)], order="name",limit=200,context=context)
        if not ids:return
        if isinstance(ids, (long, int)):
            ids = [ids]
        data = self.get_gene_type_list(cr,uid,ids,context=context)
        snp_name = "el_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        fpath = os.path.join(os.path.split(__file__)[0], REMOTE_SERVER_PATH)
        fname = os.path.join(fpath, snp_name + ".txt")
        header=[]
        f = open(fname, "w+")


        for k,v in data.items():
            line_row=[k,v["cust_name"],v["sex"]]
            if not header:
                header = v.keys()
                header.remove("cust_name")
                header.remove("sex")
                header.sort()
                f.write("编号\t姓名\t性别\t" + "\t".join(header) + '\n')
            for i in header:
                line_row.append(data[k][i])
            f.write("\t".join(line_row) + '\n')
        f.close()

        self.write(cr,uid,ids,{"state":"report"},context=context)

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
                                   {"pdf_file": "rhwl_ysel/"+LOCAL_REPORT_PATH+"/" + f2, "state": "report_done"})
                        pdf_count += 1
                elif len(name_list)==3:
                    f2 = ".".join([name_list[0],name_list[2]])
                    shutil.move(os.path.join(newfile, f1), os.path.join(tpath, f2))
                    ids = self.search(cr, uid, [("name", "=", f2.split(".")[0])])
                    if ids:
                        self.write(cr, uid, ids,
                                   {"pdf_file": "rhwl_ysel/"+LOCAL_REPORT_PATH+"/" + f2, "state": "report_done"})
                        pdf_count += 1


            if os.path.getmtime(newfile) < last_week:
                os.rmdir(newfile)


class rhwl_log(osv.osv):
    _name = "rhwl.genes.el.log"
    _order = "date desc"
    _columns = {
        "parent_id": fields.many2one("rhwl.genes.el", "Parent ID",select=True),
        "date": fields.datetime(u"时间"),
        "user_id": fields.many2one("res.users", u"操作人员"),
        "note": fields.text(u"作业说明"),
        "data": fields.char("Data")
    }

    _defaults = {
        "date": fields.datetime.now,
        "user_id": lambda obj, cr, uid, context: uid,
    }

#疾病位点数据对象
class rhwl_ys_snp(osv.osv):
    _name = "rhwl.genes.el.snp"
    _columns = {
        "parent_id": fields.many2one("rhwl.genes.el", "Parent ID",select=True),
        "snp": fields.char("SNP", size=20),
        "typ": fields.char("Type", size=10),
        "active": fields.boolean("Active"),
    }
    _defaults = {
        "active": True
    }

class rhwl_reuse(osv.osv):
    _name = "rhwl.genes.el.reuse"
    _inherit = ['ir.needaction_mixin']

    _order = "id desc"

    _columns = {
        "name": fields.many2one("rhwl.genes.el", u"样本单号",required=True,ondelete="restrict"),
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
        ('rhwl_genes_el_name_uniq', 'unique(name)', u'样品编号不能重复!'),
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

class rhwl_exception(osv.osv):
    _name = "rhwl.genes.el.exception"
    _inherit = ['ir.needaction_mixin']
    _description = "样本阳性跟踪"
    _order = "id desc"
    _columns = {
        "name": fields.many2one("rhwl.genes.el", u"样本单号",ondelete="restrict"),
        "cust_name": fields.related('name', 'cust_name', type='char', string=u'客户姓名', readonly=1),
        "date": fields.related('name', 'date', type='char', string=u'送检日期', readonly=1),
        "mobile": fields.related('name', 'mobile', type='char', string=u'手机号码', readonly=1),
        "hospital": fields.related('name', 'hospital', relation="res.partner", type='many2one', string=u'送检机构', readonly=1,store=True),
        "lib_notice": fields.char(u"检测结论", size=100),
        "cs_notice": fields.char(u"客服备注", size=100),
        "notice_user": fields.many2one("res.users", u"通知人员"),
        "notice_date": fields.date(u"通知日期"),
        "is_notice": fields.boolean(u"是否已通知"),
        "is_take": fields.boolean(u"是否取走检测报告"),
        "state": fields.selection(
            [("draft", u"未通知"), ("notice", u"已通知"), ("renotice", u"重复通知"), ("getreport", u"已取报告"),
             ("done", u"完成"), ("cancel", u"已中止")], u"状态"),
    }
    _sql_constraints = [
        ('rhwl_genes_el_number_uniq', 'unique(name)', u'样品编号不能重复!'),
    ]
    _defaults = {
        "state": lambda obj, cr, uid, context: "draft",
    }

    def _needaction_domain_get(self, cr, uid, context=None):
        #user = self.pool.get("res.users").browse(cr, uid, uid)
        return [('state','=','draft')]

    def action_notice(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'notice','notice_user':uid,"notice_date":datetime.date.today(),"is_notice":True}, context=context)

    def action_report(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'getreport','is_take':True}, context=context)

    def action_next(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'next','is_next':True}, context=context)

    def action_done(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'done'}, context=context)

    def action_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'cancel'}, context=context)