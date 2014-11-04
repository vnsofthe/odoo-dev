# -*- coding: utf-8 -*-

from openerp import http
from openerp.http import request
from openerp.addons.base.res.res_users import res_users
import json
class WebClient(http.Controller):
    @http.route('/web/applogin', type='http', auth="none")
    def login(self):
        if request.httprequest.data:
            data = json.loads(request.httprequest.data)
            if not (data.get('dbname') and data.get('login') and data.get('password')):
                res={
                    "statu":500,
                    "errtext":u"参数名称不正确。"
                }
            else:
                if data.get("dbname") not in http.db_list():
                    res={
                        "statu":500,
                        "errtext":u"数据库不存在。"
                    }
                else:
                    request.session.db = data.get('dbname')
                    uid = request.session.authenticate(data.get('dbname'),data.get('login'),data.get('password'))
                    if uid:
                        res={"statu":200}
                        user=request.session.model('res.users').read(uid)
                        res["username"]=user.get("name")
                        if not user.get("partner_id"):
                            res['usertype']=0 #没有关联业务人员，则不是内部用户，也不是外部用户
                        else:
                            partner = request.session.model('res.partner').read(user.get("partner_id")[0])
                            if partner.get("is_company"):
                                if  partner.get("id")==1:
                                    res['usertype']=1 #内部人员
                                else:
                                    res['usertype']=2 #外部人员
                                res['company']=partner.get("name")
                            else:
                                if partner.get("parent_id"):
                                    parent = request.session.model('res.partner').read(partner.get("parent_id")[0])
                                    if parent.get("id")==1:
                                        res['usertype']=1 #内部人员
                                    else:
                                         res['usertype']=2 #外部人员
                                    res['company']=parent.get("name")
                                else:
                                    res['usertype']=0
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

        response = request.make_response(json.dumps(res), [('Content-Type', 'application/json')])
        return response.make_conditional(request.httprequest)