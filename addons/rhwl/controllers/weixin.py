# -*- coding: utf-8 -*-

from openerp import http
import hashlib
from lxml import etree
from openerp.http import request
from openerp.modules.registry import RegistryManager
from openerp import SUPERUSER_ID
import time
import random
import datetime
from .. import rhwl_sms,rhwl_sale
import logging
_logger = logging.getLogger(__name__)

class weixin(http.Controller):
    CONTEXT={'lang': "zh_CN",'tz': "Asia/Shanghai"}

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
                id = user.search(cr,SUPERUSER_ID,[('openid','=',fromUser)],context=self.CONTEXT)
                if id:
                    user.write(cr,SUPERUSER_ID,id,{"active":True},context=self.CONTEXT)
                else:
                    user.create(cr,SUPERUSER_ID,{'openid':fromUser,'active':True,'state':'draft'},context=self.CONTEXT)
                cr.commit()
            return self.replyWeiXin(fromUser,toUser,u"欢迎关注【人和未来生物科技(长沙)有限公司】，您可以通过输入送检编号查询检测进度和结果。\n祝您生活愉快!")
        else:
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
                    if obj.yftelno:
                        rhwl_sms.send_sms(obj.yftelno,u"您查询样品检测结果的验证码为%s，请在五分钟内输入，如果不是您本人操作，请不用处理。" %(rand,))
                        return self.replyWeiXin(fromUser,toUser,u"验证码已经发送至检测知情同意书上登记的电话"+obj.yftelno[:3]+u"****"+obj.yftelno[-4:]+u"，请收到验证码后在五分钟内输入。")
                    else:
                        return self.replyWeiXin(fromUser,toUser,u"您查询的样品编码在检测知情同意书上没有登记电话，不能发送验证码，请与送检医院查询结果。")
                else:
                    return self.replyWeiXin(fromUser,toUser,u"您所查询的样品编码不存在，请重新输入，输入时注意区分大小写字母，并去掉多余的空格!")
            cr.commit()

    def replyWeiXin(self,toUser,fromUser,text):
        """微信号统一回复方法"""
        temp = "<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[%s]]></Content></xml>"
        return temp % (toUser,fromUser,time.time().__trunc__().__str__(),text)

    @http.route("/web/weixin/",type="http",auth="none")
    def rhwl_weixin(self,**kw):
        if kw.get('signature') and kw.get('timestamp') and kw.get('nonce'):#微信官网是否有转入验证信息
            if self.checkSignature(kw.get('signature'),kw.get('timestamp'),kw.get('nonce')):
                if kw.get('echostr'):#验证通过则返回传入的echostr
                    return kw.get('echostr')
            else:
                return 'Signature Error.'

        return self.msgProcess(request.httprequest.data)