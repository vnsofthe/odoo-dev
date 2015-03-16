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
        mimetype=kw.get("choosefile").mimetype
        #_logger.info(dir(kw.get("choosefile").stream))
        #_logger.info(base64.encodestring(kw.get("choosefile").stream.read()))
        fs=base64.encodestring(kw.get("choosefile").stream.read())
        conn = pymongo.Connection(self.DBIP,27017)
        db = conn.disease #连接库
        db.disease.update({"_id":kw.get("cn_data_id").encode("utf-8")},{"CN":{"pic":{"mimetype":mimetype,"base64":fs}}})
        return 'OK'

    @http.route('/web/api/mongo/detail/get/', type='http', auth="public")
    def detail_get(self,**kw):
        conn = pymongo.Connection(self.DBIP,27017)
        db = conn.disease #连接库
        res=db.disease.find_one({"_id":kw.get("id").encode("utf-8")})
        response = request.make_response(json.dumps(res,ensure_ascii=False), [('Content-Type', 'application/json')])
        return response.make_conditional(request.httprequest)

    @http.route('/web/api/mongo/detail/post/', type='http', auth="public")
    def detail_post(self,**kw):
        _logger.info(kw)