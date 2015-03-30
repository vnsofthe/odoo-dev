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
    DBIP="10.0.0.8"

    @http.route('/web/api/mongo/get/', type='http', auth="public",website=True)
    def login(self,**kw):
        conn = pymongo.Connection(self.DBIP,27017)
        db = conn.disease #连接库
        #db.authenticate("tage","123")
        if not kw:
            content = db.disease.find()
            res=[]
            #打印所有数据
            for i in content:
                res.append([i.get('_id'),i.get('CN') and i.get('CN').get("title","") or "",i.get('EN') and i.get('EN').get("title") or ""])
            res.sort()
        else:
            res={"_id":kw.get("id"),"CN":{"title":kw.get("cn")},"EN":{"title":kw.get("en")}}
            db.disease.insert(res)
        response = request.make_response(json.dumps(res,ensure_ascii=False), [('Content-Type', 'application/json')])
        return response.make_conditional(request.httprequest)

    @http.route('/web/api/mongo/pic/post/', type='http', auth="public")
    def pic_post(self,**kw):
        _logger.info(kw)
        #_logger.info(request.httprequest.files)
        if kw.get("choosefile"):
            key="CN"
            id=kw.get("cn_data_id").encode("utf-8")
            mimetype=kw.get("choosefile").mimetype
        elif kw.get("en_choosefile"):
            key="EN"
            id=kw.get("en_data_id").encode("utf-8")
            mimetype=kw.get("en_choosefile").mimetype
        #_logger.info(dir(kw.get("choosefile").stream))
        #_logger.info(base64.encodestring(kw.get("choosefile").stream.read()))
        if key=="CN":
            fs=base64.encodestring(kw.get("choosefile").stream.read())
        else:
            fs=base64.encodestring(kw.get("en_choosefile").stream.read())
        conn = pymongo.Connection(self.DBIP,27017)
        db = conn.disease #连接库
        res=db.disease.find_one({"_id":id})
        res[key]['pic']={"mimetype":mimetype,"base64":fs}
        db.disease.update({"_id":id},res)
        return 'OK'

    @http.route('/web/api/mongo/detail/get/', type='http', auth="public")
    def detail_get(self,**kw):
        conn = pymongo.Connection(self.DBIP,27017)
        db = conn.disease #连接库
        res=db.disease.find_one({"_id":kw.get("id").encode("utf-8")})
        response = request.make_response(json.dumps(res,ensure_ascii=False), [('Content-Type', 'application/json')])
        return response.make_conditional(request.httprequest)

    @http.route('/web/api/mongo/detail/post/', type='json', auth="public")
    def detail_post(self,**kw):
        conn = pymongo.Connection(self.DBIP,27017)
        db = conn.disease #连接库
        res=db.disease.find_one({"_id":request.jsonrequest.get("_id").encode("utf-8")})
        _logger.info(request.jsonrequest)
        if request.jsonrequest.get("CN"):
            id="CN"
            otherid="EN"
            otherval = res.get("EN")
        else:
            id="EN"
            otherid="CN"
            otherval = res.get("CN")
        cn_obj=request.jsonrequest.get(id)

        _logger.info(cn_obj.keys())
        if not res.get(id):
            res[id]={}
        res[id]['title']=cn_obj.get("title").encode("utf-8")
        if not res[id].get("desc"):
            res[id]['desc']={}
        res[id]['desc']['header']=cn_obj.get("desc").get("header").encode("utf-8")
        res[id]['desc']['description']=cn_obj.get("desc").get("description").encode("utf-8")
        if not res[id].get("genetic"):
            res[id]['genetic']={}
        res[id]['genetic']['header']=cn_obj.get("genetic").get("header").encode("utf-8")
        res[id]['genetic']['description']=cn_obj.get("genetic").get("description").encode("utf-8")
        if not res[id].get("ngenetic"):
            res[id]['ngenetic']={}
        res[id]['ngenetic']['header']=cn_obj.get("ngenetic").get("header").encode("utf-8")
        res[id]['ngenetic']['description']=cn_obj.get("ngenetic").get("description").encode("utf-8")
        if not res[id].get("clinical"):
            res[id]['clinical']={}
        res[id]['clinical']['header']=cn_obj.get("clinical").get("header").encode("utf-8")
        res[id]['clinical']['description']=cn_obj.get("clinical").get("description").encode("utf-8")
        if not res[id].get("diagnose"):
            res[id]['diagnose']={}
        res[id]['diagnose']['header']=cn_obj.get("diagnose").get("header").encode("utf-8")
        res[id]['diagnose']['description']=cn_obj.get("diagnose").get("description").encode("utf-8")
        if not res[id].get("report"):
            res[id]['report']={}
        res[id]['report']['header']=cn_obj.get("report").get("header").encode("utf-8")
        res[id]['report']['level0']=cn_obj.get("report").get("level0").encode("utf-8")
        res[id]['report']['level1']=cn_obj.get("report").get("level1").encode("utf-8")
        res[id]['report']['level2']=cn_obj.get("report").get("level2").encode("utf-8")
        res[id]['report']['level3']=cn_obj.get("report").get("level3").encode("utf-8")
        res[id]['report']['level4']=cn_obj.get("report").get("level4").encode("utf-8")
        if not res[id].get("suggestion"):
            res[id]['suggestion']={}
        res[id]['suggestion']['header']=cn_obj.get("suggestion").get("header").encode("utf-8")
        res[id]['suggestion']['description']=cn_obj.get("suggestion").get("description").encode("utf-8")
        if not res[id].get("nutrition"):
            res[id]['nutrition']={}
        res[id]['nutrition']['header']=cn_obj.get("nutrition").get("header").encode("utf-8")
        res[id]['nutrition']['description']=cn_obj.get("nutrition").get("description").encode("utf-8")

        res[id]['nutrition']['compound']=[]
        for i in cn_obj.get("nutrition").get("compound"):
            res[id]['nutrition']['compound'].append({
                "name":i.get("name").encode("utf-8"),
                "function":i.get("function").encode("utf-8")
            })
        db.disease.update({"_id":request.jsonrequest.get("_id").encode("utf-8")},{id:res.get(id),otherid:otherval})
        return 'OK'


    @http.route('/web/api/mongo/drugs-get/', type='http', auth="public",website=True)
    def drugs_login(self,**kw):
        conn = pymongo.Connection(self.DBIP,27017)
        db = conn.drugs #连接库
        #db.authenticate("tage","123")
        if not kw:
            content = db.drugs.find()
            res=[]
            #打印所有数据
            for i in content:
                res.append([i.get('_id'),i.get('CN') and i.get('CN').get("title","") or "",i.get('EN') and i.get('EN').get("title") or ""])
            res.sort()
        else:
            res={"_id":kw.get("id"),"CN":{"title":kw.get("cn")},"EN":{"title":kw.get("en")}}
            db.drugs.insert(res)
        response = request.make_response(json.dumps(res,ensure_ascii=False), [('Content-Type', 'application/json')])
        return response.make_conditional(request.httprequest)

    @http.route('/web/api/mongo/drugs-detail/get/', type='http', auth="public")
    def drugs_detail_get(self,**kw):
        conn = pymongo.Connection(self.DBIP,27017)
        db = conn.drugs #连接库
        res=db.drugs.find_one({"_id":kw.get("id").encode("utf-8")})
        response = request.make_response(json.dumps(res,ensure_ascii=False), [('Content-Type', 'application/json')])
        return response.make_conditional(request.httprequest)

    @http.route('/web/api/mongo/drugs-pic/post/', type='http', auth="public")
    def drugs_pic_post(self,**kw):

        #_logger.info(request.httprequest.files)
        if kw.get("choosefile"):
            key="CN"
            id=kw.get("cn_data_id").encode("utf-8")
            mimetype=kw.get("choosefile").mimetype
        elif kw.get("en_choosefile"):
            key="EN"
            id=kw.get("en_data_id").encode("utf-8")
            mimetype=kw.get("en_choosefile").mimetype
        #_logger.info(dir(kw.get("choosefile").stream))
        #_logger.info(base64.encodestring(kw.get("choosefile").stream.read()))
        if key=="CN":
            fs=base64.encodestring(kw.get("choosefile").stream.read())
        else:
            fs=base64.encodestring(kw.get("en_choosefile").stream.read())
        conn = pymongo.Connection(self.DBIP,27017)
        db = conn.drugs #连接库
        res=db.drugs.find_one({"_id":id})
        res[key]['pic']={"mimetype":mimetype,"base64":fs}
        db.drugs.update({"_id":id},res)
        return 'OK'

    @http.route('/web/api/mongo/drugs-detail/post/', type='json', auth="public")
    def drugs_detail_post(self,**kw):
        conn = pymongo.Connection(self.DBIP,27017)
        db = conn.drugs #连接库
        res=db.drugs.find_one({"_id":request.jsonrequest.get("_id").encode("utf-8")})

        if request.jsonrequest.get("CN"):
            id="CN"
            otherid="EN"
            otherval = res.get("EN")
        else:
            id="EN"
            otherid="CN"
            otherval = res.get("CN")
        cn_obj=request.jsonrequest.get(id)


        if not res.get(id):
            res[id]={}
        res[id]['title']=cn_obj.get("title").encode("utf-8")
        if not res[id].get("desc"):
            res[id]['desc']={}
        res[id]['desc']['header']=cn_obj.get("desc").get("header").encode("utf-8")
        res[id]['desc']['description']=cn_obj.get("desc").get("description").encode("utf-8")
        if not res[id].get("note"):
            res[id]['note']={}
        res[id]['note']['header']=cn_obj.get("note").get("header").encode("utf-8")
        res[id]['note']['description']=cn_obj.get("note").get("description").encode("utf-8")

        db.drugs.update({"_id":request.jsonrequest.get("_id").encode("utf-8")},{id:res.get(id),otherid:otherval})
        return 'OK'