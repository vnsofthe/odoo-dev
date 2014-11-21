# -*- coding: utf-8 -*-

from openerp import http
from openerp.http import request
from openerp.addons.base.res.res_users import res_users
import json,simplejson
import openerp.tools.config as config
import openerp
from openerp import SUPERUSER_ID
from openerp.modules.registry import RegistryManager

class WebClient(http.Controller):
    def get_dbname(self):
        if config.get('api_db'):
            dname = config['api_db']
        else:
            db_names = openerp.service.db.exp_list(True)
            dname = db_names[0]
        return dname and dname or None

    @http.route('/web/crmapp/login/', type='http', auth="public",website=True)
    def login(self,**kw):
        print "*"*40
        if request.httprequest.data or kw:
            if request.httprequest.data:
                data = json.loads(request.httprequest.data)
            else:
                data = kw
                #data = json.JSONEncoder.encode(json.loads(kw))
            if not (data.get('Username') and data.get('Pwd')):
                res={
                    "statu":500,
                    "errtext":u"参数名称或个数不正确。"
                }
            else:
                DBNAME = self.get_dbname()
                print DBNAME
                uid = request.session.authenticate(DBNAME,data.get('Username'),data.get('Pwd'))
                if uid:
                    res={"statu":200}
                    res['userid'] = uid
                    registry = RegistryManager.get(DBNAME)
                    with registry.cursor() as cr:
                            user = registry.get('res.users')
                            partner = registry.get('res.partner')
                            warehouse = registry.get('stock.warehouse')
                            u = user.browse(cr,SUPERUSER_ID,uid)
                            p = partner.browse(cr,SUPERUSER_ID,u.partner_id.id,context=None)
                            if not p.is_company:
                                p = partner.browse(cr,SUPERUSER_ID,p.parent_id.id,context=None)
                            res['hospitalName'] = p.name
                            w = warehouse.search(cr,SUPERUSER_ID,[('partner_id','=',p.id)])
                            w = warehouse.browse(cr,SUPERUSER_ID,w)
                            res['AllCount'] = w.qty
                            cr.commit()
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

        response = request.make_response(json.dumps(res,ensure_ascii=False), [('Content-Type', 'application/json')])
        return response.make_conditional(request.httprequest)

    @http.route('/web/api/hospital/', type='http', auth="public")
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
