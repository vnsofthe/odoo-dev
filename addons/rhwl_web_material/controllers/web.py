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
                if partner_obj.yg_material:
                    data.append([partner_obj.yg_material.id,"易感物料联络人",partner.get_detail_address(cr,uid,partner_obj.yg_material.id,context=self.CONTEXT),partner_obj.yg_material.name,partner_obj.yg_material.mobile])
                if partner_obj.ys_material:
                    data.append([partner_obj.ys_material.id,"叶酸物料联络人",partner.get_detail_address(cr,uid,partner_obj.ys_material.id,context=self.CONTEXT),partner_obj.ys_material.name,partner_obj.ys_material.mobile])
                if partner_obj.el_material:
                    data.append([partner_obj.el_material.id,"耳聋物料联络人",partner.get_detail_address(cr,uid,partner_obj.el_material.id,context=self.CONTEXT),partner_obj.el_material.name,partner_obj.el_material.mobile])

        else:
            data = res
        response = request.make_response(json.dumps(data,ensure_ascii=False), [('Content-Type', 'application/json')])
        return response.make_conditional(request.httprequest)