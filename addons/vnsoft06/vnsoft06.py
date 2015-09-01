# -*- coding: utf-8 -*-

from openerp import tools
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class rhwl_sample_report(osv.osv):
    _name = "vnsoft.stock.move.input"
    _description = "Stock Move for Supplier"
    _auto = False
    _rec_name = 'product_id'

    _columns={
        'product_id': fields.many2one("product.product",string="Product"),
        'date': fields.datetime('Date'),
        'product_uom': fields.many2one('product.uom', 'Unit of Measure', required=True,),
        'product_uom_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product Unit of Measure')),
        'move_type':fields.selection([('in',"IN"),('out',"OUT")],"Move Type")
    }

    def _select(self):
        select_str = """
             SELECT  a.id as id,
                    a.product_id as product_id,
                    a.date as date,
                    d.uom_id as product_uom,
                    a.product_qty as product_uom_qty,
                    (case when a.location_id =b.id and b.usage='supplier' then 'in' else 'out' end) as move_type
        """
        return select_str

    def _from(self):
        from_str = """
                stock_move a
                join stock_location b on ((a.location_id =b.id and b.usage='supplier') or (a.location_dest_id=b.id and b.usage='production'))
                join product_product c on (a.product_id =c.id and c.active=true)
                join product_template d on (c.product_tmpl_id=d.id and d.active=true)
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