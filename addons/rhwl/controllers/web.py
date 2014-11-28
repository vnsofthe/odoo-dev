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
from openerp.tools.translate import _
from .. import rhwl_sale

_logger = logging.getLogger(__name__)
class WebClient(http.Controller):
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
            if not (data.get('Username') and data.get('Pwd')):
                res={
                    "statu":500,
                    "errtext":u"参数中无登录帐号和密码信息。"
                }
            else:
                DBNAME = self.get_dbname()
                uid = request.session.authenticate(DBNAME,data.get('Username'),data.get('Pwd'))
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

    @http.route('/web/crmapp/login/', type='http', auth="public",website=True)
    def login(self,**kw):
        res = self.check_userinfo(kw)

        if res['statu']==200:
            registry = RegistryManager.get(request.session.db)
            with registry.cursor() as cr:
                    user = registry.get('res.users')
                    partner = registry.get('res.partner')
                    warehouse = registry.get('stock.warehouse')
                    u = user.browse(cr,SUPERUSER_ID,res['userid'])
                    p = partner.browse(cr,SUPERUSER_ID,u.partner_id.id,context=None)
                    if not p.is_company:
                        p = partner.browse(cr,SUPERUSER_ID,p.parent_id.id,context=None)
                    res['hospitalName'] = p.name
                    w = warehouse.search(cr,SUPERUSER_ID,[('partner_id','=',p.id)])
                    w = warehouse.browse(cr,SUPERUSER_ID,w)
                    res['AllCount'] = w.qty
                    cr.commit()

        response = request.make_response(json.dumps(res,ensure_ascii=False), [('Content-Type', 'application/json')])
        return response.make_conditional(request.httprequest)

    @http.route('/web/api/hospital/', type='http', auth="none")
    def hospital(self):
        request.session.db = self.get_dbname()
        registry = RegistryManager.get(request.session.db)
        with registry.cursor() as cr:
            try:
                u = registry.get('res.partner')
                data = u.get_hospital(cr, SUPERUSER_ID, context=None)
                cr.commit()
            except:
                return "Get Hospital Error "

        #request.session.authenticate(request.session.db,"admin","123")
        #data = request.session.model("res.partner").get_hospital()
        return json.dumps(data,ensure_ascii=False)
        #response = request.make_response(simplejson.dumps(data), [('Content-Type', 'application/json;charset=utf-8')])
        #return response.make_conditional(request.httprequest)

    @http.route("/web/crmapp/result/",type="http",auth="none")
    def app_result(self,**kw):
        res = self.check_userinfo(kw)
        data = {}
        if res.get('statu')==200:
            uid = res.get("userid")
            if id:
                registry = RegistryManager.get(request.session.db)
                with registry.cursor() as cr:
                    sampleone = registry.get('sale.sampleone')
                    if res.get("params").get("name"):
                        reuseid = sampleone.search(cr,uid,['|',('yfxm','ilike',res.get("params").get("name")),('name','ilike',res.get("params").get("name"))])
                        data=[]
                        for i in sampleone.browse(cr,uid,reuseid,context=self.CONTEXT):
                            data.append({
                                "time":i.cx_date,
                                "name":i.yfxm,
                                "code":i.name,
                                "status":rhwl_sale.rhwl_sale_state_select.get(i.state)
                            })
                    else:
                        reuseid = sampleone.search(cr,uid,[('cx_date','<=',datetime.date.today()),('cx_date','>',datetime.timedelta(-7) + datetime.date.today())],context={'tz': "Asia/Shanghai"})
                        temp = {}
                        except_count=0
                        for i in sampleone.browse(cr,uid,reuseid,context=self.CONTEXT):
                            if not temp.has_key(i.cx_date):
                                temp[i.cx_date]=[]
                            if i.check_state in ['reuse','except']:
                                except_count +=1
                            temp[i.cx_date].append({
                                "name":i.yfxm,
                                "code":i.name,
                                "status":rhwl_sale.rhwl_sale_state_select.get(i.state)
                            })
                        data = [{"exception":str(except_count)+u"个"},]
                        for k,v in temp.items():
                            data.append({"time":k,"datas":v})
                    cr.commit()
        else:
            data = res

        return json.dumps(data,ensure_ascii=False)


    @http.route("/web/crmapp/except/",type="http",auth="none")
    def app_except(self,**kw):
        res = self.check_userinfo(kw)
        data = {}
        if res.get('statu')==200:

            uid = res.get("userid")
            if id:
                registry = RegistryManager.get(request.session.db)
                with registry.cursor() as cr:
                    sampleone = registry.get('sale.sampleone.exception')
                    reuseid = sampleone.search(cr,uid,[('state','not in',['cancel','reuse'])])
                    data=[]
                    for i in sampleone.browse(cr,uid,reuseid,context=self.CONTEXT):
                        data.append({
                            "time":i.cx_date,
                            "name":i.yfxm,
                            "numbers":i.name,
                            "status":i.state
                        })
                    cr.commit()
        else:
            data = res
        return json.dumps(data,ensure_ascii=False)

    @http.route("/web/crmapp/reuse/",type="http",auth="none")
    def app_reuse(self,**kw):
        res = self.check_userinfo(kw)
        data = {}
        if res.get('statu')==200:

            uid = res.get("userid")
            if id:
                registry = RegistryManager.get(request.session.db)
                with registry.cursor() as cr:
                    sampleone = registry.get('sale.sampleone.reuse')
                    reuseid = sampleone.search(cr,uid,[('state','not in',['cancel','reuse'])])
                    data=[]
                    for i in sampleone.browse(cr,uid,reuseid,context=self.CONTEXT):
                        data.append({
                            "time":i.cx_date,
                            "name":i.yfxm,
                            "numbers":i.name,
                            "status":i.state
                        })
                    cr.commit()
        else:
            data = res
        return json.dumps(data,ensure_ascii=False)

    @http.route("/web/crmapp/deliver/",type="http",auth="none")
    def app_reuse(self,**kw):
        res = self.check_userinfo(kw)
        data = {}
        if res.get('statu')==200:
            id = res.get("params").get("packageID")
            detail = res.get("params").get("demos")
            #[{ "code":"X140545" , "preCode":"X145655" },{ "code":"4X32871" , "preCode":"" },{ "code":"4Y45474" , "preCode":"" } ]}';
            uid =  res.get("userid")
            if id:
                registry = RegistryManager.get(request.session.db)
                with registry.cursor() as cr:
                    express = registry.get('stock.picking.express')
                    dobj =registry.get("stock.picking.express.detail")
                    mid = express.create(cr,uid,{"num_express":id},context=self.CONTEXT)
                    for j in detail:
                        did = dobj.create(cr,uid,{"parent_id":mid,"number_seq":j.code,"number_seq_ori":j.preCode,"out_flag":True},context=self.CONTEXT)
                        express.write(cr,uid,mid,{'detail_ids':[[6, False, [did]]]})
                    express.action_send(cr,uid,mid,context=self.CONTEXT)
                    data['statu'] = 200
                    cr.commit()
        else:
            data = res
        return json.dumps(data,ensure_ascii=False)

    @http.route("/web/crmapp/express/",type="http",auth="none")
    def app_reuse(self,**kw):
        res = self.check_userinfo(kw)
        data = {}
        if res.get('statu')==200:
            startTime = res.get("params").get("startTime")
            endTime = res.get("params").get("endTime")
            uid =  res.get("userid")
            if startTime and endTime:
                registry = RegistryManager.get(request.session.db)
                with registry.cursor() as cr:
                    express = registry.get('stock.picking.express')
                    ids = express.search(cr,uid,[('date','>=',startTime),('date','<=',endTime),'|',('deliver_user.id','=',uid),('receiv_user.id','=',uid)])
                    data[' hisinfo']=[]
                    for i in express.browse(cr,uid,ids,self.CONTEXT):
                        data[' hisinfo'].append({
                             "time":i.date,
                            "logIdCompany": i.num_express+"-"+i.deliver_id.name,
                            "state": i.state
                        })
                    cr.commit()
        else:
            data = res
        return json.dumps(data,ensure_ascii=False)

    @http.route("/web/crmapp/receive/",type="http",auth="none")
    def app_reuse(self,**kw):
        res = self.check_userinfo(kw)
        data = {}
        if res.get('statu')==200:
            id = res.get("params").get("goodsId")
            uid =  res.get("userid")
            if id:
                registry = RegistryManager.get(request.session.db)
                with registry.cursor() as cr:
                    express = registry.get('stock.picking.express')
                    ids = express.search(cr,uid,[('num_express','=',id)])
                    data = {
                        "receiv_real_qty":res.get("params").get("actualNumber"),
                        "receiv_real_user": uid,
                        "receiv_real_date": datetime.datetime.now(),
                    }
                    express.write(cr,uid,ids,data,context=self.CONTEXT)
                    express.action_ok(cr,uid,ids,context=self.CONTEXT)
                    data['statu'] = 200

                    cr.commit()
        else:
            data = res
        return json.dumps(data,ensure_ascii=False)

    @http.route("/web/crmapp/goodsnum/",type="http",auth="none")
    def app_reuse(self,**kw):
        res = self.check_userinfo(kw)
        data = {}
        if res.get('statu')==200:
            id = res.get("params").get("goodsID")
            uid =  res.get("userid")
            if id:
                registry = RegistryManager.get(request.session.db)
                with registry.cursor() as cr:
                    express = registry.get('stock.picking.express')
                    ids = express.search(cr,uid,[('num_express','=',id)])
                    obj = express.browse(cr,uid,ids)
                    data = {
                        "goodsNum":obj.product_qty,
                    }
                    cr.commit()
        else:
            data = res
        return json.dumps(data,ensure_ascii=False)

    @http.route("/web/crmapp/woman/",type="http",auth="none")
    def app_reuse(self,**kw):
        res = self.check_userinfo(kw)
        data = {}
        if res.get('statu')==200:
            id = res.get("params").get("pregnantWomanID") #样品编码
            uid = res.get("userid")
            if id:
                registry = RegistryManager.get(request.session.db)
                with registry.cursor() as cr:
                    sampleone = registry.get('sale.sampleone')
                    reuseid = registry.get('sale.sampleone.reuse').search(cr,uid,[('name','=',id)])

                    ids = sampleone.search(cr,uid,[('name','=',id)])
                    obj = sampleone.browse(cr,uid,ids)
                    data = {
                        "pregnantWomanID":obj.name,
                        "pregnantWomanName":obj.yfxm,
                        "gestationalWeeks":str(obj.yfyzweek)+u"周+"+str(obj.yfyzday)+u"天",
                        "takeBloodTime":obj.cx_date,
                        "state":obj.check_state,
                        "phoneNumber":obj.yftelno,
                        "emergencyCall":obj.yfjjlltel,
                        "reTakeBloodID":reuseid and registry.get('sale.sampleone.reuse').browse(cr,uid,reuseid).newname.name or "" ,
                        "report":""
                    }
                    cr.commit()

        else:
            data = res

        return json.dumps(data,ensure_ascii=False)

    @http.route("/web/api/express/",type="http",auth="none")
    def api_express(self,**kw):
        pass