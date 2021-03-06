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
import random
_logger = logging.getLogger(__name__)
MEMCACHE={}
class gbsoft_weixin(osv.osv):
    _name = "gbsoft.weixin"

    _columns = {
        "base_id":fields.many2one("gbsoft.weixin.base",u"公众号"),
        "openid":fields.char("openId",size=64,required=True,select=True),
        "active":fields.boolean("Active"),
        "user_id":fields.many2one("res.users",string=u"关联用户"),
        "telno":fields.char("Tele No"),
        "state":fields.selection([('draft','draft'),('process','process'),('pass','pass')],string="State"),
        "checkNum":fields.char(u"验证码"),
        "checkDateTime":fields.datetime(u"验证码发送时间"),
        "sampleno":fields.char("sample No"),
        "gbsoftid":fields.char("gbsoft ID",size=20,select=True),
        
    }
    _defaults={
        
    }
    def get_gbsoft_id(self,cr,uid,context=None):
        s='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        noncestr=''.join([s[random.randrange(0,s.__len__()-1)] for i in range(1,21)])
        ids = self.search(cr,uid,[("gbsoftid","=",noncestr),'|',("active","=",True),("active","=",False)])
        if not ids:
            return noncestr
        else:
            return self.get_gbsoft_id(cr,uid,context=context)

    def init(self, cr):
        ids = self.search(cr,SUPERUSER_ID,[("gbsoftid","=",False),'|',("active","=",True),("active","=",False)])
        if ids:
            for i in ids:
                self.write(cr,SUPERUSER_ID,i,{'gbsoftid':self.get_gbsoft_id(cr,SUPERUSER_ID)})
        cr.commit()

    def create(self,cr,uid,vals,context=None):
        vals["gbsoftid"] = self.get_gbsoft_id(cr,SUPERUSER_ID,context=context)
        return super(gbsoft_weixin,self).create(cr,uid,vals,context=context)

    def action_user_bind(self,cr,code,openid,uid):
        base_obj = self.pool.get("gbsoft.weixin.base")
        id=base_obj.search(cr,SUPERUSER_ID,[("code","=",code)])
        ids=self.search(cr,SUPERUSER_ID,[("base_id","=",id[0]),'|',("openid","=",openid),("gbsoftid","=",openid)])
        if ids:
            self.write(cr,SUPERUSER_ID,ids,{"user_id":uid})
        else:
            self.create(cr,SUPERUSER_ID,{"base_id":id[0],"openid":openid,"active":True,"user_id":uid,"state":"draft"})

