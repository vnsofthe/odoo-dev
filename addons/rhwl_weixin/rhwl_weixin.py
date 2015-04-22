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
import logging

_logger = logging.getLogger(__name__)
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
        "sampleno":fields.char("sample No"),
        "is_jobmanager":fields.boolean(u"易感数据/报告数据交换通知"),
        "is_notice":fields.boolean(u"易感信息状态通知")
    }

class rhwl_config(osv.osv):
    _name = "rhwl.weixin.base"

    _columns = {
        "appid":fields.char("AppID"),
        "appsecret":fields.char("AppSecret"),
        "token":fields.char("Token",readonly=True),
        "token_create":fields.datetime("TokenCreate",readonly=True),
        "expires_in":fields.integer("Expires_IN",readonly=True),
        "user_menu":fields.text("User Menu"),
        "ticket":fields.char("Ticket",readonly=True),
        "ticket_create":fields.datetime("TicketCreate",readonly=True),
        "ticket_expires":fields.integer("Ticket Expires",readonly=True)
    }

    def _get_ticket(self,cr,uid,context=None):
        arg={
            "access_token":"",
            "type":"jsapi"
        }
        ids = self.search(cr,uid,[],limit=1)
        obj = self.browse(cr,uid,ids,context=context)
        if not obj.ticket or (datetime.datetime.now() - datetime.datetime.strptime(obj.ticket_create,tools.DEFAULT_SERVER_DATETIME_FORMAT)).seconds > (obj.ticket_expires - 30):
            arg['access_token'] = self._get_token(cr,uid,context=context)
            s=requests.post("https://api.weixin.qq.com/cgi-bin/ticket/getticket",params=arg)
            ref = s.content
            s.close()
            res = eval(ref)
            if res.get("errcode")==0:
                self.write(cr,uid,obj.id,{"ticket":res.get("ticket"),"ticket_create":fields.datetime.now(),"ticket_expires":res.get("expires_in")})
            else:
                raise osv.except_osv("错误",res.get("errmsg"))
            return res.get("ticket")
        elif obj.token:
            return obj.ticket.encode('utf-8')

    def _get_token(self,cr,uid,context=None):
        arg={
            "grant_type":"client_credential",
            "appid":"",
            "secret":"",
        }
        ids = self.search(cr,uid,[],limit=1)
        obj = self.browse(cr,uid,ids,context=context)

        if (not obj.token) or (datetime.datetime.now() - datetime.datetime.strptime(obj.token_create,tools.DEFAULT_SERVER_DATETIME_FORMAT)).total_seconds() > (obj.expires_in - 30):
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
            _logger.info("Get New Token:"+res.get("access_token"))
            return res.get("access_token")
        elif obj.token:
            _logger.info("Get Old Token:"+obj.token.encode('utf-8'))
            return obj.token.encode('utf-8')

    def action_token(self,cr,uid,ids,context=None):
        self._get_token(cr,uid,context)

    def _get_menu_detail_json(self,cr,uid,ids,context=None):
        d={
            "sub_button":[],
        }
        obj = self.pool.get("rhwl.weixin.usermenu").browse(cr,uid,ids,context=context)
        if obj.details:
            d["name"] = obj.name.encode('utf-8')
            for i in obj.details:
                dic={"type":i.type.encode('utf-8'),"name":i.name.encode('utf-8'),}
                if i.type=="view":
                    dic["url"]=i.url.encode('utf-8')
                elif i.type=="click":
                    dic["key"]=i.key.encode('utf-8')

                d['sub_button'].append(dic)
            return d
        else:
            d={}
            d["type"] = obj.type.encode('utf-8')
            d["name"] = obj.name.encode('utf-8')
            if obj.type=="view":d["url"]=obj.url.encode('utf-8')
            if obj.type=="click":d["key"]=obj.key.encode('utf-8')
            return d

    def _get_menu_json(self,cr,uid,context=None):
        m={
            "button":[],
        }
        ids = self.pool.get("rhwl.weixin.usermenu").search(cr,uid,[],context=context)
        if not ids:
            raise osv.except_osv(u"错误",u"您还没有配置用户自定义菜单内容。")

        if isinstance(ids,(long,int)):
            ids = [ids,]
        for i in ids:
            m['button'].append(self._get_menu_detail_json(cr,uid,i,context=context))
        return m

    def action_usermenu(self,cr,uid,ids,context=None):
        args={
            "access_token":""
        }
        for i in self.browse(cr,uid,ids,context=context):
            args["access_token"] = self._get_token(cr,uid,context)
            i.user_menu = str(self._get_menu_json(cr,uid,context=context))

            s=requests.post("https://api.weixin.qq.com/cgi-bin/menu/create",
                            params=args,
                            data=json.dumps(eval(i.user_menu),ensure_ascii=False),
                            headers={'content-type': 'application/json; encoding=utf-8'},allow_redirects=False)
            ref = s.content
            s.close()
            res = eval(ref)
            if res.get("errcode")!=0:
                raise osv.except_osv("错误"+str(res.get("errcode")),res.get("errmsg"))

    def send_template1(self,cr,uid,to_user,json_dict,context=None):
        id = self.pool.get("rhwl.weixin").search(cr,SUPERUSER_ID,[("user_id","=",to_user)])
        if not id:return
        obj = self.pool.get("rhwl.weixin").browse(cr,SUPERUSER_ID,id)
        json_dict["touser"]=obj.openid.encode('utf-8')
        if json_dict["url"]:
            json_dict["url"] += "?openid="+obj.openid.encode('utf-8')
        token=self._get_token(cr,SUPERUSER_ID,context)
        s=requests.post("https://api.weixin.qq.com/cgi-bin/message/template/send",
                            params={"access_token":token},
                            data=json.dumps(json_dict,ensure_ascii=False),
                            headers={'content-type': 'application/json; encoding=utf-8'},allow_redirects=False)
        ref = s.content
        s.close()

    def send_template2(self,cr,uid,json_dict,col,context=None):
        template= {
                    "touser":"OPENID",
                    "template_id":"D2fDRIhwFe9jpHgLtTjkRy5jOz_AqQnvuGzpYQFkgRs",
                    "url":"",
                    "topcolor":"#FF0000",
                    "data":{
                            "first": {"value":json_dict["first"],"color":"#173177"},
                            "keyword1":{"value":json_dict["keyword1"],"color":"#173177"},
                            "keyword2":{"value":json_dict["keyword2"],"color":"#173177"},
                            "keyword3":{"value":json_dict["keyword3"],"color":"#173177"},
                            "remark":{"value":json_dict["remark"],"color":"#173177"}
                    }
                }
        id = self.pool.get("rhwl.weixin").search(cr,SUPERUSER_ID,[(col,"=",True)])
        for i in id:
            obj = self.pool.get("rhwl.weixin").browse(cr,SUPERUSER_ID,i,context=context)
            token=self._get_token(cr,SUPERUSER_ID,context)
            template["touser"]=obj.openid.encode('utf-8')

            s=requests.post("https://api.weixin.qq.com/cgi-bin/message/template/send",
                            params={"access_token":token},
                            data=json.dumps(template,ensure_ascii=False),
                            headers={'content-type': 'application/json; encoding=utf-8'},allow_redirects=False)
            ref = s.content
            s.close()

