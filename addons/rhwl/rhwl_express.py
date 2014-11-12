# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
import datetime
import re


class rhwl_express(osv.osv):
    _inherit = "stock.picking.express"

    def _get_check_user(self, cr, uid, context=None):
        """判断用户是内部人员还是外部人员。"""
        if context is None:
            context = {}
        id = self.pool.get("res.partner").search(cr, SUPERUSER_ID, [("zydb", "=", uid)],
                                                 context=context)  # 检查用户是否为某客户的驻院代表
        if id:
            return [False, id]  # 某用户是驻院代表，则直接判断为外部人员
        else:
            user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, uid, context=context)
            if not user.partner_id:
                return [False, None]
            id = user.partner_id.parent_id.id and user.partner_id.parent_id.id or user.partner_id.id

            return [id == 1, id]


    def _get_partner_address(self, cr, uid, ids, context=None):
        """得取用户对应业务伙伴的联系地址。"""
        if context is None:
            context = {}
        user = self._get_check_user(cr, ids, context=context)
        id = user[-1]
        if id:
            if isinstance(id, (list, tuple)):
                id = id[0]

            partner = self.pool.get("res.partner").browse(cr, uid, id, context=context)
            if partner.parent_id and partner.use_parent_address:
                res = [partner.parent_id.state_id.name, partner.parent_id.city,
                       partner.parent_id.street, partner.parent_id.street2]
            else:
                res = [partner.state_id.name, partner.city, partner.street,
                       partner.street2]
        else:
            res = []

        res = [x for x in res if x]
        return ','.join(res) or ""

    def _get_addr(self, cr, uid, context=None):
        """新增时，带出作业人员对应的联系地址。"""
        return self._get_partner_address(cr, uid, uid, context)

    def get_address(self, cr, uid, ids, user, colname, context=None):
        """人员栏位修改时，带出对应的联系地址。"""
        return {
            "value": {
                colname: self._get_partner_address(cr, uid, user, context),
            }
        }

    def get_num_express(self, cr, uid, ids, deliver, context=None):
        partner = self.pool.get("res.partner").browse(cr, uid, deliver, context=context)
        if partner.comment:
            listno = re.split('[^0-9]', partner.comment)
            lastnum = listno[-1]
            newnum = str(long(lastnum) + 1).zfill(lastnum.__len__())
            self.pool.get("res.partner").write(cr, uid, deliver,
                                               {"comment": partner.comment[0:-newnum.__len__()] + newnum},
                                               context=context)
        return {
            "value": {
                "num_express": partner.comment
            }
        }

    def _get_first_deliver(self, cr, uid, context=None):
        deliver = self.pool.get("res.partner").search(cr, uid, [("is_deliver", "=", True)], context=context)
        if isinstance(deliver, (long, int)):
            return deliver
        if isinstance(deliver, (list, tuple)):
            return deliver[0]
        return False

    def _get_product_id(self, cr, uid, context=None):
        product_id = self.pool.get("product.product").search(cr, uid, [('sale_ok', '=', True), ("active", "=", True)],
                                                             context=context)
        if isinstance(product_id, (list, tuple)):
            product_id = product_id[0]
        return product_id

    def _fun_is_company(self, cr, uid, ids, prop, arg, context=None):
        if isinstance(ids, (list, tuple)) and not len(ids):
            return {}
        if isinstance(ids, (long, int)):
            ids = [ids]
        # if SUPERUSER_ID == uid:
        # return dict([(id, True) for id in ids])
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
        "product_id": fields.many2one('product.product', 'Product',
                                      domain=[('sale_ok', '=', True), ("active", "=", True)], required=True,
                                      change_default=True),
        "product_qty": fields.float(u'发货数量', digits_compute=dp.get_precision('Product Unit of Measure'),
                                    required=True),
        "receiv_real_user": fields.many2one('res.users', string=u'实际收货人员'),
        "receiv_real_date": fields.datetime('Realy Date Receiv'),
        "receiv_real_qty": fields.float(u'实际收货数量', digits_compute=dp.get_precision('Product Unit of Measure'),
                                        required=True),
        "is_deliver": fields.function(_fun_is_company, type="boolean", string=u"发货方"),
        "is_receiv": fields.function(_fun_is_company, type="boolean", string=u"收货方"),
        "detail_ids": fields.one2many("stock.picking.express.detail", "parent_id", u"收货明细"),
    }

    _defaults = {
        'date': fields.datetime.now,
        'deliver_user': lambda obj, cr, uid, context: uid,
        "receiv_date": lambda obj, cr, uid, context: datetime.timedelta(3) + datetime.datetime.now(),
        "deliver_addr": _get_addr,
        "deliver_id": _get_first_deliver,
        "product_id": _get_product_id,
    }


class rhwl_express_in(osv.osv):
    _name = "stock.picking.express.detail"
    _columns = {
        'parent_id': fields.many2one("stock.picking.express", string="物流单号"),
        'number_seq': fields.char(u"样品编号", size=20),
        'number_seq_ori': fields.char(u"原样品编号", size=20),
        "in_flag": fields.boolean(u"收货"),
        "out_flag": fields.boolean(u'发货')
    }