class gbsoft_config(osv.osv):
    _name = "gbsoft.weixin.base"

    _columns = {
        "name":fields.char("Name",size=20),
        "original_id":fields.char("Original ID",size=20),
        "code":fields.char("Code",size=10),
        "token_flag":fields.char(u"Token(令牌)",size=10),
        "appid":fields.char("AppID"),
        "appsecret":fields.char("AppSecret"),
        "token":fields.char("Token",readonly=True),
        "token_create":fields.datetime("TokenCreate",readonly=True),
        "expires_in":fields.integer("Expires_IN",readonly=True),
        "user_menu":fields.text("User Menu"),
        "ticket":fields.char("Ticket",readonly=True),
        "ticket_create":fields.datetime("TicketCreate",readonly=True),
        "ticket_expires":fields.integer("Ticket Expires",readonly=True),
        "welcome":fields.text("Welcome"),
        "users":fields.one2many("gbsoft.weixin","base_id",u"关注用户"),
        "menu":fields.one2many("gbsoft.weixin.usermenu","base_id",u"自定义菜单"),
        "is_valid":fields.boolean(u"已认证"),
        "service_type":fields.selection([("1",u"订阅号"),("2",u"服务号"),("3",u"企业号")],u"帐号类型")

    }

    def _get_memcache(self,key):
        return MEMCACHE.get(key,None)

    def _set_memcache(self,key,val):
        MEMCACHE[key]=val

    def _get_memcache_id(self,cr,original,AgentID):
        ids=self._get_memcache((original,AgentID))
        if not ids:
            if (not AgentID) or AgentID=="0":
                ids = self.search(cr,SUPERUSER_ID,[("original_id","=",original)])
            else:
                ids = self.search(cr,SUPERUSER_ID,[("original_id","=",original),("appid","=",AgentID)])
            self._set_memcache((original,AgentID),ids)
        return ids

    #用户关注时，记录用户的OpenId信息，并返回设置的欢迎文字
    def action_subscribe(self,cr,original,fromUser,AgentID="0"):
        origId=self._get_memcache_id(cr,original,AgentID)
        user = self.pool.get('gbsoft.weixin')

        for o in origId:
            id = user.search(cr,SUPERUSER_ID,[("base_id","=",o),('openid','=',fromUser),'|',('active','=',False),("active","=",True)])

            if id:
                user.write(cr,SUPERUSER_ID,id,{"active":True})
            else:
                user.create(cr,SUPERUSER_ID,{"base_id":o,'openid':fromUser,'active':True,'state':'draft'})
        cr.commit()
        obj=self.browse(cr,SUPERUSER_ID,origId[0])
        return obj.welcome

    def action_unsubscribe(self,cr,original,fromUser,AgentID="0"):
        origId=self._get_memcache_id(cr,original,AgentID)
        user = self.pool.get('gbsoft.weixin')
        for o in origId:
            id = user.search(cr,SUPERUSER_ID,[("base_id","=",o),('openid','=',fromUser)])
            if id:
               user.write(cr,SUPERUSER_ID,id,{"active":False})
        cr.commit()

    def action_event_clicked(self,cr,key,original,fromUser,appid=None):
        origId=self._get_memcache_id(cr,original,appid)
        obj=self.browse(cr,SUPERUSER_ID,origId)
        articles=self._get_htmlmsg(cr,origId[0],key)

        if articles[0]:
            userid=self._get_userid(cr,origId[0],fromUser)
            if not userid:
                articles={
                    "Title":"内部ERP帐号绑定",
                    "Description":"您查阅的功能需要授权，请先进行内部ERP帐号绑定",
                    "PicUrl":"/gbsoft_weixin/static/img/logo1.png",
                    "Url":"/gbsoft_weixin/static/weixinbind.html"
                    }
                return (obj.code.encode("utf-8"),[articles,])
            if articles[1]:
                is_has_group=False

                uobj = self.pool.get("res.users")
                for i in articles[1].split(","):
                    is_has_group = uobj.has_group(cr,userid,i)
                    if is_has_group:break
                if not is_has_group:
                    articles={
                        "Title":"访问权限不足",
                        "Description":"您查阅的功能需要特别授权，请与管理员联系。",
                        "PicUrl":"/gbsoft_weixin/static/img/logo1.png",
                        }
                    return (obj.code.encode("utf-8"),[articles,])
        _logger.debug(articles[2])
        if articles[2]:
            return (obj.code.encode("utf-8"),articles[2])
        else:
            return u"此功能在开发中，敬请稍候！"

    def action_text_input(self,cr,content,original,fromUser):
        origId=self._get_memcache_id(cr,original,None)
        obj=self.browse(cr,SUPERUSER_ID,origId)

        return u"欢迎光临"

    def _get_htmlmsg(self,cr,orig_id,key):
        msg = self.pool.get("gbsoft.weixin.usermenu2")

        id = msg.search(cr,SUPERUSER_ID,[("parent.base_id.id","=",orig_id),("key","=",key)])
        if not id:
            return (False,"",None)
        obj = msg.browse(cr,SUPERUSER_ID,id)
        if not obj.htmlmsg:
            return (obj.need_user,obj.groups,None)
        articles=[]
        for j in obj.htmlmsg:
            val={
                    "Title":j.title.encode("utf-8"),
                    "Description":j.description.encode("utf-8"),
                    "PicUrl":j.picurl.encode("utf-8"),
                }
            if j.url:
                val["Url"]=j.url and j.url.encode("utf-8") or ""
            articles.append(val)
        return (obj.need_user,obj.groups,articles)

    def _get_userid(self,cr,orig_id,openid):
        weixin = self.pool.get("gbsoft.weixin")

        id = weixin.search(cr,SUPERUSER_ID,[("base_id","=",orig_id),'|',('openid','=',openid),("gbsoftid","=",openid)])
        if id:
            obj= weixin.browse(cr,SUPERUSER_ID,id)
            return obj.user_id.id
        return None

    def _get_ticket(self,cr,uid,val,valType="code",context=None):
        arg={
            "access_token":"",
            "type":"jsapi"
        }
        ids = self.search(cr,uid,[(valType,"=",val)],limit=1)
        obj = self.browse(cr,uid,ids,context=context)
        if not obj.ticket or (datetime.datetime.now() - datetime.datetime.strptime(obj.ticket_create,tools.DEFAULT_SERVER_DATETIME_FORMAT)).total_seconds() > (obj.ticket_expires - 30):
            arg['access_token'] = self._get_token(cr,uid,val,valType,obj,context=context)
            if obj.service_type=="3":
                s=requests.post("https://qyapi.weixin.qq.com/cgi-bin/get_jsapi_ticket",params=arg)
            else:
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

    def _get_token(self,cr,uid,val,valType="code",obj=None,context=None):
        arg={
            "grant_type":"client_credential",
            "appid":"",
            "secret":"",
        }
        arg_qy={
            "corpid":"",
            "corpsecret":""
        }

        if not obj:
            ids = self.search(cr,uid,[(valType,"=",val)],limit=1)
            obj = self.browse(cr,uid,ids,context=context)

        if obj.service_type=="3":
            #企业号处理
            if (not obj.token) or (datetime.datetime.now() - datetime.datetime.strptime(obj.token_create,tools.DEFAULT_SERVER_DATETIME_FORMAT)).total_seconds() > (obj.expires_in - 30):
                arg_qy["corpid"] = obj.original_id
                arg_qy["corpsecret"] = obj.appsecret
                s=requests.post("https://qyapi.weixin.qq.com/cgi-bin/gettoken",params=arg_qy)
                ref = s.content
                s.close()
                res = eval(ref)
                if res.get("access_token"):
                    self.write(cr,uid,obj.id,{"token":res.get("access_token"),"token_create":fields.datetime.now(),"expires_in":res.get("expires_in")})
                else:
                    raise osv.except_osv("错误",res.get("errmsg"))
                return res.get("access_token")
            else:
                return obj.token.encode('utf-8')
        else:
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
        for i in self.browse(cr,uid,ids,context=context):
            self._get_token(cr,uid,None,None,i,context)

    def _get_menu_detail_json(self,cr,uid,ids,context=None):
        d={
            "sub_button":[],
        }
        obj = self.pool.get("gbsoft.weixin.usermenu").browse(cr,uid,ids,context=context)
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

    def _get_menu_json(self,cr,uid,id,context=None):
        m={
            "button":[],
        }
        ids = self.pool.get("gbsoft.weixin.usermenu").search(cr,uid,[("base_id","=",id)],context=context)
        if not ids:
            raise osv.except_osv(u"错误",u"您还没有配置用户自定义菜单内容。")

        if isinstance(ids,(long,int)):
            ids = [ids,]
        for i in ids:
            m['button'].append(self._get_menu_detail_json(cr,uid,i,context=context))
        return m

    def action_usermenu(self,cr,uid,ids,context=None):
        args={}

        for i in self.browse(cr,uid,ids,context=context):
            if i.service_type=="3":
                create_url = "https://qyapi.weixin.qq.com/cgi-bin/menu/create"
                args["access_token"] = self._get_token(cr,uid,None,None,i,context)
                args["agentid"] = i.appid
            else:
                create_url = "https://api.weixin.qq.com/cgi-bin/menu/create"
                args["access_token"] = self._get_token(cr,uid,None,None,i,context)
            i.user_menu = str(self._get_menu_json(cr,uid,i.id,context=context))

            s=requests.post(create_url,
                            params=args,
                            data=json.dumps(eval(i.user_menu),ensure_ascii=False),
                            headers={'content-type': 'application/json; encoding=utf-8'},allow_redirects=False)
            ref = s.content
            s.close()
            res = eval(ref)
            if res.get("errcode")!=0:
                raise osv.except_osv("错误"+str(res.get("errcode")),res.get("errmsg"))

    def send_template1(self,cr,uid,to_user,json_dict,context=None):
        id = self.pool.get("gbsoft.weixin").search(cr,SUPERUSER_ID,[("base_id.code","=","rhwc"),("user_id","=",to_user)])
        if not id:return
        id=id[0]
        obj = self.pool.get("gbsoft.weixin").browse(cr,SUPERUSER_ID,id)
        json_dict["touser"]=obj.openid.encode('utf-8')
        if json_dict["url"]:
            json_dict["url"] += "?openid="+obj.openid.encode('utf-8')
        token=self._get_token(cr,SUPERUSER_ID,"rhwc",context=context)
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
        id = self.pool.get("gbsoft.weixin").search(cr,SUPERUSER_ID,[(col,"=",True)])
        for i in id:
            obj = self.pool.get("gbsoft.weixin").browse(cr,SUPERUSER_ID,i,context=context)
            token=self._get_token(cr,SUPERUSER_ID,"rhwc",context=context)
            template["touser"]=obj.openid.encode('utf-8')

            s=requests.post("https://api.weixin.qq.com/cgi-bin/message/template/send",
                            params={"access_token":token},
                            data=json.dumps(template,ensure_ascii=False),
                            headers={'content-type': 'application/json; encoding=utf-8'},allow_redirects=False)
            ref = s.content
            s.close()

    def send_qy_text_ids(self,cr,uid,ids,content,context=None):
        vals={
               "touser": "",
               "toparty": "",
               "totag": "",
               "msgtype": "text",
               "agentid": None,
               "text": {
                   "content": ""
               },
               "safe":"0"
            }
        touser=[]
        if ids:
            for i in self.pool.get("gbsoft.weixin").browse(cr,uid,ids,context=context):
                touser.append(i.openid.encode('utf-8'))
                if not vals["agentid"]:
                    vals["agentid"] = i.base_id.appid.encode('utf-8')
                    token=self._get_token(cr,SUPERUSER_ID,i.base_id.code.encode('utf-8'),context=context)
            vals["touser"] = '|'.join(touser)
            vals["text"]["content"] = content.encode('utf-8')
            _logger.error(vals)
            s=requests.post("https://qyapi.weixin.qq.com/cgi-bin/message/send",
                            params={"access_token":token},
                            data=json.dumps(vals,ensure_ascii=False),
                            headers={'content-type': 'application/json; encoding=utf-8'},allow_redirects=False)
            ref = s.content
            s.close()

    def send_qy_text_openid(self,cr,uid,code,openid,content,context=None):
        ids = self.pool.get("gbsoft.weixin").search(cr,uid,[("base_id.code","=",code),("openid","=",openid)],context=context)
        self.send_qy_text_ids(cr,uid,ids,content,context=context)

    def send_qy_text(self,cr,uid,code,field_name,content,context=None):
        ids = self.pool.get("gbsoft.weixin").search(cr,uid,[("base_id.code","=",code),(field_name,"=",True)],context=context)
        self.send_qy_text_ids(cr,uid,ids,content,context=context)

    def get_dept_user(self,cr,uid,id,context=None):
        obj = self.browse(cr,uid,id,context=context)
        token=self._get_token(cr,SUPERUSER_ID,obj.code.encode("utf-8"),context=context)
        vals={
            "access_token":token,
            "department_id":1,
            "fetch_child":1,
             "status":0
        }
        s=requests.post("https://qyapi.weixin.qq.com/cgi-bin/user/simplelist",
                            params=vals,
                            headers={'content-type': 'application/json; encoding=utf-8'},allow_redirects=False)
        ref = eval(s.content)
        s.close()
        if ref["errcode"]==0:
            for i in ref["userlist"]:
                u_id = self.pool.get("gbsoft.weixin").search(cr,SUPERUSER_ID,[("base_id","=",obj.id),("openid","=",i["userid"])])
                if not u_id:
                    self.pool.get("gbsoft.weixin").create(cr,SUPERUSER_ID,{"base_id":obj.id,"openid":i["userid"],"active":True,"state":"draft"})

