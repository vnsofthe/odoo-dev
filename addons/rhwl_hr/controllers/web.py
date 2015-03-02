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

    def dateTimeTZ(self,dateStr,delta):
        if not isinstance(dateStr,(str,)):return dateStr
        return (datetime.datetime.strptime(dateStr,"%Y-%m-%d %H:%M:%S") + datetime.timedelta(hours=delta)).strftime("%Y-%m-%d %H:%M:%S")

    @http.route('/web/api/hr_holidays_status/', type='http', auth="none")
    def get_holidays_status(self,**kw):
        res = wb.WebClient().check_userinfo(kw)
        uid = res.get('userid',False)
        registry = RegistryManager.get(request.session.db)
        data=[]
        with registry.cursor() as cr:
            try:
                u = registry.get('hr.holidays.status')
                ids = u.search(cr,SUPERUSER_ID,[])
                cont=self.CONTEXT
                if uid:
                    cont['employee_id']=uid
                data = u.name_get(cr,SUPERUSER_ID,ids,context=cont)
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
                        df = self.dateTimeTZ(res['params']['date_from']+':00',-8)
                        dt = self.dateTimeTZ(res['params']['date_to']+':00',-8)
                        number_of_days_temp = hr_holidays.onchange_date_to(cr, uid, 0, dt, df).get('value').get('number_of_days_temp')
                        id = hr_holidays.create(cr,SUPERUSER_ID,{"name":res['params']['note'],'employee_id':emp_id,
                                                            'holiday_status_id':res['params']['sel_type'],
                                                            'date_from':df,
                                                            'date_to':dt,
                                                            'number_of_days_temp':number_of_days_temp},context=self.CONTEXT)
                        cr.commit()
                        template = registry.get('ir.model.data').get_object(cr, uid, 'rhwl_hr', 'holidays_approve_email')
                        registry.get('email.template').send_mail(cr, uid, template.id, id, force_send=True, raise_exception=True, context=self.CONTEXT)
                except openerp.exceptions.ValidationError,ex:
                    cr.rollback()
                    res['statu']=500
                    res['errtext']=ex[1].split(':')[-1]
                except Exception,ex:
                    cr.rollback()
                    res['statu']=500
                    res['errtext']=ex

        response = request.make_response(json.dumps(res,ensure_ascii=False), [('Content-Type', 'application/json')])
        return response.make_conditional(request.httprequest)

    @http.route('/web/api/hr_holidays/list/', type='http', auth="none")
    def list_holidays(self,**kw):
        res = wb.WebClient().check_userinfo(kw)
        registry = RegistryManager.get(request.session.db)
        if res['statu']==200:
            uid = res['userid']
            res['data']=[]
            with registry.cursor() as cr:
                try:
                    hr_holidays = registry.get("hr.holidays")
                    emp_obj = registry.get("hr.employee")
                    emp_id = emp_obj.search(cr,SUPERUSER_ID,[('user_id','=',uid)])
                    if not emp_id:
                        res['statu']=500
                        res['errtext']=u"当前用户没有关联员工信息。"
                    else:
                        ids = hr_holidays.search(cr,uid,[('employee_id','in',emp_id),('type','=', 'remove')],order="id desc")
                        sel_state = hr_holidays.get_select_state(cr,uid,self.CONTEXT)
                        for i in hr_holidays.browse(cr,uid,ids,context=self.CONTEXT):
                            df = self.dateTimeTZ(i.date_from,8)
                            dt = self.dateTimeTZ(i.date_to,8)
                            res['data'].append((i.id,df,dt,i.holiday_status_id.name,i.name,sel_state.get(i.state)))
                except:
                    res['statu']=500
        response = request.make_response(json.dumps(res,ensure_ascii=False), [('Content-Type', 'application/json')])
        return response.make_conditional(request.httprequest)

    @http.route("/web/api/holidays/approve/",type='http',auth="none")
    def approve_holidays(self,**kw):
        res = wb.WebClient().check_userinfo(kw)
        registry = RegistryManager.get(request.session.db)
        if res['statu']==200:
            uid = res['userid']
            res['data']=[]
            with registry.cursor() as cr:
                try:
                    hr_holidays = registry.get("hr.holidays")
                    emp_obj = registry.get("hr.employee")
                    emp_id = emp_obj.search(cr,SUPERUSER_ID,[('user_id','=',uid)])
                    if not emp_id:
                        res['statu']=500
                        res['errtext']=u"当前用户没有关联员工信息。"
                    else:
                        ids = hr_holidays.search(cr,uid,['|','&',('employee_id.department_id.manager_id.id','in',emp_id),('employee_id.parent_id','=',False),'&',('employee_id.parent_id.id','in',emp_id),('employee_id.parent_id','!=',False),('type','=', 'remove')],order="id desc")
                        sel_state = hr_holidays.get_select_state(cr,uid,self.CONTEXT)
                        for i in hr_holidays.browse(cr,uid,ids,context=self.CONTEXT):
                            df = self.dateTimeTZ(i.date_from,8)
                            dt = self.dateTimeTZ(i.date_to,8)
                            res['data'].append((i.id,df,dt,i.holiday_status_id.name,i.name,sel_state.get(i.state),i.state,i.employee_id.name))
                except Exception,e:
                    res['statu']=500
                    res['errtext']=e.message
        response = request.make_response(json.dumps(res,ensure_ascii=False), [('Content-Type', 'application/json')])
        return response.make_conditional(request.httprequest)

    @http.route("/web/api/holidays/approve/<id>/<state>/",type='http',auth='none')
    def approve_holidays_submit(self,id,state,**kw):
        res = wb.WebClient().check_userinfo(kw)
        registry = RegistryManager.get(request.session.db)
        if res['statu']==200:
            uid = res['userid']
            res['data']=[]
            with registry.cursor() as cr:
                try:
                    hr_holidays = registry.get("hr.holidays")
                    if state=="success":
                        hr_holidays.signal_workflow(cr,uid,[int(id),],'validate')
                    elif state=="danger":
                        hr_holidays.signal_workflow(cr,uid,[int(id),], 'refuse')

                except Exception,e:
                    res['statu']=500
                    res['errtext']=e.message
        response = request.make_response(json.dumps(res,ensure_ascii=False), [('Content-Type', 'application/json')])
        return response.make_conditional(request.httprequest)