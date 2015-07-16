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
import pymongo
import base64
_logger = logging.getLogger(__name__)

class WebClient(http.Controller):
    DB_SERVER="10.0.0.8"
    DB_PORT = 27021
    DB_NAME = "susceptibility"
    COMMON={}

    def _get_cursor(self):
        conn = pymongo.Connection(self.DB_SERVER,self.DB_PORT)
        db = conn[self.DB_NAME]
        return db

    def _get_common(self):
        if not self.COMMON:
            db = self._get_cursor()
            for i in db.common.find():
                self.COMMON[i.get("_id")] = i.get("region")

        return self.COMMON

    def _get_category_header(self,category,template):
        for k,v in template.items():
            if k=="disease":
                return [[]]
    @http.route('/web/api/mongo/get_menu/', type='http', auth="public",website=True)
    def _get_menu(self,**kw):
        db = self._get_cursor()
        content = db.products.find()
        res=[]
        """["泰济生","泰济生",[("CN","中文",[("tjs_quantaoxi","全套系",[("yunmataocan","孕妈套餐")])])]]"""
        languages = self._get_common().get("languages")
        val={}
        for i in content:
            #第一层客户
            if not val.has_key(i.get("belongsto")):
                val[i.get("belongsto")]={
                    "id":i.get("belongsto"),
                    "name":i.get("belongsto"),
                    "sub":{}
                }
            for k in languages.keys():
                if not val[i.get("belongsto")]["sub"].has_key(k):
                    val[i.get("belongsto")]["sub"][k]={"id":k,"name":languages.get(k),"sub":[]}
                if i.has_key(k):
                    tc=[]
                    for s in i.get(k).get("sets").keys():
                        tc.append((s,i.get(k).get("sets").get(s).get("name")))
                    val[i.get("belongsto")]["sub"][k]["sub"].append((i.get("_id"),i.get(k).get("name"),tc))

        for k,v in val.items():
            lang=[]
            for k1,v1 in val.get(k)["sub"].items():
                lang.append((v1["id"],v1["name"],v1["sub"]))
            res.append((v["id"],v["name"],lang))

        response = request.make_response(json.dumps(res,ensure_ascii=False), [('Content-Type', 'application/json')])
        return response.make_conditional(request.httprequest)

    @http.route("/web/api/mongo/get_list/",type='http', auth="public",website=True)
    def _get_list(self,**kw):
        db = self._get_cursor()
        content = db.products.find_one({"_id":kw.get("id").encode("utf-8")})
        res=[]

        category = self._get_common().get("category")
        if category.has_key(kw.get("lang")):
            key = category.get(kw.get("lang")).keys()
            key.sort()

            for i in key:
                tc = content.get(i,{}).get("sets",{}).get(kw.get("tc").encode("utf-8"),{})
                if tc.get("xmlmode"):#取套餐模板
                    template = db.pagemodes.find_one({"_id":tc.get("xmlmode")})

                else:
                    continue
                res.append([i,category.get(kw.get("lang")).get(i),[]])

        response = request.make_response(json.dumps(res,ensure_ascii=False), [('Content-Type', 'application/json')])
        return response.make_conditional(request.httprequest)