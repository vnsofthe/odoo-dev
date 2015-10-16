# -*- coding: utf-8 -*-

from openerp import tools
from openerp.osv import fields, osv

class rhwl_sample_report(osv.osv):
    _name = "rhwl.sample.report"
    _description = "Sample Orders Statistics"
    _auto = False
    _rec_name = 'name'

    _columns={
        "name": fields.char(u"样品编号", required=True, size=20),
        "cx_date": fields.date(u'采血时间', required=True),
        "receiv_user": fields.many2one('res.users', string=u'收样人员'),
        #"state_id": fields.many2one('res.country.state', string=u'样品区域（省）',domain="[('country_id.code','=','CN')]"),
        "state_id": fields.related('cxyy', 'state_id', relation="res.country.state", type='many2one', string=u'样品区域（省）', readonly=1, store=True),
        #"city_id": fields.many2one("res.country.state.city", string=u"样品区域（市)",domain="[('state_id','=',state_id)]"),
        "city_id": fields.related('cxyy', 'city_id', relation="res.country.state.city", type='many2one', string=u'样品区域（市)', readonly=1, store=True),
        "lyyy": fields.many2one('res.partner', string=u'来源医院'),
        "cxyy": fields.many2one('res.partner', string=u'采血医院',),
        "lyys": fields.many2one('res.partner', string=u'来源医生',),
        "cxys": fields.many2one('res.partner', string=u'采血医生',),
        "is_reused": fields.selection([('0', u'首次采血'), ('1', u'重采血')], u'是否重采血'),
        "is_free": fields.selection([('1', u'是'), ('0', u'否')], u'是否免费', required=True),
        "check_state": fields.selection(
            [('get', u'已接收'), ('library', u'已进实验室'), ('pc', u'已上机'), ('reuse', u'需重采血'), ('ok', u'检验结果正常'),
             ('except', u'检验结果阳性')], u'检验状态'),
        "amt":fields.float("Amt"),
        "sale_user":fields.many2one('res.users', string=u'销售人员'),
    }

    def _select(self):
        select_str = """
             SELECT  a.id as id,
                    a.name as name,
                    a.cx_date as cx_date,
                    a.receiv_user as receiv_user,
                    a.state_id as state_id,
                    a.city_id as city_id,
                    a.lyyy as lyyy,
                    a.cxyy as cxyy,
                    a.lyys as lyys,
                    a.cxys as cxys,
                    a.is_reused as is_reused,
                    a.is_free as is_free,
                    a.check_state as check_state,
                    c.price_unit * c.product_uom_qty as amt,
                    b.user_id as sale_user
        """
        return select_str

    def _from(self):
        from_str = """
                sale_sampleone a
                join sale_order b on (a.cxys=b.partner_id and a.name = b.client_order_ref and b.state!='cancel')
                left join sale_order_line c on (b.id = c.order_id)
        """
        return from_str

    def _group_by(self):
        group_by_str = """

        """
        return group_by_str

    def init(self, cr):
        # self._table = sale_report
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM  %s
            %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))