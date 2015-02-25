# -*- coding: utf-8 -*-

from openerp import http
from openerp.http import request
from openerp.addons.base.res.res_users import res_users
import json,simplejson
import openerp.tools.config as config
import openerp
from openerp import SUPERUSER_ID
from openerp.modules.registry import RegistryManager
import openerp.addons.web.controllers.main as db
import datetime
import logging
from openerp.tools.translate import _
from lxml import etree
import openerp.addons.rhwl.controllers.web as wb

_logger = logging.getLogger(__name__)
class WebClient(http.Controller):
    CONTEXT={'lang': "zh_CN",'tz': "Asia/Shanghai"}

    @http.route('/web/api/hr_holidays_status/', type='http', auth="none")
    def get_holidays_status(self,**kw):
        request.session.db = wb.WebClient().get_dbname()
        registry = RegistryManager.get(request.session.db)
        data=[]
        with registry.cursor() as cr:
            try:
                u = registry.get('hr.holidays.status')
                ids = u.search(cr,SUPERUSER_ID,[])
                for d in u.browse(cr,SUPERUSER_ID,ids,context=self.CONTEXT):
                    data.append((d.id,d.name))
                cr.commit()
            except:
                return "Get Holidays Status Error "

        #request.session.authenticate(request.session.db,"admin","123")
        #data = request.session.model("res.partner").get_hospital()
        response = request.make_response(json.dumps(data,ensure_ascii=False), [('Content-Type', 'application/json')])
        return response.make_conditional(request.httprequest)

    @http.route('/web/api/hr_holidays/', type='http', auth="none")
    def post_holidays(self,**kw):
        res = wb.WebClient().check_userinfo(kw)
        registry = RegistryManager.get(request.session.db)
        if res['statu']==200:
            uid = res['userid']
            with registry.cursor() as cr:
                try:
                    hr_holidays = registry.get("hr.holidays")
                    emp_obj = registry.get("hr.employee")
                    emp_id = emp_obj.search(cr,SUPERUSER_ID,[('user_id','=',uid)])
                    if not emp_id:
                        res['statu']=500
                        res['errtext']=u"当前用户没有关联员工信息。"
                    else:
                        if isinstance(emp_id,(list,tuple)):
                            emp_id = emp_id[0]
                        df = datetime.datetime.strptime(res['params']['date_from'],"%Y-%m-%d %H:%M") - datetime.timedelta(hours=8)
                        dt = datetime.datetime.strptime(res['params']['date_to'],"%Y-%m-%d %H:%M") - datetime.timedelta(hours=8)
                        number_of_days_temp = hr_holidays.onchange_date_to(cr, uid, 0, dt.strftime("%Y-%m-%d %H:%M:%S"), df.strftime("%Y-%m-%d %H:%M:%S")).get('value').get('number_of_days_temp')
                        id = hr_holidays.create(cr,SUPERUSER_ID,{"name":res['params']['note'],'employee_id':emp_id,
                                                            'holiday_status_id':res['params']['sel_type'],
                                                            'date_from':df,
                                                            'date_to':dt,
                                                            'number_of_days_temp':number_of_days_temp},context=self.CONTEXT)
                        cr.commit()
                        template = self.pool.get('ir.model.data').get_object(cr, uid, 'rhwl_hr', 'holidays_approve_email')
                        self.pool.get('email.template').send_mail(cr, uid, template.id, id, force_send=True, raise_exception=True, context=self.CONTEXT)
                except Exception,ex:
                    cr.rollback()
                    res['statu']=500

                    if isinstance(ex,(list,tuple)):
                        res['errtext']=ex[1].split(':')[-1]
                    else:
                        res['errtext']=ex
        response = request.make_response(json.dumps(res,ensure_ascii=False), [('Content-Type', 'application/json')])
        return response.make_conditional(request.httprequest)