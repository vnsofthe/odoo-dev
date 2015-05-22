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

    @http.route('/web/api/mongo/character-get/', type='http', auth="public",website=True)
    def drugs_login(self,**kw):
        conn = pymongo.Connection(self.DBIP,27017)
        db = conn.topic #连接库
        #db.authenticate("tage","123")
        if not kw:
            content = db.topic.find()
            res=[]
            #打印所有数据
            for i in content:
                res.append([i.get('_id'),i.get('CN') and i.get('CN').get("title","") or "",i.get('EN') and i.get('EN').get("title") or ""])
            res.sort()
        else:
            res={"_id":kw.get("id"),"CN":{"title":kw.get("cn")},"EN":{"title":kw.get("en")}}
            db.topic.insert(res)
        response = request.make_response(json.dumps(res,ensure_ascii=False), [('Content-Type', 'application/json')])
        return response.make_conditional(request.httprequest)

    @http.route('/web/api/mongo/character-detail/get/', type='http', auth="public")
    def drugs_detail_get(self,**kw):
        conn = pymongo.Connection(self.DBIP,27017)
        db = conn.topic #连接库
        res=db.topic.find_one({"_id":kw.get("id").encode("utf-8")})
        response = request.make_response(json.dumps(res,ensure_ascii=False), [('Content-Type', 'application/json')])
        return response.make_conditional(request.httprequest)

    @http.route('/web/api/mongo/character-pic/post/', type='http', auth="public")
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
        db = conn.topic #连接库
        res=db.topic.find_one({"_id":id})
        res[key]['pic']={"mimetype":mimetype,"base64":fs}
        db.topic.update({"_id":id},res)
        return 'OK'

    @http.route('/web/api/mongo/character-detail/post/', type='json', auth="public")
    def drugs_detail_post(self,**kw):
        conn = pymongo.Connection(self.DBIP,27017)
        db = conn.topic #连接库
        res=db.topic.find_one({"_id":request.jsonrequest.get("_id").encode("utf-8")})

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
        res[id]['note']['descriptionM']=cn_obj.get("note").get("descriptionM").encode("utf-8")
        res[id]['note']['descriptionF']=cn_obj.get("note").get("descriptionF").encode("utf-8")

        db.topic.update({"_id":request.jsonrequest.get("_id").encode("utf-8")},res)
        return 'OK'