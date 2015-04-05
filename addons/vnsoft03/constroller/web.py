# -*- coding: utf-8 -*-

from openerp import http
from openerp import SUPERUSER_ID
import logging

_logging = logging.getLogger(__name__)

class session_web(http.Controller):
    @http.route('/web/session/remove/', type='json', auth="user")
    def remove(self,**kw):
        para = http.request.jsonrequest.get("params")
        u = http.request.registry.get('res.users')
        obj=u.browse(http.request.cr,SUPERUSER_ID,para.get("uid",0))
        if obj.session_id and para.get("session","") and obj.session_id != para.get("session",""):
            sess=http.root.session_store.get(obj.session_id)
            http.root.session_store.delete(sess)
        u.write(http.request.cr,SUPERUSER_ID,para.get("uid",0),{"session_id":para.get("session","")})