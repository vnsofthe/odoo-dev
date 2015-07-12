# -*- coding: utf-8 -*-

from openerp import http
import hashlib
from lxml import etree
from openerp.http import request
from openerp.modules.registry import RegistryManager
from openerp import SUPERUSER_ID
import time
import random
import datetime,json
from openerp.addons.rhwl import rhwl_sale,rhwl_sms



import logging
import re
_logger = logging.getLogger(__name__)

class weixin(http.Controller):
    CONTEXT={'lang': "zh_CN",'tz': "Asia/Shanghai"}
    HOSTNAME="http://erp.genetalks.com"

    def checkSignature(self,signature,timestamp,nonce,token):
        """检查是否微信官方通信请求。"""
        #token = 'vnsoft'
        #字典序排序
        list=[token,timestamp,nonce]
        list.sort()
        #sha1加密算法
        sha1=hashlib.sha1()
        map(sha1.update,list)
        hashcode=sha1.hexdigest()

        #如果是来自微信的请求，则回复True,否则为False
        return hashcode == signature

    def msgProcess(self,msgdata):
        """处理消息接口内容"""
        #获取官方POST过来的数据

        if msgdata:
            try:
                xml = etree.fromstring(msgdata)#进行XML解析
                msgType=xml.find("MsgType").text
                #根据消息类型调用不同的方法处理
                if msgType=='event':
                    return self.eventProcess(xml)
                elif msgType=='text':
                    return self.textProcess(xml)
            except:
                return msgdata
        return 'Not Data Found'

    def eventProcess(self,xmlstr):
        msgType=xmlstr.find("MsgType").text
        fromUser=xmlstr.find("FromUserName").text
        toUser=xmlstr.find("ToUserName").text
        Event=xmlstr.find("Event").text#获得用户所输入的内容
        if Event=='subscribe':#关注
            registry = RegistryManager.get(request.session.db)
            with registry.cursor() as cr:
                orig = registry.get("rhwl.weixin.base")
                welcome = orig.action_subscribe(cr,toUser,fromUser)
                return self.replyWeiXin(fromUser,toUser,welcome)
            #return self.replyWeiXin(fromUser,toUser,u"欢迎关注【人和未来生物科技(北京)有限公司】，您可以通过输入送检编号查询检测进度和结果。\n祝您生活愉快!")
        elif Event=="CLICK":
            key = xmlstr.find("EventKey").text
            registry = RegistryManager.get(request.session.db)
            with registry.cursor() as cr:
                orig = registry.get("rhwl.weixin.base")
                res=orig.action_event_clicked(cr,key,toUser,fromUser)
                _logger.debug(res)
                if isinstance(res,(list,tuple)):
                    return self.send_photo_text(fromUser,toUser,res[0],res[1])
                else:
                    return self.replyWeiXin(fromUser,toUser,res)
        elif Event=="unsubscribe":
             registry = RegistryManager.get(request.session.db)
             with registry.cursor() as cr:
                orig = registry.get("rhwl.weixin.base")
                orig.action_unsubscribe(cr,toUser,fromUser)
             return self.replyWeiXin(fromUser,toUser,u"祝您生活愉快!")
        else:
            return ""

    def textProcess(self,xmlstr):
        msgType=xmlstr.find("MsgType").text
        fromUser=xmlstr.find("FromUserName").text
        toUser=xmlstr.find("ToUserName").text
        content=xmlstr.find("Content").text#获得用户所输入的内容

        registry = RegistryManager.get(request.session.db)

        if content=="openid":
            return self.replyWeiXin(fromUser,toUser,fromUser)
        with registry.cursor() as cr:
            orig = registry.get("rhwl.weixin.base")
            res = orig.action_text_input(cr,content,toUser,fromUser)
            return self.replyWeiXin(fromUser,toUser,res)


    def send_photo_text(self,toUser,fromUser,code,articles):
        #发送图文消息
        articlesxml=""
        for i in articles:
            itemxml=""

            for k,v in i.items():

                if k=="Url" or k=="PicUrl":
                    if not v.startswith("http"): v = self.HOSTNAME+v
                    if k=='Url':
                        if v.count('?')>0:
                            v = v+"&code="+code+"&openid="+toUser
                        else:
                            v = v+"?code="+code+"&openid="+toUser

                itemxml +="<%s><![CDATA[%s]]></%s>" %(k,v,k)
            itemxml="<item>%s</item>" % (itemxml,)
            articlesxml += itemxml

        temp = "<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[news]]></MsgType><ArticleCount>%s</ArticleCount><Articles>%s</Articles></xml> "
        return temp % (toUser,fromUser,time.time().__trunc__().__str__(),str(articles.__len__()),articlesxml)

    def replyWeiXin(self,toUser,fromUser,text):
        """微信号统一回复方法"""
        temp = "<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[%s]]></Content></xml>"
        return temp % (toUser,fromUser,time.time().__trunc__().__str__(),text)

    def customer_service(self,toUser,fromUser):
        """微信号统一回复方法"""
        temp = "<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[transfer_customer_service]]></MsgType></xml>"
        return temp % (toUser,fromUser,time.time().__trunc__().__str__())





    @http.route("/web/weixin/",type="http",auth="none")
    def rhwl_weixin(self,**kw):
        if kw.get('signature') and kw.get('timestamp') and kw.get('nonce'):#微信官网是否有转入验证信息
            if self.checkSignature(kw.get('signature'),kw.get('timestamp'),kw.get('nonce'),kw.get('t')):
                if kw.get('echostr'):#验证通过则返回传入的echostr
                    return kw.get('echostr')
            else:
                return 'Signature Error.'

        return self.msgProcess(request.httprequest.data)

    @http.route("/web/weixin/bind/",type="http",auth="public")
    def rhwl_weixin_bind(self,**kw):
        para={}
        if request.httprequest.data:
            para = eval(request.httprequest.data)
        if kw:
            para.update(kw)
        if para.get("openid") and para.get("uid"):
            registry = RegistryManager.get(request.session.db)
            with registry.cursor() as cr:
                obj = registry.get("rhwl.weixin")
                obj.action_user_bind(cr,para.get("code"),para.get("openid"),para.get("uid"))
                response = request.make_response(json.dumps({"statu":200},ensure_ascii=False), [('Content-Type', 'application/json')])
        else:
            response = request.make_response(json.dumps({"statu":500},ensure_ascii=False), [('Content-Type', 'application/json')])
        return response.make_conditional(request.httprequest)

    @http.route("/web/weixin/jsapi/",type="http",auth="public")
    def rhwl_weixin_jsapi(self,**kw):
        para={}
        if request.httprequest.data:
            para = eval(request.httprequest.data)
        if kw:
            para.update(kw)
        url=para.get("url","").encode('utf-8')
        code=para.get("code","").encode('utf-8')
        s='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        noncestr=''.join([s[random.randrange(0,s.__len__()-1)] for i in range(1,21)])
        timestamp=time.time().__trunc__().__str__()

        registry = RegistryManager.get(request.session.db)
        with registry.cursor() as cr:
            b = registry.get('rhwl.weixin.base')
            ids =b.search(cr,SUPERUSER_ID,[("code","=",code)],limit=1)
            appid = b.browse(cr,SUPERUSER_ID,ids).appid
            jsapi_ticket= b._get_ticket(cr,SUPERUSER_ID,code,context=self.CONTEXT)
        str = "jsapi_ticket="+jsapi_ticket+"&noncestr="+noncestr+"&timestamp="+timestamp+"&url="+url
        sha = hashlib.sha1(str)
        s = sha.hexdigest()
        data={
            "noncestr":noncestr,
            "timestamp":timestamp,
            "signature":s,
            "appid":appid
        }
        response = request.make_response(json.dumps(data,ensure_ascii=False), [('Content-Type', 'application/json')])
        return response.make_conditional(request.httprequest)