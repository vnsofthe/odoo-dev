# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp import tools, api
import datetime


class rhwl_stock_warehouse(osv.osv):
    _inherit = "stock.warehouse"

    def write(self, cr, uid, ids, vals, context=None):
        print vals
        return super(rhwl_stock_warehouse, self).write(cr, uid, ids, vals, context=context)


class rhwl_partner(osv.osv):
    _name = "res.partner"
    _description = "Partner"
    _inherit = "res.partner"

    _columns = {
        "partner_unid": fields.char(u"编号", required=True),
        "dev_user_id": fields.many2one('res.users', string=u'开发人员'),
        "cust_level": fields.selection(
            [('AA', u'省级、地级市产前诊断中心；大型筛查机构(筛查量1万以上)'), ('AB', u'县级市产前诊断中心、一般筛查机构、分娩5000以上的医院、有能力的三甲医院'),
             ('BC', u'年分娩量1500-3000的医院'), ('CC', u'年分娩量1500以下的医院')], u'客户级别'),
        "hospital_level": fields.selection(
            [(u'三甲', u'三甲'), (u'三级', u'三级'), (u'二甲', u'二甲'), (u'二乙', u'二乙'), (u'一级', u'一级'), (u'卫生服务中心', u'卫生服务中主')],
            u'医院等级'),
        "cust_type": fields.selection([(u'私立', u'私立'), (u'公立', u'公立')], u'客户性质'),
        "zydb": fields.many2one('res.users', string=u'驻院代表'),
        "amt": fields.float(u'收费金额', required=True, digits_compute=dp.get_precision('Product Price')),
        "sfdw": fields.many2one('res.partner', string=u'收费单位', domain=[('is_company', '=', True)]),
        "sncjrs": fields.integer(u'上年产检人数'),
        "snwcrs": fields.integer(u'上年无创人数'),
        "jnmbrs": fields.integer(u'今年目标人数'),
        "jnsjrs": fields.integer(u'今年实际人数', readonly=True),
        "qyks": fields.selection([(u'产科', u'产科'), (u'妇产科', u'妇产科'), (u'遗传科', u'遗传科')], u"签约科室"),
        "jzds": fields.selection([(u'人和', u'人和'), (u'华大', u'华大'), (u'贝瑞', u'贝瑞'), (u'凡迪', u'凡迪'), ('0', u'其它')],
                                 u"客户占有"),
        "jzdsother": fields.char(size=20),
        "mbjysj": fields.date(u'目标进院时间'),
        "sjjysj": fields.date(u'实际进院时间'),
        "eduction": fields.selection([(u'博士', u'博士'), (u'硕士', u'硕士'), (u'本科', u'本科'), (u'专科', u'专科'), (u'中专', u'中专'), ],
                                     string=u'学历'),
        "yjfx": fields.char(u"研究方向", size=100),
        "cprz": fields.selection([("1", u"初识"), ("2", u"认可"), ("3", u"推荐")], string=u"产品认知"),
        "hospital_price": fields.float(u"临床收费", digits_compute=dp.get_precision('Product Price')),
        "city_id": fields.many2one("res.country.state.city", string=u"城市"),
        'function_sel': fields.selection(
            [(u"主任", u"主任"), (u"副主任", u"副主任"), (u"主治", u"主治"), (u'住院', u'住院'), (u'护士长', u'护士长'), (u'护士', u'护士'),
             (u'销售助理', u'销售助理'), (u'销售', u'销售')], u'职位'),

    }

    _defaults = {
        "date": fields.date.today,
        "amt": 0,
        "dev_user_id": lambda obj, cr, uid, context: uid,
        "user_id":lambda obj, cr, uid, context: uid,
    }

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
                "city": city_obj.name
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
                    val = {
                        "name": i.name,
                        "code": i.name,  # vals.get("partner_unid"),
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
                                                [('code', '=', i.name), ('partner_id', '=', i.id)],
                                                context=context)
                    if not wh:
                        id_s = stock_warehouse.create(cr, SUPERUSER_ID, val, context=context)
        return id

    def create(self, cr, uid, vals, context=None):
        if not vals.get('partner_unid'):
            if vals.get("use_parent_address"):
                parent = self.pool.get("res.partner").browse(cr,uid,vals.get("parent_id"),context=context)
                vals["city_id"] =parent.city_id.id
            if vals.get("state_id"):
                state_code = self.pool.get("res.country.state").browse(cr,uid,vals.get("state_id")).code
            if vals.get("city_id"):
                city_code = self.pool.get("res.country.state.city").browse(cr,uid,vals.get("city_id")).code
            cr.execute("select max(partner_unid) from res_partner where partner_unid like '%s'" % (
            state_code + city_code + '%',))
            for unid in cr.fetchall():
                max_id = unid[0]
            if max_id:
                max_id = max_id[:4] + str(int(max_id[4:]) + 1).zfill(4)
            else:
                max_id = state_code + city_code + '0001'
            vals['partner_unid'] = max_id
        if not (vals.get("customer") or vals.get("supplier")):
            if not vals.get('parent_id'):
               vals['parent_id'] = 1

        id = super(rhwl_partner, self).create(cr, uid, vals, context)
        partner = self.pool.get("res.company").search(cr, uid, [("id", '=', vals.get("company_id"))], context=context)
        if not partner:
            return id
        partner = self.pool.get("res.company").browse(cr, uid, partner, context=context)


        if vals.get("customer") and vals.get("is_company") and vals.get("sjjysj"):
            val = {
                "name": vals.get("name"),
                "code": vals.get("name"),  # vals.get("partner_unid"),
                "partner_id": id,
                "company_id": vals.get("company_id"),
                "buy_to_resupply": False,
                "default_resupply_wh_id": 0,
              }
            stock_warehouse = self.pool.get("stock.warehouse")

            default_id = stock_warehouse.search(cr, SUPERUSER_ID, [('partner_id', '=', partner.partner_id.id)],
                                                context=context)
            if not default_id:
                raise osv.except_osv(_('Error'), u"没有找到归属当前公司的仓库。")
            val["default_resupply_wh_id"] = default_id[0]
            val["resupply_wh_ids"] = [[6, False, [default_id[0]]]]
            wh = stock_warehouse.search(cr, SUPERUSER_ID,
                                        [('code', '=', vals.get("name")), ('partner_id', '=', id)],
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
                cus = {"name":i.name,"tel":i.phone,"website":i.website,"accept":'Y'}
                if not data.has_key(i.state_id.name):
                    data[i.state_id.name]={}
                if not data[i.state_id.name].has_key(i.city_id.name):
                    data[i.state_id.name][i.city_id.name]=[]
                data[i.state_id.name][i.city_id.name].append(cus)

        return data

class rhwl_country_state_city(osv.osv):
    _name = "res.country.state.city"

    _columns = {
        "state_id": fields.many2one("res.country.state", string="State"),
        "code": fields.char("Code", size=10),
        "name": fields.char("Name", size=20),

    }