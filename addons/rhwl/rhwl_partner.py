# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp import tools, api
import datetime
import logging

class rhwl_stock_warehouse(osv.osv):
    _inherit = "stock.warehouse"

    def write(self, cr, uid, ids, vals, context=None):
        print vals
        return super(rhwl_stock_warehouse, self).write(cr, uid, ids, vals, context=context)

_logger = logging.getLogger(__name__)
class rhwl_partner(osv.osv):
    _name = "res.partner"
    _description = "Partner"
    _inherit = "res.partner"

    _columns = {
        "partner_unid": fields.char(u"编号", required=True),
        "dev_user_id": fields.many2one('res.users', string=u'开发人员'),
        "cust_level": fields.selection(
            [('AA', u'省级、地级市产前诊断中心；大型筛查机构(筛查量1万以上)'), ('AB', u'县级市产前诊断中心、一般筛查机构、分娩5000以上的医院、有能力的三甲医院'),
             ('BC', u'年分娩量1500-3000的医院'), ('CC', u'年分娩量1500以下的医院'),('PROXY0',u'区域总代理商')], u'客户级别'),
        "hospital_level": fields.selection(
            [(u'三甲', u'三甲'), (u'三级', u'三级'), (u'二甲', u'二甲'), (u'二乙', u'二乙'), (u'一级', u'一级'), (u'卫生服务中心', u'卫生服务中主')],
            u'医院等级'),
        "cust_type": fields.selection([(u'私立', u'私立'), (u'公立', u'公立')], u'客户性质'),
        "zydb": fields.many2one('res.users', string=u'驻院代表'),
        "amt": fields.float(u'无创收费金额', required=True, digits_compute=dp.get_precision('Product Price')),
        "sfdw": fields.many2one('res.partner', string=u'收费单位', domain=[('is_company', '=', True)]),
        "sncjrs": fields.integer(u'上年产检人数'),
        "njfml":fields.integer(u'年均分娩人数'),
        "njtsrs":fields.integer(u'年均唐筛人数'),
        "snwcrs": fields.integer(u'上年无创人数'),
        "jnmbrs": fields.integer(u'今年目标人数'),
        "jnsjrs": fields.integer(u'今年实际人数', readonly=True),
        "nextmonth":fields.integer(u"下月目标人数"),
        "qyks": fields.selection([(u'产科', u'产科'), (u'妇产科', u'妇产科'), (u'遗传科', u'遗传科')], u"签约科室"),
        "jzds": fields.selection([(u'人和', u'人和'), (u'华大', u'华大'), (u'贝瑞', u'贝瑞'), (u'凡迪', u'凡迪'), ('0', u'其它')],
                                 u"客户占有"),
        "jzdsother": fields.char(size=20),
        "mbjysj": fields.date(u'无创目标进院时间'),
        "sjjysj": fields.date(u'无创实际进院时间'),
        "eduction": fields.selection([(u'博士', u'博士'), (u'硕士', u'硕士'), (u'本科', u'本科'), (u'专科', u'专科'), (u'中专', u'中专'), ],
                                     string=u'学历'),
        "yjfx": fields.char(u"研究方向", size=100),
        "cprz": fields.selection([("1", u"初识"), ("2", u"认可"), ("3", u"推荐")], string=u"产品认知"),
        "hospital_price": fields.float(u"无创临床收费", digits_compute=dp.get_precision('Product Price')),
        "city_id": fields.many2one("res.country.state.city", string=u"城市",domain="[('state_id','=',state_id]"),
        "area_id": fields.many2one("res.country.state.city.area",string=u"区/县", domain="[('city_id','=',city_id)]"),
        'function_sel': fields.selection(
            [(u"主任", u"主任"), (u"副主任", u"副主任"), (u"主治", u"主治"), (u'住院', u'住院'), (u'护士长', u'护士长'), (u'护士', u'护士'),
             (u'销售助理', u'销售助理'), (u'销售', u'销售')], u'职位'),
        "product_cost":fields.float(u'试管成本收费', required=True, digits_compute=dp.get_precision('Product Price')),
        "proxy_partner":fields.many2one("res.partner",u"上级代理",domain="[('is_company', '=', True),('customer','=',True)]"),
        "payment_kind":fields.selection([('hospital',u"医院代收"),('proxy',u'经销商代收'),('pos',u'POS机收费'),('cash',u'现金')],string=u"收费方式", required=True),
        "yg_amt":fields.float(u'易感收费金额', required=True, digits_compute=dp.get_precision('Product Price')),
        "ys_amt":fields.float(u'叶酸收费金额', required=True, digits_compute=dp.get_precision('Product Price')),
        "el_amt":fields.float(u'耳聋收费金额', required=True, digits_compute=dp.get_precision('Product Price')),
        "yg_mbjysj": fields.date(u'易感目标进院时间'),
        "ys_mbjysj": fields.date(u'叶酸目标进院时间'),
        "el_mbjysj": fields.date(u'耳聋目标进院时间'),
        "yg_sjjysj": fields.date(u'易感实际进院时间'),
        "ys_sjjysj": fields.date(u'叶酸实际进院时间'),
        "el_sjjysj": fields.date(u'耳聋实际进院时间'),
        "wc_contacts":fields.many2one("res.partner",string=u"医院联系人",domain="[('parent_id','=',id)]"),
        "wc_material":fields.many2one("res.partner",string=u"物料联系人",domain="[('parent_id','=',id)]"),
        "wc_report":fields.many2one("res.partner",string=u"报告联系人",domain="[('parent_id','=',id)]"),
        "yg_contacts":fields.many2one("res.partner",string=u"医院联系人",domain="[('parent_id','=',id)]"),
        "yg_material":fields.many2one("res.partner",string=u"物料联系人",domain="[('parent_id','=',id)]"),
        "yg_report":fields.many2one("res.partner",string=u"报告联系人",domain="[('parent_id','=',id)]"),
        "ys_contacts":fields.many2one("res.partner",string=u"医院联系人",domain="[('parent_id','=',id)]"),
        "ys_material":fields.many2one("res.partner",string=u"物料联系人",domain="[('parent_id','=',id)]"),
        "ys_report":fields.many2one("res.partner",string=u"报告联系人",domain="[('parent_id','=',id)]"),
        "el_contacts":fields.many2one("res.partner",string=u"医院联系人",domain="[('parent_id','=',id)]"),
        "el_material":fields.many2one("res.partner",string=u"物料联系人",domain="[('parent_id','=',id)]"),
        "el_report":fields.many2one("res.partner",string=u"报告联系人",domain="[('parent_id','=',id)]")
    }

    _defaults = {
        "date": fields.date.today,
        "amt": 0,
        "dev_user_id": lambda obj, cr, uid, context: uid,
        "user_id":lambda obj, cr, uid, context: uid,
        "payment_kind":lambda obj,cr,uid,context:"hospital",
        "product_cost":0,
        "yg_amt":0,
        "ys_amt":0,
        "el_amt":0
    }

    def init(self, cr):
        ids = self.search(cr,SUPERUSER_ID,[("is_company","=",True),("parent_id","!=",False)])
        self.write(cr,SUPERUSER_ID,ids,{"parent_id":False})
        ids = self.search(cr,SUPERUSER_ID,[("is_company","=",False),("parent_id","!=",False),("partner_unid","=",False)])
        for i in ids:
            self.write(cr,SUPERUSER_ID,i,{"partner_unid":str(i)})
        cr.execute("""update res_partner
                    set partner_unid = partner_unid||'_'||id
                    where partner_unid in (select partner_unid from res_partner group by partner_unid having count(*)>1)""")
        #cr.execute("ALTER TABLE res_partner DROP constraint res_partner_partner_unid_uniq")
        cr.commit()



    def onchange_city_id(self, cr, uid, ids, city, arg, newid, context=None):
        if not city:
            return {
                "value": {
                    "city": '',
                }
            }
        city_obj = self.pool.get("res.country.state.city").browse(cr, SUPERUSER_ID, city, context=context)
        state_code = city_obj.state_id.code
        city_code = city_obj.code
        if not state_code:state_code=""
        if not city_code:city_code=""
        if arg and not newid:
            cr.execute("select max(partner_unid) from res_partner where partner_unid like '%s'" % (
            state_code + city_code + '%',))
            for unid in cr.fetchall():
                max_id = unid[0]
            if max_id:
                max_id = max_id[:4] + str(int(max_id[4:]) + 1).zfill(4)
            else:
                max_id = state_code + city_code + '0001'

        res = {
            "value": {
                "city": city_obj.name,
                "area_id":False,
            }
        }
        if arg and not newid:
            res['value']['partner_unid'] = max_id
        return res

    @api.multi
    def onchange_state(self, state_id):
        val = super(rhwl_partner, self).onchange_state(state_id)
        if not val.has_key('value'):
            val['value'] = {}
        val['value']['city_id'] = False
        val['value']['city'] = ''
        return val

    def write(self, cr, uid, ids, vals, context=None):
        id = super(rhwl_partner,self).write(cr,uid,ids,vals,context=context)
        obj = self.browse(cr,uid,ids,context=context)
        company = None
        stock_warehouse = self.pool.get("stock.warehouse")
        for i in obj:
            if not company:
                company = self.pool.get("res.company").search(cr, uid, [("id", '=', i.company_id.id)], context=context)
            if company:
                partner = self.pool.get("res.company").browse(cr, uid, company, context=context)

                if i.customer and i.is_company and i.sjjysj:
                    stock_warehouse_id = stock_warehouse.search(cr,SUPERUSER_ID,[],order="id desc",limit=1)
                    stock_warehouse_obj = stock_warehouse.browse(cr,SUPERUSER_ID,stock_warehouse_id,context=context)
                    val = {
                        "name": i.name,
                        "code": str(stock_warehouse_obj.id+1),  # vals.get("partner_unid"),
                        "partner_id": i.id,
                        "company_id": i.company_id.id,
                        "buy_to_resupply": False,
                        "default_resupply_wh_id": 0,
                      }
                    default_id = stock_warehouse.search(cr, SUPERUSER_ID, [('partner_id', '=', partner.partner_id.id)],
                                                        context=context)
                    if not default_id:
                        raise osv.except_osv(_('Error'), u"没有找到归属当前公司的仓库。")
                    val["default_resupply_wh_id"] = default_id[0]
                    val["resupply_wh_ids"] = [[6, False, [default_id[0]]]]
                    wh = stock_warehouse.search(cr, SUPERUSER_ID,
                                                [('partner_id', '=', i.id)],
                                                context=context)
                    if not wh:
                        id_s = stock_warehouse.create(cr, SUPERUSER_ID, val, context=context)
        return id

    def create(self, cr, uid, vals, context=None):
        #_logger.error(vals)
        if not vals.get('partner_unid'):
            state_code=None
            city_code=None

            if (not (vals.get("state_id") and vals.get("city_id"))) or vals.get("parent_id"):
                parent = self.pool.get("res.partner").browse(cr,uid,vals.get("parent_id"),context=context)
                vals["state_id"] = parent.state_id.id
                vals["city_id"] =parent.city_id.id
            if vals.get("state_id"):
                state_code = self.pool.get("res.country.state").browse(cr,uid,vals.get("state_id")).code
            if vals.get("city_id"):
                city_code = self.pool.get("res.country.state.city").browse(cr,uid,vals.get("city_id")).code
            if state_code and city_code:
                cr.execute("select max(partner_unid) from res_partner where partner_unid like '%s'" % (
                state_code + city_code + '%',))
                for unid in cr.fetchall():
                    max_id = unid[0]
                if max_id:
                    max_id = max_id[:4] + str(int(max_id[4:]) + 1).zfill(4)
                else:
                    max_id = state_code + city_code + '0001'
                vals['partner_unid'] = max_id
        if (not (vals.get("customer") or vals.get("supplier"))) and (not vals.get("is_company")):
            if not vals.get('parent_id'):
               vals['parent_id'] = 1

        id = super(rhwl_partner, self).create(cr, uid, vals, context)
        partner = self.pool.get("res.company").search(cr, uid, [("id", '=', vals.get("company_id"))], context=context)
        if not partner:
            return id
        partner = self.pool.get("res.company").browse(cr, uid, partner, context=context)

        stock_warehouse = self.pool.get("stock.warehouse")
        if vals.get("customer") and vals.get("is_company") and vals.get("sjjysj"):
            stock_warehouse_id = stock_warehouse.search(cr,SUPERUSER_ID,[],order="id desc",limit=1)
            stock_warehouse_obj = stock_warehouse.browse(cr,SUPERUSER_ID,stock_warehouse_id,context=context)
            val = {
                "name": vals.get("name"),
                "code": str(stock_warehouse_obj.id+1),  # vals.get("partner_unid"),
                "partner_id": id,
                "company_id": vals.get("company_id"),
                "buy_to_resupply": False,
                "default_resupply_wh_id": 0,
              }


            default_id = stock_warehouse.search(cr, SUPERUSER_ID, [('partner_id', '=', partner.partner_id.id)],
                                                context=context)
            if not default_id:
                raise osv.except_osv(_('Error'), u"没有找到归属当前公司的仓库。")
            val["default_resupply_wh_id"] = default_id[0]
            val["resupply_wh_ids"] = [[6, False, [default_id[0]]]]
            wh = stock_warehouse.search(cr, SUPERUSER_ID,
                                        [('partner_id', '=', id)],
                                        context=context)
            if not wh:
                id_s = stock_warehouse.create(cr, SUPERUSER_ID, val, context=context)

        return id

    def get_hospital(self,cr,uid,context=None):
        ids = self.search(cr,uid,[('is_company','=',True),('customer','=',True)],context = context)
        obj = self.browse(cr,uid,ids,context=context)
        data = {}

        for i in obj:
            if i.state_id.name and i.city_id.name:
                cus = {"name":i.name,"accept":'Y'}
                if not data.has_key(i.state_id.name):
                    data[i.state_id.name]={}
                if not data[i.state_id.name].has_key(i.city_id.name):
                    data[i.state_id.name][i.city_id.name]=[]
                data[i.state_id.name][i.city_id.name].append(cus)

        return data

    def get_Contact_person(self,cr,uid,id,category_name=u"联络人",context=None):
        obj = self.browse(cr,uid,id,context=context)
        for i in obj.child_ids:
            for j in i.category_id:
                if j.name==category_name:
                    return i.id and i.id or None

        return None

    def get_Contact_person_user(self,cr,uid,id,category_name=u"联络人",context=None):
        p_id = self.get_Contact_person(cr,uid,id,category_name,context=context)
        if p_id:
            person = self.pool.get("res.users").search(cr,uid,[("partner_id.id","=",p_id)])
            if isinstance(person,(list,tuple)):
                person = person[0]
            return person
        return p_id

    def get_detail_address_dict(self,cr,uid,id,context=None):
        partner = self.browse(cr, uid, id, context=context)
        if partner.parent_id and partner.use_parent_address:
            res = {"state_id":partner.parent_id.state_id.id,
                   "city_id":partner.parent_id.city_id.id,
                   "area_id":partner.parent_id.area_id.id,
                   "street":partner.parent_id.street,
                   "street2":partner.parent_id.street2}
        else:
            res = {"state_id":partner.state_id.id,
                   "city_id":partner.city_id.id,
                   "area_id":partner.area_id.id,
                   "street":partner.street,
                   "street2":partner.street2}
        return res

    def get_detail_address(self,cr,uid,id,context=None):
        partner = self.browse(cr, uid, id, context=context)
        if partner.parent_id and partner.use_parent_address:
            res = [partner.parent_id.state_id.name, partner.parent_id.city_id.name,partner.parent_id.area_id.name,
                   partner.parent_id.street, partner.parent_id.street2]
        else:
            res = [partner.state_id.name, partner.city_id.name, partner.area_id.name,partner.street,
                   partner.street2]
        return ''.join([x for x in res if x])

class rhwl_country_state_city(osv.osv):
    _name = "res.country.state.city"

    _columns = {
        "state_id": fields.many2one("res.country.state", string="State"),
        "code": fields.char("Code", size=10),
        "name": fields.char("Name", size=20),
    }

class rhwl_country_state_city_area(osv.osv):
    _name = "res.country.state.city.area"

    _columns = {
        "city_id":fields.many2one("res.country.state.city",string="City"),
        "name": fields.char("Area",size=200)
    }

class rhwl_user(osv.osv):
    _inherit="res.users"
    _columns={
        'section_ids': fields.many2many('crm.case.section', 'sale_member_rel', 'member_id','section_id',  'Sale Teams'),
    }
    _defaults={
        "parent_id":1
    }