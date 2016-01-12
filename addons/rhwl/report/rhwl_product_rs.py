# -*- coding: utf-8 -*-

from openerp import tools
from openerp.osv import fields, osv

class rhwl_sample_report(osv.osv):
    _name = "rhwl.product.rs"
    _description = "product Statistics"
    _auto = False
    _rec_name = 'name'

    _columns={
        "name": fields.char(u"探针编号", required=True, size=50),
        "project_name": fields.char(u'检测项目', required=True,size=100),
        "qty": fields.float(u"可作样本数"),
    }

    def _select(self):
        select_str = """
             select a.id as id
                    ,a.name_template as name
                    ,c.name as project_name
                    ,b.sample_count as qty
        """
        return select_str

    def _from(self):
        from_str = """
                product_product a
                join rhwl_product_project b on a.id=b.product_id
                join res_company_project c on b.project_id=c.id
                where a.name_template like '探针%'
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


class rhwl_product_stock_rs_report(osv.osv):
    _name = "rhwl.product.stock.rs"
    _description = "product Statistics"
    _auto = False
    _rec_name = 'name'

    _columns={
        "name": fields.char(u"探针编号", required=True, size=50),
        "project_name": fields.char(u'检测项目', required=True,size=100),
        "qty": fields.float(u"可作样本数"),
    }

    def _select(self):
        select_str = """
             select a.id as id
                    ,a.name_template as name
                    ,c.name as project_name
                    ,d.qty*b.sample_count as qty
        """
        return select_str

    def _from(self):
        from_str = """
                product_product a
                join rhwl_product_project b on a.id=b.product_id
                join res_company_project c on b.project_id=c.id
                left join (select stock_quant.product_id as product_id,sum(stock_quant.qty) as qty from stock_quant,stock_location where stock_quant.location_id=stock_location.id and stock_location.usage='internal' group by stock_quant.product_id) d on a.id = d.product_id
                where a.name_template like '探针%'
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