class gbsoft_usermenu(osv.osv):
    _name = "gbsoft.weixin.usermenu"
    _columns={
        "base_id":fields.many2one("gbsoft.weixin.base",u"公众号"),
        "type":fields.selection([("click","click"),("view","view")],"Type"),
        "name":fields.char("Name"),
        "key":fields.char("Key"),
        "url":fields.char("URL"),
        "details":fields.one2many("gbsoft.weixin.usermenu2","parent","Detail"),
        "seq":fields.integer("Seq"),
    }
    _order = "seq asc"

    def init(self, cr):
        ids = self.search(cr,SUPERUSER_ID,[("base_id","=",False)])
        if ids:
            base_id = self.pool.get("gbsoft.weixin.base").search(cr,SUPERUSER_ID,[])
            if len(base_id)==1:
                self.write(cr,SUPERUSER_ID,ids,{'base_id':base_id[0]})
        cr.commit()

class gbsoft_usermenu2(osv.osv):
    _name = "gbsoft.weixin.usermenu2"
    _columns={
        "type":fields.selection([("click","click"),("view","view")],"Type"),
        "name":fields.char("Name"),
        "key":fields.char("Key"),
        "url":fields.char("URL"),
        "need_user":fields.boolean("Need UserID"),
        "parent":fields.many2one("gbsoft.weixin.usermenu","Parent"),
        "htmlmsg":fields.one2many("gbsoft.weixin.htmlmsg","menu","HtmlMsg"),
        "groups":fields.char("Groups",size=100),
        "seq":fields.integer("Seq"),
    }
    _order = "seq asc"

class gbsoft_htmlmsg(osv.osv):
    _name = "gbsoft.weixin.htmlmsg"
    _columns={
        "menu":fields.many2one("gbsoft.weixin.usermenu2","Menu"),
        "title":fields.char("Title"),
        "description":fields.char("Description"),
        "picurl":fields.char("PicUrl"),
        "url":fields.char("Url"),
        "seq":fields.integer("Seq"),
    }
    _order = "menu,seq asc"
#AppID(应用ID)wx4c30a421cfb8be51
#AppSecret(应用密钥)d33521e37f782bfcda0373faf0ae2ba8 隐藏 重置