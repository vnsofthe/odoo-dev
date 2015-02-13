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
_logger = logging.getLogger(__name__)

class weixin(http.Controller):
    CONTEXT={'lang': "zh_CN",'tz': "Asia/Shanghai"}
    HOSTNAME="http://www.vnsoft.cn"

    def checkSignature(self,signature,timestamp,nonce):
        """检查是否微信官方通信请求。"""
        token = 'vnsoft'
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
                user = registry.get('rhwl.weixin')
                id = user.search(cr,SUPERUSER_ID,[('openid','=',fromUser),('active','=',False)],context=self.CONTEXT)
                if id:
                    user.write(cr,SUPERUSER_ID,id,{"active":True},context=self.CONTEXT)
                else:
                    user.create(cr,SUPERUSER_ID,{'openid':fromUser,'active':True,'state':'draft'},context=self.CONTEXT)
                cr.commit()
            return self.replyWeiXin(fromUser,toUser,u"欢迎关注【人和未来生物科技(北京)有限公司】，您可以通过输入送检编号查询检测进度和结果。\n祝您生活愉快!")
        elif Event=="CLICK":
            key = xmlstr.find("EventKey").text
            if key=="ONLINE_QUERY":
                return self.replyWeiXin(fromUser,toUser,u"请您输入送检编号！")
            else:
                articles=self._get_htmlmsg(key)
                if articles[0]:
                    if not self._get_userid(fromUser):
                        articles={
                            "Title":"内部ERP帐号绑定",
                            "Description":"您查阅的功能需要授权，请先进行内部ERP帐号绑定",
                            "PicUrl":"/rhwl_weixin/static/img/logo.png",
                            "Url":"/rhwl_weixin/static/weixinbind.html"
                            }
                        return self.send_photo_text(fromUser,toUser,[articles,])
                if articles[1]:
                    return self.send_photo_text(fromUser,toUser,articles[1])
                else:
                    return self.replyWeiXin(fromUser,toUser,u"此功能在开发中，敬请稍候！")
        elif Event=="unsubscribe":
             registry = RegistryManager.get(request.session.db)
             with registry.cursor() as cr:
                user = registry.get('rhwl.weixin')
                id = user.search(cr,SUPERUSER_ID,[('openid','=',fromUser)],context=self.CONTEXT)
                if id:
                   user.write(cr,SUPERUSER_ID,id,{"active":False},context=self.CONTEXT)
                cr.commit()
             return self.replyWeiXin(fromUser,toUser,u"祝您生活愉快!")

    def textProcess(self,xmlstr):
        msgType=xmlstr.find("MsgType").text
        fromUser=xmlstr.find("FromUserName").text
        toUser=xmlstr.find("ToUserName").text
        content=xmlstr.find("Content").text#获得用户所输入的内容

        registry = RegistryManager.get(request.session.db)
        sample = registry.get("sale.sampleone")
        user = registry.get('rhwl.weixin')
        if content=="openid":
            return self.replyWeiXin(fromUser,toUser,fromUser)
        if content.isalnum() and len(content)==6:
            with registry.cursor() as cr:
                id = user.search(cr,SUPERUSER_ID,[("active",'=',True),("state","=","process"),("checkNum","=",content)])
                if not id:
                    return self.replyWeiXin(fromUser,toUser,u"请先输入样品编码。")
                else:
                    obj = user.browse(cr,SUPERUSER_ID,id)
                    mindate = datetime.datetime.utcnow() - datetime.timedelta(minutes =5)
                    if obj.checkDateTime < mindate.strftime("%Y-%m-%d %H:%M:%S"):
                        return self.replyWeiXin(fromUser,toUser,u"验证码已过期，请重新输入样品编码查询。")
                    else:
                        id = sample.search(cr,SUPERUSER_ID,[("name","=",obj.sampleno)])
                        sample_obj = sample.browse(cr,SUPERUSER_ID,id)
                        user.write(cr,SUPERUSER_ID,obj.id,{"state":"pass"})
                        cr.commit()
                        return self.replyWeiXin(fromUser,toUser,u"您的样品编码"+obj.sampleno+u"检查结果为【"+rhwl_sale.rhwl_sale_state_select.get(sample_obj.check_state)+u"】,详细的检测报告请与检测医院索取。" )
        else:
            with registry.cursor() as cr:
                id = sample.search(cr,SUPERUSER_ID,[('name','=',content)])
                if id:
                    openid = user.search(cr,SUPERUSER_ID,[('openid','=',fromUser)])
                    obj = sample.browse(cr,SUPERUSER_ID,id)
                    rand = random.randint(111111,999999)
                    checkDateTime = datetime.datetime.utcnow()
                    user.write(cr,SUPERUSER_ID,openid,{"telno":obj.yftelno,"state":"process","checkNum":rand,"checkDateTime":checkDateTime,"sampleno":content})
                    cr.commit()
                    if obj.yftelno:
                        rhwl_sms.send_sms(obj.yftelno,u"您查询样品检测结果的验证码为%s，请在五分钟内输入，如果不是您本人操作，请不用处理。" %(rand,))
                        return self.replyWeiXin(fromUser,toUser,u"验证码已经发送至检测知情同意书上登记的电话"+obj.yftelno[:3]+u"****"+obj.yftelno[-4:]+u"，请收到验证码后在五分钟内输入。")
                    else:
                        return self.replyWeiXin(fromUser,toUser,u"您查询的样品编码在检测知情同意书上没有登记电话，不能发送验证码，请与送检医院查询结果。")
                else:
                    return self.replyWeiXin(fromUser,toUser,u"您所查询的样品编码不存在，请重新输入，输入时注意区分大小写字母，并去掉多余的空格!")
            cr.commit()

    def send_photo_text(self,toUser,fromUser,articles):
        #发送图文消息
        articlesxml=""
        for i in articles:
            itemxml=""
            for k,v in i.items():
                if k=="Url" or k=="PicUrl":
                    if not v.startswith("http"): v = self.HOSTNAME+v
                    if k=='Url':v = v+"?openid="+toUser

                itemxml +="<%s><![CDATA[%s]]></%s>" %(k,v,k)
            itemxml="<item>%s</item>" % (itemxml,)
            articlesxml += itemxml

        temp = "<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[news]]></MsgType><ArticleCount>%s</ArticleCount><Articles>%s</Articles></xml> "
        return temp % (toUser,fromUser,time.time().__trunc__().__str__(),str(articles.__len__()),articlesxml)

    def replyWeiXin(self,toUser,fromUser,text):
        """微信号统一回复方法"""
        temp = "<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[%s]]></Content></xml>"
        return temp % (toUser,fromUser,time.time().__trunc__().__str__(),text)

    def _get_userid(self,openid):
        registry = RegistryManager.get(request.session.db)
        weixin = registry.get("rhwl.weixin")

        with registry.cursor() as cr:
            id = weixin.search(cr,SUPERUSER_ID,[('openid','=',openid)],context=self.CONTEXT)
            if id:
                obj= weixin.browse(cr,SUPERUSER_ID,id,context=self.CONTEXT)
                return obj.user_id.id
        return None

    def _get_htmlmsg(self,key):
        registry = RegistryManager.get(request.session.db)
        msg = registry.get("rhwl.weixin.usermenu2")
        with registry.cursor() as cr:
            id = msg.search(cr,SUPERUSER_ID,[("key","=",key)])
            if not id:
                return (False,None)
            obj = msg.browse(cr,SUPERUSER_ID,id)
            if not obj.htmlmsg:
                return (obj.need_user,None)
            articles=[]
            for j in obj.htmlmsg:
                if j.url:
                    articles.append({
                        "Title":j.title.encode("utf-8"),
                        "Description":j.description.encode("utf-8"),
                        "PicUrl":j.picurl.encode("utf-8"),
                        "Url":j.url and j.url.encode("utf-8") or ""
                    })
                else:
                    articles.append({
                        "Title":j.title.encode("utf-8"),
                        "Description":j.description.encode("utf-8"),
                        "PicUrl":j.picurl.encode("utf-8"),
                    })
            return (obj.need_user,articles)

    @http.route("/web/weixin/",type="http",auth="none")
    def rhwl_weixin(self,**kw):
        if kw.get('signature') and kw.get('timestamp') and kw.get('nonce'):#微信官网是否有转入验证信息
            if self.checkSignature(kw.get('signature'),kw.get('timestamp'),kw.get('nonce')):
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
                id=obj.search(cr,SUPERUSER_ID,[("openid","=",para.get("openid"))])
                obj.write(cr,SUPERUSER_ID,id,{"user_id":para.get("uid")})
                cr.commit()
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

        s='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        noncestr=''.join([s[random.randrange(0,s.__len__()-1)] for i in range(1,21)])
        timestamp=time.time().__trunc__().__str__()

        registry = RegistryManager.get(request.session.db)
        with registry.cursor() as cr:
            b = registry.get('rhwl.weixin.base')
            ids =b.search(cr,SUPERUSER_ID,[],limit=1)
            appid = b.browse(cr,SUPERUSER_ID,ids).appid
            jsapi_ticket= b._get_ticket(cr,SUPERUSER_ID,self.CONTEXT)
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