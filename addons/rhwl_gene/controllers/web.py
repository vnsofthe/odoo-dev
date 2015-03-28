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
_logger = logging.getLogger(__name__)

class gene(http.Controller):
    @http.route("/web/api/gene/pic/",type="http",auth="none")
    def imagepost(self,**kw):
        registry = RegistryManager.get(request.session.db)
        obj = registry.get("rhwl.easy.genes")
        with registry.cursor() as cr:
            id = obj.search(cr,SUPERUSER_ID,[("name","=",kw.get("no"))])
            if not id:
                return "NO_DATA_FOUND"
            file_like = cStringIO.StringIO(kw.get("img1").split(";")[-1].split(",")[-1].decode('base64','strict'))
            img = Image.open(file_like)
            width,height = img.size
            file_like2 = cStringIO.StringIO(kw.get("img2").split(";")[-1].split(",")[-1].decode('base64','strict'))
            img2 = Image.open(file_like2)

            region = img2.crop((0,0,width/2,height))
            img.paste(region, (width/2, 0,width,height))
            obj.write(cr,SUPERUSER_ID,id,{"img":base64.encodestring(img.tostring("jpeg",img.mode))})
            cr.commit()
            return "OK"


# assume data contains your decoded image


