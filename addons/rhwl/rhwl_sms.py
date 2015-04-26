#codeing=utf-8
import requests
from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp import tools, api
import datetime

class rhwl_company(osv.osv):
    _inherit="res.company"

    """000/Send:1/Consumption:.1/Tmoney:.4/sid:1121102038224252"""
    def send_sms(self,cr,uid,tel,text):
        arg={
            "id":"",
            "pwd":"",
            "to":"",
            "content":'',
            "time":None
        }
        config_obj = self.pool.get('ir.config_parameter')
        #s=requests.post('http://service.winic.org/sys_port/gateway/?id=vnsoft&pwd=10261121sms&to=18657130579&content=%s&time='
        arg['to']=tel
        arg['content']=text.encode('gb2312')
        arg['id']=config_obj.get_param(cr, uid, 'rhwl.sms.login', default='').encode('utf-8')
        arg['pwd']=config_obj.get_param(cr, uid, 'rhwl.sms.passwd', default='').encode('utf-8')
        s=requests.post("http://service.winic.org/sys_port/gateway/",params=arg)
        ref = s.content
        s.close()
        return ref

