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
_logger = logging.getLogger(__name__)
content_m=[("前言",1,1),
            ("致辞",2,2),
            ("个人信息",3,3),
            ["目录",
                [
                    ["关于您基因检测报告的说明",[("服务项目介绍",8,8),("检测报告解读示例",9,12)]],
                    ["关于您健康综合评估和指导建议",
                        [
                            ["肿瘤专项相关疾病预防",
                                [("肿瘤类疾病高危警示",14,14),("肿瘤类疾病易感性综合评估",15,16),("肿瘤类疾病环境风险因素分析与指导",17,18)]
                            ]
                        ]
                    ]
                ]
            ]
           ]

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

    @http.route("/web/api/genes/weixin/",type="http",auth="none")
    def _get_rhwl_api_weixin(self,**kw):
        res = self.check_userinfo(kw)
        data = {}
        if res.get('statu')==200:
            registry = RegistryManager.get(request.session.db)
            with registry.cursor() as cr:
                sample = registry.get("rhwl.easy.genes")
                log = registry.get("rhwl.easy.genes.log")
                id = sample.search(cr,SUPERUSER_ID,[("name","=",res.get("params").get("id"))])
                if id:
                    obj = sample.browse(cr,SUPERUSER_ID,id,context=self.CONTEXT)

                    data["name"] = obj.name.encode('utf-8')
                    data["stateList"]=[
                        ["已收件","等待中",""],
                        ["已出实验结果","等待中",""],
                		["已出报告","等待中",""]
                    ]
                    log_id=log.search(cr,SUPERUSER_ID,[("genes_id","=",id[0]),("data","in",['except','except_confirm','confirm','img'])],order="date")
                    if log_id:
                        log_obj=log.browse(cr,SUPERUSER_ID,log_id[0],context=self.CONTEXT)
                        data["stateList"][0][1]="完成"
                        data["stateList"][0][2]=(datetime.datetime.strptime(log_obj.date,"%Y-%m-%d %H:%M:%S") + datetime.timedelta(hours=8)).strftime("%Y/%m/%d %H:%M:%S")
                    log_id=log.search(cr,SUPERUSER_ID,[("genes_id","=",id[0]),("data","in",['dna_except','dna_ok','report','ok'])],order="date")
                    if log_id:
                        log_obj=log.browse(cr,SUPERUSER_ID,log_id[0],context=self.CONTEXT)
                        data["stateList"][1][1]="完成"
                        data["stateList"][1][2]=(datetime.datetime.strptime(log_obj.date,"%Y-%m-%d %H:%M:%S") + datetime.timedelta(hours=8)).strftime("%Y/%m/%d %H:%M:%S")
                    log_id=log.search(cr,SUPERUSER_ID,[("genes_id","=",id[0]),("data","in",['report_done','result_done','deliver','done'])],order="date")
                    if log_id:
                        log_obj=log.browse(cr,SUPERUSER_ID,log_id[0],context=self.CONTEXT)
                        data["stateList"][2][1]="完成"
                        data["stateList"][2][2]=(datetime.datetime.strptime(log_obj.date,"%Y-%m-%d %H:%M:%S") + datetime.timedelta(hours=8)).strftime("%Y/%m/%d %H:%M:%S")
                cr.commit()
        else:
            data=res
        _logger.error(data)
        response = request.make_response(json.dumps(data,ensure_ascii=False), [('Content-Type', 'application/json')])
        return response.make_conditional(request.httprequest)

# assume data contains your decoded image


