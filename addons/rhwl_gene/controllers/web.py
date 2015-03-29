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
            obj.write(cr,request.uid,id,{"img":base64.encodestring(img.tostring("jpeg",img.mode))})
            cr.commit()
            return "OK"

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


