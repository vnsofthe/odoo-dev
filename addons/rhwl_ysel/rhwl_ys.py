# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID,api
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import datetime,time
import requests
import logging

class rhwl_ys(osv.osv):
    _name="rhwl.genes.ys"
    _description = "叶酸项目信息维护"
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
        "age":fields.integer(u"年龄(周岁)"),
        "mingzhu":fields.char(u"民族",size=20),
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
        "state":fields.selection([("draft",u"草稿"),("img",u"拍照"),("confirm",u"确认"),("library",u"实验完成"),("report",u"生成报告中"),("done",u"完成"),("cancel",u"取消"),("error",u"重做")],string=u"状态"),
        "img_atta":fields.many2one("ir.attachment","IMG"),
        "img_new":fields.related("img_atta","datas",type="binary"),
        "log":fields.one2many("rhwl.genes.ys.log","parent_id",string=u"日志",readonly=True),
        "snp": fields.one2many("rhwl.genes.ys.snp", "parent_id", "SNP"),
    }
    _sql_constraints = [
        ('rhwl_genes_ys_uniq', 'unique(name)', u'样本编号不能重复!'),
    ]
    _defaults={
        "state":"draft",
        "sex":"F"
    }

    @api.onchange("hospital")
    def onchange_hospital(self):
        if self.hospital:
            self.user_id = self.hospital.user_id

    def create(self, cr, uid, val, context=None):
        val["log"] = [[0, 0, {"note": u"资料新增", "data": "create"}]]

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

    def action_state_confirm(self,cr,uid,id,context=None):
        self.write(cr,uid,id,{"state":"confirm"},context=None)

    def action_state_snp(self,cr,uid,id,context=None):
        self.write(cr,uid,id,{"state":"library"},context=None)

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
            "res_model":"rhwl.genes.ys",
            "res_id":id[0],
            "create_date":fields.datetime.now,
            "create_uid":SUPERUSER_ID,
            "datas":img,
        }
        atta_obj = self.pool.get('ir.attachment')
        atta_id = atta_obj.create(cr,SUPERUSER_ID,vals)
        val["img_atta"]=atta_id
        val["state"]="img"
        return self.write(cr,uid,id,val,context=context)

class rhwl_log(osv.osv):
    _name = "rhwl.genes.ys.log"
    _order = "date desc"
    _columns = {
        "parent_id": fields.many2one("rhwl.genes.ys", "Parent ID",select=True),
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
    _name = "rhwl.genes.ys.snp"
    _columns = {
        "parent_id": fields.many2one("rhwl.genes.ys", "Parent ID",select=True),
        "snp": fields.char("SNP", size=20),
        "typ": fields.char("Type", size=10),
        "active": fields.boolean("Active"),
    }
    _defaults = {
        "active": True
    }