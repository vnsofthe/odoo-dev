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

_logger = logging.getLogger(__name__)
class WebClient(http.Controller):
    @http.route('/web/api/mongo/get/', type='http', auth="public",website=True)
    def login(self,**kw):
        conn = pymongo.Connection("10.0.0.8",27017)
        db = conn.test #连接库
        #db.authenticate("tage","123")
        if not kw:
            content = db.test.find()
            res=[]
            #打印所有数据
            for i in content:
                i.pop('_id')
                res.append(i)
        else:
            db.test.insert(kw)
        response = request.make_response(json.dumps(res,ensure_ascii=False), [('Content-Type', 'application/json')])
        return response.make_conditional(request.httprequest)