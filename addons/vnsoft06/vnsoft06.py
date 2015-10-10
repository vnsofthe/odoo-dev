# -*- coding: utf-8 -*-

from openerp import tools
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
import logging
from openerp import SUPERUSER_ID

_logger = logging.getLogger(__name__)
class rhwl_sample_report(osv.osv):
    _name = "vnsoft.stock.move.input"
    _description = "Stock Move for Supplier"
    _auto = False
    _rec_name = 'product_id'

    def _get_invoice(self,cr,uid,ids,field_names,arg,context=None):
        res={}
        for id in ids:
            move_obj = self.pool.get("stock.move").browse(cr,uid,id,context=context)
            res[id]=False
            if move_obj.purchase_line_id:
                for inv in move_obj.purchase_line_id.invoice_lines:
                    if inv.invoice_id.state in ("open","paid"):
                        res[id]=True
                    else:
                        res[id]=False
            else:
                for q in move_obj.quant_ids:
                    for h in q.history_ids:
                        if h.purchase_line_id != False and h.state=="done":
                            for inv in h.purchase_line_id.invoice_lines:
                                if inv.invoice_id.state in ("open","paid"):
                                    res[id]=True
                                else:
                                    res[id]=False
        return res

    def _get_project(self,cr,uid,ids,fields_names,arg,context=None):
        res={}
        for id in ids:
            move_obj = self.pool.get("stock.move").browse(cr,uid,id,context=context)
            res[id]=""
            if move_obj.picking_id and move_obj.picking_id.project:
                res[id]=move_obj.picking_id.project.name

        return res

    def _get_supplier(self,cr,uid,ids,fields_names,arg,context=None):
        res={}
        for id in ids:
            move_obj = self.pool.get("stock.move").browse(cr,uid,id,context=context)
            res[id]=""
            if move_obj.purchase_line_id:
                res[id]=move_obj.purchase_line_id.partner_id.name

        return res

    def _get_period(self,cr,uid,ids,fields_names,arg,context=None):
        res={}
        for id in ids:
            move_obj = self.pool.get("stock.move").browse(cr,uid,id,context=context)
            res[id]=""
            if move_obj.purchase_line_id:
                for inv in move_obj.purchase_line_id.invoice_lines:
                    if inv.invoice_id.state in ("open","paid"):
                        res[id]= inv.invoice_id.period_id.name
                    else:
                        res[id]=""
            else:
                picking_origin = move_obj.picking_id.origin
                request_ids = self.pool.get("rhwl.library.request").search(cr,uid,[("name","=",picking_origin)])
                if request_ids:
                    request_obj = self.pool.get("rhwl.library.request").browse(cr,uid,request_ids,context=context)
                else:
                    request_ids = self.pool.get("rhwl.library.consump").search(cr,uid,[("name","=",picking_origin)])
                    if request_ids:
                        request_obj = self.pool.get("rhwl.library.consump").browse(cr,uid,request_ids,context=context)
                    else:
                        request_obj = None

                for q in move_obj.quant_ids:
                    for h in q.history_ids:
                        if h.purchase_line_id != False and h.state=="done":
                            for inv in h.purchase_line_id.invoice_lines:
                                if inv.invoice_id.state in ("open","paid"):
                                    if request_obj and request_obj.date > inv.invoice_id.period_id.date_start:
                                        period_ids = self.pool.get("account.period").search(cr,SUPERUSER_ID,[("date_stop",">=",request_obj.date),("date_start","<=",request_obj.date),("special","=",False)],context=context)
                                        period_obj = self.pool.get("account.period").browse(cr,SUPERUSER_ID,period_ids,context=context)
                                        res[id]=period_obj.name
                                    elif request_obj:
                                        res[id]=inv.invoice_id.period_id.name
                                else:
                                    res[id]=""
        return res

    _columns={
        'product_id': fields.many2one("product.product",string="Product",auto_join=True),
        'date': fields.datetime('Date'),
        'product_uom': fields.many2one('product.uom', 'Unit of Measure', required=True,),
        'product_uom_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product Unit of Measure')),
        'move_type':fields.selection([('in',"IN"),('out',"OUT")],"Move Type"),
        "amt":fields.float("Amt",digits_compute= dp.get_precision('Product Price')),
        "invoice":fields.function(_get_invoice,type="boolean",string="Invoice"),
        "project":fields.function(_get_project,type="char",string="Project"),
        "partner":fields.function(_get_supplier,type="char",string="Supplier"),
        "period":fields.function(_get_period,type="char",string="Period"),
    }

    def _select(self):
        select_str = """
             SELECT  a.id as id,
                    a.product_id as product_id,
                    a.date as date,
                    d.uom_id as product_uom,
                    a.product_qty as product_uom_qty,
                    (case when a.location_id =b.id and b.usage='supplier' then 'in' else 'out' end) as move_type,
                    a.product_qty * a.price_unit as amt
        """
        return select_str

    def _from(self):
        from_str = """
                stock_move a
                join stock_location b on ((a.location_id =b.id and b.usage='supplier') or (a.location_dest_id=b.id and b.usage='production'))
                join product_product c on (a.product_id =c.id and c.active=true)
                join product_template d on (c.product_tmpl_id=d.id and d.active=true)
                where a.state='done'
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