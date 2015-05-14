# -*- coding: utf-8 -*-

from openerp import http
from openerp.http import request
from openerp.modules.registry import RegistryManager
import openerp.addons.web.controllers.main as db
import datetime
import logging
import json
from . import web
_logger = logging.getLogger(__name__)
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
            _logger.info(partner_ids)
            cr.execute("""
                with t as (
                select b.id,b.name,a.cx_date,count(*) as c
                                from sale_sampleone a
                                left join res_partner b on a.cxyy=b.id
                                where a.is_reused='0' and b.id in %s
                                group by b.id,b.name,a.cx_date)
                select	id
                    ,name
                    ,sum(c)
                    ,(select COALESCE(sum(c),0) from t where date_trunc('month',cx_date)::date = date_trunc('month',now())::date and t.id=tt.id)
                    ,(select COALESCE(sum(c),0) from t where date_trunc('month',cx_date)::date = date_trunc('month',(now() - interval '1 month'))::date and t.id=tt.id)
                    ,(select COALESCE(sum(c),0) from t where cx_date >= (now() - interval '3 month')::date and t.id=tt.id)
                    ,(select COALESCE(sum(c),0) from t where cx_date >= (now() - interval '6 month')::date and t.id=tt.id)
                    ,(select COALESCE(sum(c),0) from t where cx_date >= (now() - interval '12 month')::date and t.id=tt.id)
                     from t tt group by id,name""" % (str(partner_ids).replace('[','(').replace(']',')'),))
            return self.json_return(cr.fetchall())

    @http.route("/web/charts/sale2/",type="http",auth="public")
    def charts_sale2(self,**kw):
        res =self.check_userinfo(kw)
        if res.get("statu")!=200:
            return self.json_return(res)
        uid=res.get("userid")
        registry = RegistryManager.get(request.session.db)
        with registry.cursor() as cr:
            obj = registry.get("res.partner")
            partner_ids = obj.search(cr,uid,[("sjjysj","!=",False)])
            cr.execute("""
                with t as (
                select b.id,b.name,a.check_state,count(*) as c
                                from sale_sampleone a
                                left join res_partner b on a.cxyy=b.id
                                where b.id in %s
                                group by b.id,b.name,a.check_state)
                select	id
                    ,name
                    ,sum(c)
                    ,(select COALESCE(sum(c),0) from t where check_state='reuse' and t.id=tt.id)
                    ,(select COALESCE(sum(c),0) from t where check_state='except' and t.id=tt.id)
                     from t tt group by id,name""" % (str(partner_ids).replace('[','(').replace(']',')'),))
            return self.json_return(cr.fetchall())

    def json_return(self,data):
        response = request.make_response(json.dumps(data,ensure_ascii=False), [('Content-Type', 'application/json')])
        return response.make_conditional(request.httprequest)