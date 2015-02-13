# -*- coding: utf-8 -*-

from openerp import http
from openerp.http import request
from openerp.modules.registry import RegistryManager
import openerp.addons.web.controllers.main as db
import datetime
import logging
import json
from . import web
class WebClient(web.WebClient):

    @http.route("/web/charts/sale/",type="http",auth="public")
    def charts_sale(self,**kw):
        res =self.check_userinfo(kw)
        if res.get("statu")!=200:
            return self.json_return(res)
        uid=res.get("userid")
        registry = RegistryManager.get(request.session.db)
        with registry.cursor() as cr:
            obj = registry.get("res.partner")
            partner_ids = obj.search(cr,uid,[("sjjysj","!=",False)])
            cr.execute("""
                select b.name,count(*)
                from sale_sampleone a
                left join res_partner b on a.cxyy=b.id
                where b.id in %s
                group by b.name""" %(tuple(partner_ids),))
            return self.json_return(cr.fetchall())


    def json_return(self,data):
        response = request.make_response(json.dumps(data,ensure_ascii=False), [('Content-Type', 'application/json')])
        return response.make_conditional(request.httprequest)