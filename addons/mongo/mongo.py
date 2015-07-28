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
        content = db.products.find_one({"_id":kw.get("id").encode("utf-8")}) #取套餐数据

        tc = content.get(kw.get("lang").encode("utf-8"),{}).get("sets",{}).get(kw.get("tc").encode("utf-8"),{}) #取指定套餐内容
        #template = db.pagemodes.find_one({"_id":tc.get("xmlmode")}) # 取套餐模板
        category = self._get_common().get("category")
        res=[]

        result={}
        for k,v in tc.get("list").items():
            pd = db.prodata.find_one({"_id":v})
            if not result.has_key(pd["category"]):
                result[pd["category"]]=[]
            result[pd["category"]].append([k,pd.get(kw.get("lang"))["title"]])

        for i in tc.get("region"):
            res.append([i,category.get(kw.get("lang")).get(i),result[i]])

        response = request.make_response(json.dumps([tc["name"],res],ensure_ascii=False), [('Content-Type', 'application/json')])
        return response.make_conditional(request.httprequest)

    @http.route("/web/api/mongo/get_detail/",type='http', auth="public",website=True)
    def _get_detail(self,**kw):
        db = self._get_cursor()
        content = db.products.find_one({"_id":kw.get("id").encode("utf-8")}) #取套餐数据
        tc = content.get(kw.get("lang").encode("utf-8"),{}).get("sets",{}).get(kw.get("tc").encode("utf-8"),{}) #取指定套餐内容
        no = tc.get("list").get(kw.get("no"))
        pd = db.prodata.find_one({"_id":no})

        template = db.pagemodes.find_one({"_id":pd.get("pagemode")}) # 取套餐模板

        res=[]

        #result={}
        #for k,v in content.get(kw.get("lang")).get("sets").get(kw.get("tc")).get("list").items():
        #    if not result.has_key(v["category"]):
        #        result[v["category"]]=[]
        #    result[v["category"]].append([k,v["title"]])
        data = pd.get(kw.get("lang").encode("utf-8"))
        data["sex"] = pd.get("sex")
        res = [template.get("itms"),data]

        response = request.make_response(json.dumps(res,ensure_ascii=False), [('Content-Type', 'application/json')])
        return response.make_conditional(request.httprequest)

    @http.route("/web/api/mongo/post_detail/",type="http",auth="public")
    def _post_detail(self,**kw):
        db = self._get_cursor()
        contents = db.products.find_one({"_id":kw.get("id").encode("utf-8")}) #取套餐数据
        no = contents.get(kw.get("lang")).get("sets").get(kw.get("tc")).get("list").get(kw.get("no"))

        pd = db.prodata.find_one({"_id":no})

        for k,v in kw.items():
            if(k in ["lang","id","tc","no"]):continue
            key=k.split("_")
            if(len(key)==1):
                if(key[0]=="pic"):
                    mimetype=kw.get("pic").mimetype
                    fs=base64.encodestring(kw.get("pic").stream.read())
                    if not (mimetype and fs):continue
                    if not pd[kw.get("lang")].has_key(key[0]):
                        pd[kw.get("lang")][key[0]]={"base64":"","mimetype":""}
                    if not isinstance(pd[kw.get("lang")][key[0]],(dict,)):
                        pd[kw.get("lang")][key[0]]={"base64":"","mimetype":""}
                    pd[kw.get("lang")][key[0]]["base64"]=fs
                    pd[kw.get("lang")][key[0]]["mimetype"]=mimetype
                elif(key[0]=="sex"):
                    pd["sex"]=kw.get("sex")
                else:
                    pd[kw.get("lang")][key[0]]=v
            elif(len(key)==2):
                if not pd[kw.get("lang")].has_key(key[0]):
                    pd[kw.get("lang")][key[0]]={}
                pd[kw.get("lang")][key[0]][key[1]]=v
        db.prodata.update({"_id":no},pd)

        response = request.make_response("数据提交成功，<a href=\"javascript:history.back(-2);\">后退</a>")
        return response.make_conditional(request.httprequest)
