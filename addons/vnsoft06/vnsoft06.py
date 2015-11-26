# -*- coding: utf-8 -*-

from openerp import tools
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
import logging
from openerp import SUPERUSER_ID
"""insert into stock_quant_move_rel
select distinct q.quant_id,tt.max_id
from (
select id,(select max(id) from stock_move where product_id=a.product_id and location_id=8) as max_id from stock_move a
where picking_id in (
select id from stock_picking where origin in (
select name from rhwl_library_request where date>='2015-09-01'
 union
select name from rhwl_library_consump where date>='2015-09-01')
)
and not exists (
select * from stock_move where location_id=8 and id in (
select move_id from stock_quant_move_rel where quant_id in (
select quant_id from stock_quant_move_rel where move_id=a.id)))) as tt
join stock_quant_move_rel q on (tt.id=q.move_id)
where tt.max_id is not null
and not exists (select * from stock_quant_move_rel where quant_id=q.quant_id and move_id=tt.max_id);
"""
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

            line_ids = self.pool.get("stock.move")._get_purchase_order_line(cr,SUPERUSER_ID,move_obj.id,context=context)
            if line_ids:
                for p in self.pool.get("purchase.order.line").browse(cr,SUPERUSER_ID,line_ids,context=context):
                    for inv in p.invoice_lines:
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
        "request_no":fields.char("Request No",size=10),
        "request_date":fields.date("Request Date"),
        "invoice":fields.function(_get_invoice,type="boolean",string="Invoice"),
        "project":fields.many2one("res.company.project",string="Project",),
        "partner":fields.char("Supplier"),
        "period":fields.function(_get_period,type="char",string="Period"),
    }

    def action_check(self,cr,uid,ids,context=None):
        obj = self.pool.get("stock.move").browse(cr,uid,ids,context=context)
        msg=""
        if obj.location_id.usage=="supplier":
            msg += u"单据类型为入库单,"
            if obj.purchase_line_id:
                msg += u"采购单号为："+obj.purchase_line_id.order_id.name+u","
                if not obj.purchase_line_id.invoice_lines:
                    msg += u"发票未开立,"
                for inv in obj.purchase_line_id.invoice_lines:
                    if inv.invoice_id.state in ("open","paid"):
                        msg += u"发票"+inv.invoice_id.name+u"已确认,"
                        msg += u"发票会计期间为"+inv.invoice_id.period_id.name+u","
                    else:
                        msg += u"发票"+inv.invoice_id.name+u"未确认,"
        elif obj.location_dest_id.usage=="production":
            msg += u"单据类型为出库单,"
            p_ids=[]
            for q in obj.quant_ids:
                for h in q.history_ids:
                    if h.location_id.usage=="supplier" and h.purchase_line_id != False and h.state=="done":
                        p_ids.append(h.purchase_line_id.id)
            if not p_ids:
                msg += u"没有找到关联的采购单，"
            else:
                for p in self.pool.get("purchase.order.line").browse(cr,uid,p_ids,context=context):
                    msg += u"关联的采购单:"+p.order_id.name+u","
                    if not p.invoice_lines:
                        msg += u"发票未开立,"
                    for inv in p.invoice_lines:
                        if inv.invoice_id.state in ("open","paid"):
                            msg += u"发票"+inv.invoice_id.name+u"已确认,"
                            msg += u"发票会计期间为"+inv.invoice_id.period_id.name+u","
                        else:
                            msg += u"发票"+inv.invoice_id.name+u"未确认,"
        if msg:
            raise osv.except_osv("Message",msg)

    def _select(self):
        select_str = """
             SELECT  a.id as id,
                    a.product_id as product_id,
                    a.date as date,
                    d.uom_id as product_uom,
                    a.product_qty as product_uom_qty,
                    (case when a.location_id =b.id and b.usage='supplier' then 'in' else 'out' end) as move_type,
                    a.product_qty * a.price_unit as amt,
                    f.name as request_no,
                    f.date as request_date,
                    i.name as partner,
                    e.project as project
        """
        return select_str

    def _from(self):
        from_str = """
                stock_move a
                join stock_location b on ((a.location_id =b.id and b.usage='supplier') or (a.location_dest_id=b.id and b.usage='production'))
                join product_product c on (a.product_id =c.id and c.active=true)
                join product_template d on (c.product_tmpl_id=d.id and d.active=true)
                left join purchase_order_line g on (a.purchase_line_id=g.id)
                left join purchase_order h on (g.order_id=h.id)
                left join res_partner i on (h.partner_id=i.id)
                left join stock_picking e on (a.picking_id = e.id)
                left join (select name,date from rhwl_library_request
                        union
                      select name,date from rhwl_library_consump) f on ( e.origin=f.name)
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