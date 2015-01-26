# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
import datetime
import re
import requests
import openerp.tools as tools
import time
import json
class rhwl_weixin(osv.osv):
    _name = "rhwl.weixin"

    _columns = {
        "openid":fields.char("openId",size=64,required=True,select=True),
        "active":fields.boolean("Active"),
        "user_id":fields.many2one("res.users",string=u"关联用户"),
        "telno":fields.char("Tele No"),
        "state":fields.selection([('draft','draft'),('process','process'),('pass','pass')],string="State"),
        "checkNum":fields.char(u"验证码"),
        "checkDateTime":fields.datetime(u"验证码发送时间"),
        "sampleno":fields.char("sample No")
    }

class rhwl_config(osv.osv):
    _name = "rhwl.weixin.base"

    _columns = {
        "appid":fields.char("AppID"),
        "appsecret":fields.char("AppSecret"),
        "token":fields.char("Token",readonly=True),
        "token_create":fields.datetime("TokenCreate",readonly=True),
        "expires_in":fields.integer("Expires_IN",readonly=True),
        "user_menu":fields.text("User Menu")
    }

    def _get_token(self,cr,uid,context=None):
        arg={
            "grant_type":"client_credential",
            "appid":"",
            "secret":"",
        }
        ids = self.search(cr,uid,[],limit=1)
        obj = self.browse(cr,uid,ids,context=context)

        if not obj.token or (datetime.datetime.now() - datetime.datetime.strptime(obj.token_create,tools.DEFAULT_SERVER_DATETIME_FORMAT)).seconds > (obj.expires_in - 30):
            arg["appid"]=obj.appid
            arg["secret"]=obj.appsecret
            s=requests.post("https://api.weixin.qq.com/cgi-bin/token",params=arg)
            ref = s.content
            s.close()
            res = eval(ref)
            if res.get("access_token"):
                self.write(cr,uid,obj.id,{"token":res.get("access_token"),"token_create":fields.datetime.now(),"expires_in":res.get("expires_in")})
            else:
                raise osv.except_osv("错误",res.get("errmsg"))
            return res.get("access_token")
        elif obj.token:
            return obj.token.encode('utf-8')

    def action_token(self,cr,uid,ids,context=None):
        self._get_token(cr,uid,context)


    def action_usermenu(self,cr,uid,ids,context=None):
        args={
            "access_token":""
        }
        for i in self.browse(cr,uid,ids,context=context):
            args["access_token"] = self._get_token(cr,uid,context)

            s=requests.post("https://api.weixin.qq.com/cgi-bin/menu/create",
                            params=args,
                            data=json.dumps(eval(i.user_menu.encode("utf-8")),ensure_ascii=False),
                            headers={'content-type': 'application/json; encoding=utf-8'},allow_redirects=False)
            ref = s.content
            s.close()
            res = eval(ref)
            if res.get("errcode")!=0:
                raise osv.except_osv("错误"+str(res.get("errcode")),res.get("errmsg"))

#AppID(应用ID)wx4c30a421cfb8be51
#AppSecret(应用密钥)d33521e37f782bfcda0373faf0ae2ba8 隐藏 重置