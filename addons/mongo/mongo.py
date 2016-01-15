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
import os,re

_logger = logging.getLogger(__name__)

class WebClient(http.Controller):
    DB_SERVER="10.0.0.8"
    DB_PORT = 27021
    DB_NAME = "susceptibility"
    COMMON={}


    def _get_cursor(self,dbname=DB_NAME):
        conn = pymongo.Connection(self.DB_SERVER,self.DB_PORT)
        db = conn[dbname]
        return db

    def _get_common(self):
        #if not self.COMMON:
        db = self._get_cursor()
        for i in db.common.find():
            self.COMMON[i.get("_id")] = i.get("region")

        return self.COMMON

    def _get_category_header(self,category,template):
        for k,v in template.items():
            if k=="disease":
                return [[]]

    @http.route("/tjs/",type="http",auth="user")
    def index_tjs(self,**kw):
        fname = os.path.join(os.path.split(__file__)[0],"html/tjs.html")
        f=open(fname,"r")
        html=f.readlines()
        f.close()
        return ''.join(html)

    @http.route("/rhwl/",type="http",auth="user")
    def index_rhwl(self,**kw):
        fname = os.path.join(os.path.split(__file__)[0],"html/rhwl.html")
        f=open(fname,"r")
        html=f.readlines()
        f.close()
        return ''.join(html)

    @http.route("/tjs/list/",type="http",auth="user")
    def index_tjs_list(self,**kw):
        fname = os.path.join(os.path.split(__file__)[0],"html/tjs_list.html")
        f=open(fname,"r")
        html=f.readlines()
        f.close()
        return ''.join(html)

    @http.route("/rhwl/list/",type="http",auth="user")
    def index_rhwl_list(self,**kw):
        fname = os.path.join(os.path.split(__file__)[0],"html/rhwl_list.html")
        f=open(fname,"r")
        html=f.readlines()
        f.close()
        return ''.join(html)

    @http.route("/tjs/detail/",type="http",auth="user")
    def index_tjs_detail(self,**kw):
        fname = os.path.join(os.path.split(__file__)[0],"html/tjs_detail.html")
        f=open(fname,"r")
        html=f.readlines()
        f.close()
        return ''.join(html)

    @http.route("/web/mongo/index/",type="http",auth="user")
    def index(self,**kw):
        fname = os.path.join(os.path.split(__file__)[0],"html/index_new.html")
        f=open(fname,"r")
        html=f.readlines()
        f.close()
        return ''.join(html)

    @http.route("/web/mongo/index/listview/",type="http",auth="user")
    def index_list(self,**kw):
        fname = os.path.join(os.path.split(__file__)[0],"html/listview.html")
        f=open(fname,"r")
        html=f.readlines()
        f.close()
        return ''.join(html)

    @http.route("/web/mongo/index/listview/edit/",type="http",auth="user")
    def index_list_edit(self,**kw):
        fname = os.path.join(os.path.split(__file__)[0],"html/edit-new.html")
        f=open(fname,"r")
        html=f.readlines()
        f.close()
        return ''.join(html)

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
        susceptibility_db = self._get_cursor("susceptibility")
        genes_db = self._get_cursor("genes")

        content = db.products.find_one({"_id":kw.get("id").encode("utf-8")}) #取套餐数据

        tc = content.get(kw.get("lang").encode("utf-8"),{}).get("sets",{}).get(kw.get("tc").encode("utf-8"),{}) #取指定套餐内容
        #template = db.pagemodes.find_one({"_id":tc.get("xmlmode")}) # 取套餐模板
        category = self._get_common().get("category")
        res=[]
        result={}
        snp_result=[]
        for k,v in tc.get("list").items():
            pd = db.prodata.find_one({"_id":v})
            if not pd:continue
            if not result.has_key(pd["category"]):
                result[pd["category"]]=[]
            result[pd["category"]].append([k,pd.get(kw.get("lang")).get("title",""),pd.get("sex"),int(pd.get(kw.get("lang")).get("subclass").get("order"))*100+int(pd.get(kw.get("lang")).get("order")),pd.get(kw.get("lang")).get("subclass").get("name")])
            for r in susceptibility_db.relations.find({'itm': pd.get("_id")}):
                rsid= [r.get("rsid")]
                genes=[]
                rsid_ids = genes_db.rsid2genes.find({"_id":{'$in':rsid}})
                for i in rsid_ids:
                    for g in i.get("gene"):
                        snp_result.append([pd.get(kw.get("lang")).get("title",""),r.get("gtid"),g])

        for i in tc.get("region"):
            result[i].sort(lambda x,y:cmp(x[3],y[3]))
            res.append([i,category.get(kw.get("lang")).get(i),result[i]])

        response = request.make_response(json.dumps([tc["name"],res,snp_result],ensure_ascii=False), [('Content-Type', 'application/json')])
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

        susceptibility_db = self._get_cursor("susceptibility")
        genes_db = self._get_cursor("genes")
        for r in susceptibility_db.relations.find({'itm': pd.get("_id")}):
            rsid= [r.get("rsid")]
            genes=[]
            rsid_ids = genes_db.rsid2genes.find({"_id":{'$in':rsid}})
            for i in rsid_ids:
                genes = genes + i.get("gene")
            if genes:
                for i in genes_db.geneFunctions.find({"_id":{'$in':genes}}):
                    res.append([r.get("gtid"),i["_id"],i["fullname"],i["function"]["pathway_go"],i["function"]["summary"]])

        data = pd.get(kw.get("lang").encode("utf-8"))
        data["sex"] = pd.get("sex")
        res = [template.get("itms"),data,res]

        response = request.make_response(json.dumps(res,ensure_ascii=False), [('Content-Type', 'application/json')])
        return response.make_conditional(request.httprequest)

    @http.route("/web/api/mongo/post_detail/",type="http",auth="user")
    def _post_detail(self,**kw):
        if not request.uid:
            return "权限不足"
        registry = RegistryManager.get(request.session.db)
        with registry.cursor() as cr:
            user = registry.get("res.users")
            user_obj = user.browse(cr,SUPERUSER_ID,request.uid)
            if not user.has_group(cr,request.uid,"mongo.rhwl_mongo_manager"):
                return "权限不足"

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

    @http.route("/web/api/mongo/get_genes/",type="http",auth="user")
    def _get_genes(self,**kw):
        genes_db = self._get_cursor("genes")
        snps_db = self._get_cursor("snps")
        res=[]
        snps_ids={}
        gene_ids=[]
        for i in snps_db.snps.find({"gtid":{"$in":[re.compile(kw.get("no").encode("utf-8"))]}}):
            snps_ids[i["_id"]] = i["gtid"]
        for k,v in snps_ids.items():
            for i in genes_db.rsid2genes.find({"_id":{"$in":[k]}}):
                gene_ids = i["gene"]
                for i in genes_db.geneFunctions.find({"_id":{'$in':gene_ids}}):
                    res.append([v,i["_id"],i["fullname"],i["function"]["pathway_go"],i["function"]["summary"]])

        for i in genes_db.geneFunctions.find({"_id":{'$in':[re.compile(kw.get("no").encode("utf-8"))]}}):
            res.append(["--",i["_id"],i["fullname"],i["function"]["pathway_go"],i["function"]["summary"]])

        response = request.make_response(json.dumps(res,ensure_ascii=False), [('Content-Type', 'application/json')])
        return response.make_conditional(request.httprequest)

    @http.route("/web/api/mongo/get_rs_from_gt/",type="http",auth="user")
    def _get_rs_from_gt(self,**kw):
        snps_db = self._get_cursor("snps")
        res=[]
        for i in snps_db.snps.find({"gtid":{"$in":[re.compile(kw.get("rs").encode("utf-8"))]}}):
            res.append([i.get("_id"),i.get("gtid")])

        response = request.make_response(json.dumps(res,ensure_ascii=False), [('Content-Type', 'application/json')])
        return response.make_conditional(request.httprequest)