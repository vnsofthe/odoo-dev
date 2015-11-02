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
class WebClient(http.Controller):
    CONTEXT={'lang': "zh_CN",'tz': "Asia/Shanghai"}

    @http.route("/web/api/web_material/get/",type="http",auth="public")
    def _rhwl_partner_get(self,**kw):
        res = rhwlweb.check_userinfo(kw)
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