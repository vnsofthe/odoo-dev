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
_logger = logging.getLogger(__name__)

class gene(http.Controller):
    @http.route("/web/api/gene/pic/",type="http",auth="user")
    def imagepost(self,**kw):
        registry = RegistryManager.get(request.session.db)
        obj = registry.get("rhwl.easy.genes")
        with registry.cursor() as cr:
            id = obj.search(cr,request.uid,[("name","=",kw.get("no"))])
            if not id:
                return "NO_DATA_FOUND"
            file_like = cStringIO.StringIO(kw.get("img1").split(";")[-1].split(",")[-1].decode('base64','strict'))
            img = Image.open(file_like)
            width,height = img.size
            file_like2 = cStringIO.StringIO(kw.get("img2").split(";")[-1].split(",")[-1].decode('base64','strict'))
            img2 = Image.open(file_like2)

            region = img2.crop((0,0,width/2,height))
            img.paste(region, (width/2, 0,width,height))
            val={"img":base64.encodestring(img.tostring("jpeg",img.mode))}
            if kw.get("etx",""):
                val["except_note"]=kw.get("etx")

            obj.write(cr,request.uid,id,val,context={'lang': "zh_CN",'tz': "Asia/Shanghai"})
            o=obj.browse(cr,request.uid,id,context={'lang': "zh_CN",'tz': "Asia/Shanghai"})
            if o.state=="draft":
                if val.has_key("except_note"):
                    obj.action_state_except(cr,request.uid,id,context={'lang': "zh_CN",'tz': "Asia/Shanghai"})
                elif kw.get("is_confirm")=="true":
                    obj.action_state_confirm(cr,request.uid,id,context={'lang': "zh_CN",'tz': "Asia/Shanghai"})

            cr.commit()
            return "OK"

    @http.route("/web/rhwl_gene/get/",type="http",auth="user")
    def get_detail(self,**kw):
        registry = RegistryManager.get(request.session.db)
        obj = registry.get("rhwl.easy.genes")
        sexdict={'T':u'男','F':u'女'}
        with registry.cursor() as cr:
            id = obj.search(cr,request.uid,[("name","=",kw.get("no"))])
            if not id:
                data={}
            else:
                res = obj.browse(cr,request.uid,id,context={'lang': "zh_CN",'tz': "Asia/Shanghai"})
                data={
                    "batch_no":res.batch_no,
                    "name":res.name,
                    "date":res.date,
                    "cust_name":res.cust_name,
                    "sex": sexdict.get(res.sex,""),
                    "identity":res.identity and res.identity or "",
                    "mobile":res.mobile and res.mobile or "",
                    "birthday":res.birthday and res.birthday or "",
                }

        response = request.make_response(json.dumps(data,ensure_ascii=False), [('Content-Type', 'application/json')])
        return response.make_conditional(request.httprequest)

    @http.route("/web/rhwl_gene/images/",type="http",auth="user")
    def index(self,**kw):
        fname = os.path.join(os.path.split(os.path.split(__file__)[0])[0],"static/webcam.html")
        f=open(fname,"r")
        html=f.readlines()
        f.close()
        return ''.join(html)
        return """<html><head><script>
                    window.location = '/rhwl_gene/static/webcam.html';
                </script></head></html>
                """
# assume data contains your decoded image


