# -*- coding: utf-8 -*-

from openerp import http
import hashlib
from lxml import etree
from openerp.http import request
from openerp.modules.registry import RegistryManager
from openerp import SUPERUSER_ID
import time
import base64
import datetime,json
import cStringIO
import StringIO
import Image
import logging
import os
import openerp
import openerp.tools.config as config
import shutil
_logger = logging.getLogger(__name__)

class ys(http.Controller):
    @http.route("/web/rhwl_ys/images/",type="http",auth="user")
    def index(self,**kw):
        fname = os.path.join(os.path.split(os.path.split(__file__)[0])[0],"static/webcam_ys.html")
        f=open(fname,"r")
        html=f.readlines()
        f.close()
        return ''.join(html)

    @http.route("/web/rhwl_ys/get/",type="http",auth="user")
    def get_detail(self,**kw):
        registry = RegistryManager.get(request.session.db)
        obj = registry.get("rhwl.genes.ys")
        sexdict={'M':u'男','F':u'女'}
        with registry.cursor() as cr:
            id = obj.search(cr,request.uid,[("name","=",kw.get("no"))])
            if not id:
                data={}
            else:
                res = obj.browse(cr,request.uid,id,context={'lang': "zh_CN",'tz': "Asia/Shanghai"})
                data={
                    "name":res.name,
                    "hospital":res.hospital.name,
                    "doctor":res.doctor.name or "",
                    "date":res.date,
                    "cust_name":res.cust_name,
                    "identity":res.identity,
                    "tel":res.tel
                }

        response = request.make_response(json.dumps(data,ensure_ascii=False), [('Content-Type', 'application/json')])
        return response.make_conditional(request.httprequest)

    @http.route("/web/api/rhwl_ys/pic/",type="http",auth="user")
    def imagepost(self,**kw):
        registry = RegistryManager.get(request.session.db)
        obj = registry.get("rhwl.genes.ys")
        with registry.cursor() as cr:
            id = obj.search(cr,request.uid,[("name","=",kw.get("no"))])
            if not id:
                return "NO_DATA_FOUND"
            file_like = cStringIO.StringIO(kw.get("img1").split(";")[-1].split(",")[-1].decode('base64','strict'))
            img = Image.open(file_like)
            img = img.transpose(Image.ROTATE_270)
            val={"img":base64.encodestring(img.tostring("jpeg",img.mode))}
            if kw.get("etx",""):
                val["except_note"]=kw.get("etx")
                val["except_type"]=kw.get("etx_type")
                obj.write(cr,request.uid,id,{"except_note":kw.get("etx"),"state":"except"},context={'lang': "zh_CN",'tz': "Asia/Shanghai","name":kw.get("no")})
            obj._post_images(cr,request.uid,id,val["img"],context={'lang': "zh_CN",'tz': "Asia/Shanghai","name":kw.get("no")})
            if kw.get("is_confirm")=="true":
                o=obj.browse(cr,request.uid,id,context={'lang': "zh_CN",'tz': "Asia/Shanghai"})
                obj.action_state_confirm(cr,request.uid,id,context={'lang': "zh_CN",'tz': "Asia/Shanghai"})

            return "OK"