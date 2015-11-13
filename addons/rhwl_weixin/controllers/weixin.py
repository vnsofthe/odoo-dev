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
from .. import WXBizMsgCrypt
from urllib import unquote
import logging
import re
_logger = logging.getLogger(__name__)

class weixin(http.Controller):
    CONTEXT={'lang': "zh_CN",'tz': "Asia/Shanghai"}
    HOSTNAME="http://erp.genetalks.com"

    def xml2dict(self,xml):
        data = dict([(x.tag,x.text) for x in xml.getchildren()])
        return data

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

    def msgProcess(self,msgdata,encrypt=False,kw=None):
        """处理消息接口内容"""
        #获取官方POST过来的数据

        if msgdata:
            try:
                xml = etree.fromstring(msgdata)#进行XML解析
                msgType=xml.find("MsgType").text
                #根据消息类型调用不同的方法处理
                _logger.debug("msg type is:"+msgType)
                if msgType=='event':
                    return self.eventProcess(xml,encrypt,kw)
                elif msgType=='text':
                    _logger.debug("call textProcess")
                    return self.textProcess(xml,encrypt,kw)
            except:
                return msgdata
        return 'Not Data Found'

    def eventProcess(self,xmlstr,encrypt=False,kw=None):
        xml_data = self.xml2dict(xmlstr)
        msgType=xml_data.get("MsgType")
        fromUser=xml_data.get("FromUserName")
        toUser=xml_data.get("ToUserName")
        Event=xml_data.get("Event")#获得用户所输入的内容
        AgentID=xml_data.get("AgentID",None)

        if Event=='subscribe':#关注
            registry = RegistryManager.get(request.session.db)
            with registry.cursor() as cr:
                orig = registry.get("rhwl.weixin.base")
                welcome = orig.action_subscribe(cr,toUser,fromUser,AgentID)
                return self.replyWeiXin(fromUser,toUser,welcome,encrypt,AgentID,kw)
            #return self.replyWeiXin(fromUser,toUser,u"欢迎关注【人和未来生物科技(北京)有限公司】，您可以通过输入送检编号查询检测进度和结果。\n祝您生活愉快!")
        elif Event=="CLICK" or Event=="click":
            key = xml_data.get("EventKey")
            registry = RegistryManager.get(request.session.db)
            with registry.cursor() as cr:
                orig = registry.get("rhwl.weixin.base")
                res=orig.action_event_clicked(cr,key,toUser,fromUser,AgentID)

                if isinstance(res,(list,tuple)):
                    return self.send_photo_text(fromUser,toUser,res[0],res[1],encrypt,AgentID,kw)
                else:
                    return self.replyWeiXin(fromUser,toUser,res,encrypt,AgentID,kw)
        elif Event=="unsubscribe":
             registry = RegistryManager.get(request.session.db)
             with registry.cursor() as cr:
                orig = registry.get("rhwl.weixin.base")
                orig.action_unsubscribe(cr,toUser,fromUser,AgentID)
             return self.replyWeiXin(fromUser,toUser,u"祝您生活愉快!",encrypt,AgentID,kw)
        else:
            return ""

    def textProcess(self,xmlstr,encrypt=False,kw=None):

        msgType=xmlstr.find("MsgType").text
        fromUser=xmlstr.find("FromUserName").text
        toUser=xmlstr.find("ToUserName").text
        content=xmlstr.find("Content").text #获得用户所输入的内容
        AgentID_el = [x for x in xmlstr.getchildren() if x.tag=="AgentID"]
        if AgentID_el:
            AgentID = AgentID_el[0].text
        else:
            AgentID=None

        registry = RegistryManager.get(request.session.db)

        if content=="openid":
            return self.replyWeiXin(fromUser,toUser,fromUser,encrypt,AgentID,kw)
        with registry.cursor() as cr:
            orig = registry.get("rhwl.weixin.base")
            res = orig.action_text_input(cr,content,toUser,fromUser)
            return self.replyWeiXin(fromUser,toUser,res,encrypt,AgentID,kw)


    def send_photo_text(self,toUser,fromUser,code,articles,encrypt=None,AgentID=None,kw=None):
        #发送图文消息
        registry = RegistryManager.get(request.session.db)
        with registry.cursor() as cr:
            orig = registry.get("rhwl.weixin")
            ids = orig.search(cr,SUPERUSER_ID,[("openid","=",toUser),("base_id.code","=",code)])
            if ids:
                user_obj = orig.browse(cr,SUPERUSER_ID,ids[0]).rhwlid
                user_obj = user_obj.encode("utf-8")
            else:
                user_obj=toUser
        articlesxml=""
        for i in articles:
            itemxml=""

            for k,v in i.items():

                if k=="Url" or k=="PicUrl":
                    if not v.startswith("http"): v = self.HOSTNAME+v
                    if k=='Url':
                        if v.count('?')>0:
                            v = v+"&code="+code+"&openid="+user_obj
                        else:
                            v = v+"?code="+code+"&openid="+user_obj

                itemxml +="<%s><![CDATA[%s]]></%s>" %(k,v,k)
            itemxml="<item>%s</item>" % (itemxml,)
            articlesxml += itemxml

        temp = "<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[news]]></MsgType><ArticleCount>%s</ArticleCount><Articles>%s</Articles></xml> "
        temp =  temp % (toUser,fromUser,time.time().__trunc__().__str__(),str(articles.__len__()),articlesxml)
        if encrypt:
            sVerifyTimeStamp=kw.get('timestamp')
            sVerifyNonce=kw.get('nonce')
            sToken = kw.get('t')
            sEncodingAESKey = "KWkAnyk5COAu3tiLlSvWCwHp8pHj7wGwjYvuNxLdyCR"
            sCorpID = "wx77bc43a51cdb049b"
            wxcpt=WXBizMsgCrypt.WXBizMsgCrypt(sToken,sEncodingAESKey,sCorpID)
            ret,sEncryptMsg=wxcpt.EncryptMsg(temp, sVerifyNonce, sVerifyTimeStamp)
            _logger.debug((ret,sEncryptMsg))
            if( ret!=0 ):
               return "ERR: EncryptMsg ret: " + ret
            return sEncryptMsg
        else:
            return temp

    def replyWeiXin(self,toUser,fromUser,text,encrypt=False,AgentID=None,kw=None):
        """微信号统一回复方法"""
        _logger.error((toUser,fromUser,text,encrypt,AgentID,kw))
        if AgentID:
            temp = "<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[%s]]></Content><AgentID>"+AgentID+"</AgentID></xml>"
            temp = temp % (toUser,fromUser,time.time().__trunc__().__str__(),text.encode("utf-8"))
            sVerifyTimeStamp=kw.get('timestamp')
            sVerifyNonce=kw.get('nonce')
            sToken = kw.get('t')
            sEncodingAESKey = "KWkAnyk5COAu3tiLlSvWCwHp8pHj7wGwjYvuNxLdyCR"
            sCorpID = "wx77bc43a51cdb049b"
            wxcpt=WXBizMsgCrypt.WXBizMsgCrypt(sToken,sEncodingAESKey,sCorpID)
            ret,sEncryptMsg=wxcpt.EncryptMsg(temp, sVerifyNonce, sVerifyTimeStamp)
            _logger.error((ret,sEncryptMsg))
            if( ret!=0 ):
               return "ERR: EncryptMsg ret: " + ret
            return sEncryptMsg
        else:
            temp = "<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[%s]]></Content></xml>"
            return temp % (toUser,fromUser,time.time().__trunc__().__str__(),text)

    def customer_service(self,toUser,fromUser,encrypt=False):
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
        elif kw.get('msg_signature') and kw.get('timestamp') and kw.get('nonce'):
            #加密消息判断
            sToken = kw.get('t')
            sEncodingAESKey = "KWkAnyk5COAu3tiLlSvWCwHp8pHj7wGwjYvuNxLdyCR"
            sCorpID = "wx77bc43a51cdb049b"
            wxcpt=WXBizMsgCrypt.WXBizMsgCrypt(sToken,sEncodingAESKey,sCorpID)
            sVerifyMsgSig=kw.get('msg_signature')
            sVerifyTimeStamp=kw.get('timestamp')
            sVerifyNonce=kw.get('nonce')
            sVerifyEchoStr=kw.get('echostr')
            if sVerifyEchoStr:
                ret,sEchoStr=wxcpt.VerifyURL(sVerifyMsgSig, sVerifyTimeStamp,sVerifyNonce,unquote(sVerifyEchoStr))
                if(ret!=0):
                   return "ERR: VerifyURL ret: " + ret
                else:
                    return sEchoStr
            else:
               sReqData = request.httprequest.data
               ret,sMsg=wxcpt.DecryptMsg( sReqData, sVerifyMsgSig, sVerifyTimeStamp, sVerifyNonce)
               _logger.debug((ret,sMsg))
               if( ret!=0 ):
                  return "ERR: DecryptMsg ret: " + ret
               else:
                  return self.msgProcess(sMsg,True,kw)
        return self.msgProcess(request.httprequest.data,False,kw)

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
            appid = b.browse(cr,SUPERUSER_ID,ids).original_id
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