class rhwl_usermenu(osv.osv):
    _name = "rhwl.weixin.usermenu"
    _columns={
        "type":fields.selection([("click","click"),("view","view")],"Type"),
        "name":fields.char("Name"),
        "key":fields.char("Key"),
        "url":fields.char("URL"),
        "details":fields.one2many("rhwl.weixin.usermenu2","parent","Detail"),
        "seq":fields.integer("Seq"),
    }
    _order = "seq asc"

class rhwl_usermenu2(osv.osv):
    _name = "rhwl.weixin.usermenu2"
    _columns={
        "type":fields.selection([("click","click"),("view","view")],"Type"),
        "name":fields.char("Name"),
        "key":fields.char("Key"),
        "url":fields.char("URL"),
        "need_user":fields.boolean("Need UserID"),
        "parent":fields.many2one("rhwl.weixin.usermenu","Parent"),
        "htmlmsg":fields.one2many("rhwl.weixin.htmlmsg","menu","HtmlMsg"),
        "seq":fields.integer("Seq"),
    }
    _order = "seq asc"

class rhwl_htmlmsg(osv.osv):
    _name = "rhwl.weixin.htmlmsg"
    _columns={
        "menu":fields.many2one("rhwl.weixin.usermenu2","Menu"),
        "title":fields.char("Title"),
        "description":fields.char("Description"),
        "picurl":fields.char("PicUrl"),
        "url":fields.char("Url"),
        "seq":fields.integer("Seq"),
    }
    _order = "menu,seq asc"
#AppID(应用ID)wx4c30a421cfb8be51
#AppSecret(应用密钥)d33521e37f782bfcda0373faf0ae2ba8 隐藏 重置