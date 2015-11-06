# -*- coding: utf-8 -*-

from openerp import http
from openerp.http import request
from openerp.addons.base.res.res_users import res_users
import json,simplejson
import openerp.tools.config as config
import openerp
from openerp import SUPERUSER_ID
from openerp.modules.registry import RegistryManager
import openerp.addons.web.controllers.main as db
import datetime
import logging
from openerp.tools.translate import _
from lxml import etree
import openerp.addons.rhwl.controllers.web as rhwlweb

STATE = {
    'done':u"完成",
    'progress':u"待确认",
    'draft':u"草稿",
    'cancel':u"取消"
}
_logger = logging.getLogger(__name__)
class WebClient(rhwlweb.WebClient):
    CONTEXT={'lang': "zh_CN",'tz': "Asia/Shanghai"}

    @http.route("/web/api/web_material/get/",type="http",auth="public")
    def _rhwl_web_material_get(self,**kw):
        res = self.check_userinfo(kw)
        data = []
        if res.get('statu')==200:
            uid = res.get("userid")
            registry = RegistryManager.get(request.session.db)
            with registry.cursor() as cr:
                obj = registry.get("product.product")
                ids = obj.search(cr,uid,[("is_web","=",True)],context=self.CONTEXT)
                for i in obj.browse(cr,uid,ids,context=self.CONTEXT):
                    data.append((i.id,i.display_name,i.uom_id.name))
        else:
            data = res
        response = request.make_response(json.dumps(data,ensure_ascii=False), [('Content-Type', 'application/json')])
        return response.make_conditional(request.httprequest)

    @http.route("/web/api/web_material/login_address/",type="http",auth="public")
    def _rhwl_web_material_login_address(self,**kw):
        res = self.check_userinfo(kw)
        data = []
        if res.get('statu')==200:
            uid = res.get("userid")
            registry = RegistryManager.get(request.session.db)
            with registry.cursor() as cr:
                obj = registry.get("res.users")
                partner = registry.get("res.partner")
                user_obj = obj.browse(cr,uid,uid,context=self.CONTEXT)
                partner_obj = partner.browse(cr,uid,user_obj.partner_id.id,context=self.CONTEXT)
                data = [partner_obj.id,partner.get_detail_address(cr,uid,user_obj.partner_id.id,context=self.CONTEXT),partner_obj.name,partner_obj.mobile]
        else:
            data = res
        response = request.make_response(json.dumps(data,ensure_ascii=False), [('Content-Type', 'application/json')])
        return response.make_conditional(request.httprequest)

    @http.route("/web/api/web_material/all_address/",type="http",auth="public")
    def _rhwl_web_material_all_address(self,**kw):
        res = self.check_userinfo(kw)
        data = []
        if res.get('statu')==200:
            uid = res.get("userid")
            partner_id = int(res.get("params").get("partner").encode("utf-8"))

            registry = RegistryManager.get(request.session.db)
            with registry.cursor() as cr:
                partner = registry.get("res.partner")
                partner_obj = partner.browse(cr,uid,partner_id,context=self.CONTEXT)
                if partner_obj.wc_material:
                    data.append([partner_obj.wc_material.id,"无创物料联络人",partner.get_detail_address(cr,uid,partner_obj.wc_material.id,context=self.CONTEXT),partner_obj.wc_material.name,partner_obj.wc_material.mobile])
                if partner_obj.yg_material and partner_obj.yg_material.id != partner_obj.wc_material.id:
                    data.append([partner_obj.yg_material.id,"易感物料联络人",partner.get_detail_address(cr,uid,partner_obj.yg_material.id,context=self.CONTEXT),partner_obj.yg_material.name,partner_obj.yg_material.mobile])
                if partner_obj.ys_material and partner_obj.ys_material.id != partner_obj.yg_material.id and partner_obj.ys_material.id != partner_obj.wc_material.id:
                    data.append([partner_obj.ys_material.id,"叶酸物料联络人",partner.get_detail_address(cr,uid,partner_obj.ys_material.id,context=self.CONTEXT),partner_obj.ys_material.name,partner_obj.ys_material.mobile])
                if partner_obj.el_material and partner_obj.el_material.id not in (partner_obj.wc_material.id,partner_obj.ys_material.id,partner_obj.yg_material.id):
                    data.append([partner_obj.el_material.id,"耳聋物料联络人",partner.get_detail_address(cr,uid,partner_obj.el_material.id,context=self.CONTEXT),partner_obj.el_material.name,partner_obj.el_material.mobile])

        else:
            data = res
        response = request.make_response(json.dumps(data,ensure_ascii=False), [('Content-Type', 'application/json')])
        return response.make_conditional(request.httprequest)

    @http.route("/web/api/web_material/post/",type="http",auth="public")
    def _rhwl_web_material_post(self,**kw):
        res = self.check_userinfo(kw)
        data = []
        if res.get('statu')==200:
            uid = res.get("userid")
            params = eval(res.get("params").get("p"))
            vals={}

            registry = RegistryManager.get(request.session.db)
            with registry.cursor() as cr:
                if params["wh_level"]!="person":
                    vals["hospital"] = int(params["partner_id"])
                vals["wh_level"] = params["wh_level"]
                partner = registry.get("res.partner")
                partner_obj = partner.browse(cr,uid,int(params["address_id"]),context=self.CONTEXT)
                vals["address_id"] = int(params["address_id"])
                vals["receiver_user"] = partner_obj.name
                vals["receiver_address"] = partner.get_detail_address(cr,uid,int(params["address_id"]),context=self.CONTEXT)
                vals["receiver_tel"] = partner_obj.mobile
                if int(params["is_confirm"])==1:
                    vals["state"] = "confirm"
                material = registry.get("rhwl.web.material")
                if int(params["id"])>0:
                    material.write(cr,uid,int(params["id"]),vals,context=self.CONTEXT)
                else:
                    params["id"] = material.create(cr,uid,vals,context=self.CONTEXT)
                #处理明细
                material_line = registry.get("rhwl.web.material.line")
                line_ids = material_line.search(cr,uid,[("parent_id","=",int(params["id"]))])
                if line_ids:
                    material_line.unlink(cr,uid,line_ids)
                for i in params["line"]:
                    material_line.create(cr,uid,{"parent_id":int(params["id"]),"product_id":i[0],"qty":i[1]})
                data.append(params["id"])

        else:
            data = res
        response = request.make_response(json.dumps(data,ensure_ascii=False), [('Content-Type', 'application/json')])
        return response.make_conditional(request.httprequest)

    @http.route("/web/api/web_material/list/",type="http",auth="public")
    def _rhwl_web_material_list(self,**kw):
        res = self.check_userinfo(kw)
        data = []
        if res.get('statu')==200:
            uid = res.get("userid")
            registry = RegistryManager.get(request.session.db)
            with registry.cursor() as cr:
                material = registry.get("rhwl.web.material")
                ids = material.search(cr,uid,[("user_id","=",uid)])
                for i in material.browse(cr,uid,ids,context=self.CONTEXT):
                    data.append([i.id,i.name,i.date,i.state])
        else:
            data = res
        response = request.make_response(json.dumps(data,ensure_ascii=False), [('Content-Type', 'application/json')])
        return response.make_conditional(request.httprequest)

    @http.route("/web/api/web_material/detail/",type="http",auth="public")
    def _rhwl_web_material_detail(self,**kw):
        res = self.check_userinfo(kw)
        data = []
        if res.get('statu')==200:
            uid = res.get("userid")
            id = int(res.get("params").get("id"))
            registry = RegistryManager.get(request.session.db)
            with registry.cursor() as cr:
                material = registry.get("rhwl.web.material")

                for i in material.browse(cr,uid,id,context=self.CONTEXT):
                    data = [i.wh_level,i.hospital.id if i.hospital else 0,i.address_id.id,i.state]
                    detail=[]
                    for d in i.line:
                        detail.append([d.product_id.id,d.product_id.name,d.product_id.uom_id.name,round(d.qty,2)])
                    data.append(detail)
        else:
            data = res
        response = request.make_response(json.dumps(data,ensure_ascii=False), [('Content-Type', 'application/json')])
        return response.make_conditional(request.httprequest)