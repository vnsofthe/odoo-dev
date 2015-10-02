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

class gene(http.Controller):
    CONTEXT={'lang': "zh_CN",'tz': "Asia/Shanghai"}

    def get_dbname(self):
        if config.get('api_db'):
            dname = config['api_db']
        else:
            db_names = openerp.service.db.exp_list(True)
            dname = db_names[0]
        return dname and dname or None

    def check_userinfo(self,kw=None):
        if request.httprequest.data or kw:
            data = {}
            if request.httprequest.data:
                data = json.loads(request.httprequest.data)
            if kw:
                data.update(kw)
                #data = json.JSONEncoder.encode(json.loads(kw))
            if data.get("openid",'0')=='0' and not (data.get('Username') and data.get('Pwd')):
                res={
                    "statu":500,
                    "errtext":u"参数中无登录帐号和密码信息。"
                }
            else:
                if data.get("Username"):
                    DBNAME = self.get_dbname()
                    uid = request.session.authenticate(DBNAME,data.get('Username'),data.get('Pwd'))
                elif data.get("openid"):
                    registry = RegistryManager.get(request.session.db)
                    weixin = registry.get("rhwl.weixin")

                    with registry.cursor() as cr:
                        id = weixin.search(cr,SUPERUSER_ID,[('openid','=',data.get("openid"))],context=self.CONTEXT)
                        if id:
                            obj= weixin.browse(cr,SUPERUSER_ID,id,context=self.CONTEXT)
                            uid = obj.user_id.id

                if uid:
                    res={"statu":200,"userid":uid,"params":data}
                else:
                    res={
                        "statu":500,
                        "errtext":u"登录名与密码不正确。"
                    }
        else:
            res={
                "statu":500,
                "errtext":u"请传入验证参数"
            }
        return res

    @http.route("/web/api/gene_new/pic/",type="http",auth="user")
    def imagepost(self,**kw):
        registry = RegistryManager.get(request.session.db)
        obj = registry.get("rhwl.easy.genes.new")
        with registry.cursor() as cr:
            id = obj.search(cr,request.uid,[("name","=",kw.get("no"))])
            if not id:
                return "NO_DATA_FOUND"
            file_like = cStringIO.StringIO(kw.get("img1").split(";")[-1].split(",")[-1].decode('base64','strict'))
            img = Image.open(file_like)
            #判断是单张还是两张拍照，如果是单张，则旋转后保存，如果是两张，则截取后合并保存
            if not kw.has_key("img2"):
                img = img.transpose(Image.ROTATE_270)
            else:
                width,height = img.size
                file_like2 = cStringIO.StringIO(kw.get("img2").split(";")[-1].split(",")[-1].decode('base64','strict'))
                img2 = Image.open(file_like2)

                region = img2.crop((0,0,width/2,height))
                img.paste(region, (width/2, 0,width,height))
            val={"img":base64.encodestring(img.tostring("jpeg",img.mode))}
            if kw.get("etx",""):
                val["except_note"]=kw.get("etx")
                val["except_type"]=kw.get("etx_type")
                obj.write(cr,request.uid,id,{"except_note":kw.get("etx"),"state":"except"},context={'lang': "zh_CN",'tz': "Asia/Shanghai","name":kw.get("no")})
            obj._post_images(cr,request.uid,id,val["img"],context={'lang': "zh_CN",'tz': "Asia/Shanghai","name":kw.get("no")})
            #obj.write(cr,request.uid,id,val,context={'lang': "zh_CN",'tz': "Asia/Shanghai","name":kw.get("no")})
            if (not val.has_key("except_note")) and kw.get("is_confirm")=="true":
                o=obj.browse(cr,request.uid,id,context={'lang': "zh_CN",'tz': "Asia/Shanghai"})
                if o.state=="draft":
                    obj.action_state_confirm(cr,request.uid,id,context={'lang': "zh_CN",'tz': "Asia/Shanghai"})


            return "OK"

    @http.route("/web/rhwl_gene_new/get/",type="http",auth="user")
    def get_detail(self,**kw):
        registry = RegistryManager.get(request.session.db)
        obj = registry.get("rhwl.easy.genes.new")
        sexdict={'M':u'男','F':u'女'}
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
                    "hospital":res.hospital.name,
                    "package":res.package_id.name,
                }

        response = request.make_response(json.dumps(data,ensure_ascii=False), [('Content-Type', 'application/json')])
        return response.make_conditional(request.httprequest)

    @http.route("/web/rhwl_gene_new/images/",type="http",auth="user")
    def index(self,**kw):
        fname = os.path.join(os.path.split(os.path.split(__file__)[0])[0],"static/webcam_new.html")
        f=open(fname,"r")
        html=f.readlines()
        f.close()
        return ''.join(html)


# assume data contains your decoded image


