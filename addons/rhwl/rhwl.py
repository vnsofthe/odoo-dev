# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
import datetime


class rhwl_hr(osv.osv):
    _name = "hr.employee"
    _description = "Employee"
    _inherit = "hr.employee"

    _columns = {
        "work_number": fields.char(u"工号", required=True),
    }
    _sql_constraints = [
        ('work_number_uniq', 'unique(work_number)', u'工号必须唯一!'),
    ]


class rhwl_partner(osv.osv):
    _name = "res.partner"
    _description = "Partner"
    _inherit = "res.partner"

    _columns = {
        "partner_unid": fields.char(u"编号", required=True),
        "dev_user_id": fields.many2one('res.users', string=u'开发人员'),
        "cust_level": fields.selection([('AA', 'AA'), ('AB', 'AB'), ('BC', 'BC'), ('CC', 'CC')], u'客户级别'),
        "hospital_level": fields.selection([(u'二级以下', u'二级以下'), (u'二乙', u'二乙'), (u'二甲', u'二甲'), (u'三甲', u'三甲')],
                                           u'医院等级'),
        "cust_type": fields.selection([(u'私立', u'私立'), (u'公立', u'公立')], u'客户性质'),
    }

    _sql_constraints = [
        ("partner_unid_uniq", "unique(partner_unid)", u"编号必须为唯一!"),
    ]


class rhwl_express(osv.osv):
    _inherit = "stock.picking.express"

    def _get_partner_address(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        user = self.pool.get('res.users').browse(cr, uid, ids, context=context)
        if not user.partner_id:
            return False
        if user.partner_id.parent_id and user.partner_id.use_parent_address:
            res = [user.partner_id.parent_id.state_id.name, user.partner_id.parent_id.city,
                   user.partner_id.parent_id.street, user.partner_id.parent_id.street2]
        else:
            res = [user.partner_id.state_id.name, user.partner_id.city, user.partner_id.street, user.partner_id.street2]

        res = [x for x in res if x]
        return ','.join(res) or ""

    def _get_addr(self, cr, uid, context=None):
        return self._get_partner_address(cr, uid, uid, context)

    def get_address(self, cr, uid, ids, user, colname, context=None):
        return {
            "value": {
                colname: self._get_partner_address(cr, uid, user, context),
            }
        }

    def _fun_is_company(self, cr, uid, ids, prop, arg, context=None):
        if isinstance(ids, (list, tuple)) and not len(ids):
            return {}
        if isinstance(ids, (long, int)):
            ids = [ids]
        # if SUPERUSER_ID == uid:
        #    return dict([(id, True) for id in ids])
        user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, uid, context=context)
        if not user.partner_id:
            return dict([(id, False) for id in ids])
        if user.partner_id.is_company:
            curr_company = user.partner_id.id
        else:
            if not user.partner_id.parent_id:
                return dict([(id, False) for id in ids])
            curr_company = user.partner_id.parent_id.id

        res = self.browse(cr, SUPERUSER_ID, ids, context=context)
        if not res:
            return {}
        result = []
        for k in res:
            if prop == "is_deliver":
                userid = k.deliver_user
            elif prop == "is_receiv":
                userid = k.receiv_user
            else:
                userid = None

            if not userid:
                result.append((k.id, False))
            else:
                if not userid.partner_id:
                    result.append((k.id, False))
                if userid.partner_id.is_company:
                    result.append((k.id, userid.partner_id.id == curr_company))
                else:
                    if not userid.partner_id.parent_id:
                        result.append((k.id, False))
                    else:
                        result.append((k.id, userid.partner_id.parent_id.id == curr_company))
        return dict(result)

    _columns = {
        "deliver_user": fields.many2one('res.users', string=u'发货人员'),
        "deliver_addr": fields.char(size=120, string=u"发货地址"),
        "receiv_user": fields.many2one('res.users', string=u'收货人员'),
        "receiv_date": fields.datetime('Date Receiv', required=True),
        "receiv_addr": fields.char(size=120, string=u"收货地址"),
        "product_id": fields.many2one('product.product', 'Product', domain=[('purchase_ok', '=', True)], required=True,
                                      change_default=True),
        "product_qty": fields.float('Quantity', digits_compute=dp.get_precision('Product Unit of Measure'),
                                    required=True),
        "receiv_real_user": fields.many2one('res.users', string=u'实际收货人员'),
        "receiv_real_date": fields.datetime('Realy Date Receiv'),
        "is_loss": fields.boolean(u"物品已丢失"),
        "is_deliver": fields.function(_fun_is_company, type="boolean", string=u"发货方"),
        "is_receiv": fields.function(_fun_is_company, type="boolean", string=u"收货方"),
    }

    _defaults = {
        'date': fields.datetime.now,
        'deliver_user': lambda obj, cr, uid, context: uid,
        "receiv_date": lambda obj, cr, uid, context: datetime.timedelta(3) + datetime.datetime.now(),
        "deliver_addr": _get_addr,
    }