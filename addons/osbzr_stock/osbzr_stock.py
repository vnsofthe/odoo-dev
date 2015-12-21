# -*- coding: utf-8-*- 

from openerp import models,api,_,tools
from openerp.osv import osv,fields
import decimal

class stock_transfer_details(osv.TransientModel):
    _inherit = 'stock.transfer_details'
    @api.one
    def do_detailed_transfer(self):
        '''
                    移动时检查输入的产品、库位、批次、包装、数量是否足够
        '''
        plan_qty={}  #移库单上的产品数量
        tran_qty={}  #transfer上的产品数量
        res={}       #增加搜索条件（区别于tran_qty），查出要出库的产品的列表和数量。
        
        for line in self.picking_id.move_lines:
            if plan_qty.has_key(line.product_id.id):
                plan_qty[line.product_id.id]+=line.product_uom_qty
            else:
                plan_qty.update({line.product_id.id:line.product_uom_qty})
                
        for item in self.item_ids:
            if self.picking_id.picking_type_code=="incoming":
                continue       #只考虑出库单的情况
            if item.product_id.id not in plan_qty.keys():
                raise osv.except_osv(_(u'错误'), _(u'移动的产品 <%s> 不在移库单上！' % item.product_id.name))
            
            if tran_qty.has_key(item.product_id.id):
                tran_qty[item.product_id.id]+=item.quantity
            else:
                tran_qty.update({item.product_id.id:item.quantity})
                
            new_key = (item.product_id.id,item.sourceloc_id.id,item.lot_id.id,item.package_id.id)
            if res.has_key(new_key):
                res[new_key] += item.quantity
            else:
                res.update({new_key:item.quantity})
                
        for key in tran_qty.keys():
            if tran_qty[key] > plan_qty[key]:
                raise osv.except_osv(_(u'错误'), _(u'移动的产品 <%s> 数量不能大于该产品移库单上的数量！' % self.env['product.product'].browse(key).name))
                      
        for key in res.keys():
            all_number=0 #stock.quant中出库单上产品的库存数量
            #循环得出stock.quant中包含（产品，库位，批次，包装）的列表
            for quant in self.env['stock.quant'].search([('product_id','=',key[0]),('location_id','=',key[1]),('lot_id','=',key[2]),('package_id','=',key[3])]):
                all_number += quant.qty                   
                    
            #检查产品数量是否正确
            if decimal.Decimal(str(all_number)) < decimal.Decimal(str(res[key])): #使用decimal来保证精度正确
                raise osv.except_osv(_(u'错误'), _(u'移动的产品 <%s> 数量不能大于该产品的库存数量！' % self.env['product.product'].browse(key[0]).name))
        return super(stock_transfer_details,self).do_detailed_transfer()

'''
库存周转天数（库存周转率）= 一个月每天平均库存金额（不含VAT）/一个月发货材料成本（不含VAT）*30

要求针对产品和产品类别各出一个列表

实现思路：根据stock.move填充产品每天的库存数据，根据out的stock.move的quant取发出成本（新建一个表存储下来）
'''

class stock_daily(osv.osv):
    _name = 'stock.daily'
    _auto = False
    _rec_name = 'date'
    _columns = {
            'date':fields.date(u'日期'),
            'month':fields.char(u'月份'),
            'location_id':fields.many2one('stock.location',u'库位'),
            'product_id':fields.many2one('product.product',u'产品'),
            'categ_id':fields.related('product_id','categ_id',type='many2one',relation='product.category',string=u'分类'),
            'qty_begin':fields.float(u'期初数量'),
            'amt_begin':fields.float(u'期初余额'),
            'qty_in':fields.float(u'入库数量'),
            'amt_in':fields.float(u'入库成本'),
            'qty_out':fields.float(u'出库数量'),
            'amt_out':fields.float(u'发出成本'),
            'qty_end':fields.float(u'结存数量'),
            'amt_end':fields.float(u'结存余额'),
        }
        
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'stock_daily')
        cr.execute("""
            CREATE OR REPLACE VIEW stock_daily AS (
                SELECT moves.id,
                       moves.date,
                       substring(moves.cdate FROM 1 FOR 7) AS month,
                       moves.location_id,
                       moves.product_id,
                       (SELECT sum(CASE WHEN location_dest_id=moves.location_id THEN product_qty WHEN location_id=moves.location_id THEN -product_qty ELSE 0 end) FROM stock_move 
                       WHERE date::date<moves.date AND product_id=moves.product_id AND state='done') AS qty_begin,
                       (SELECT sum(CASE WHEN location_dest_id=moves.location_id THEN product_qty*price_unit WHEN location_id=moves.location_id THEN -product_qty*price_unit ELSE 0 end) FROM stock_move 
                       WHERE date::date<moves.date AND product_id=moves.product_id AND state='done') AS amt_begin,
                       (SELECT sum(product_qty) FROM stock_move 
                       WHERE date::date<=moves.date AND product_id=moves.product_id AND state='done' AND location_dest_id=moves.location_id) AS qty_in,
                       (SELECT sum(product_qty*price_unit) FROM stock_move 
                       WHERE date::date<=moves.date AND product_id=moves.product_id AND state='done' AND location_dest_id=moves.location_id) AS amt_in,
                       (SELECT sum(product_qty) FROM stock_move 
                       WHERE date::date<=moves.date AND product_id=moves.product_id AND state='done' AND location_id=moves.location_id) AS qty_out,
                       (SELECT sum(product_qty*price_unit) FROM stock_move 
                       WHERE date::date<=moves.date AND product_id=moves.product_id AND state='done' AND location_id=moves.location_id) AS amt_out,
                       (SELECT sum(CASE WHEN location_dest_id=moves.location_id THEN product_qty WHEN location_id=moves.location_id THEN -product_qty ELSE 0 end) FROM stock_move 
                       WHERE date::date<=moves.date AND product_id=moves.product_id AND state='done') AS qty_end,
                       (SELECT sum(CASE WHEN location_dest_id=moves.location_id THEN product_qty*price_unit WHEN location_id=moves.location_id THEN -product_qty*price_unit ELSE 0 end) FROM stock_move 
                       WHERE date::date<=moves.date AND product_id=moves.product_id AND state='done') AS amt_end
                FROM (
                       SELECT DISTINCT id, to_char(date, 'YYYY-MM-DD') AS cdate,date::date,product_id,location_id FROM stock_move WHERE state='done'
                       UNION 
                       SELECT DISTINCT id, to_char(date, 'YYYY-MM-DD') AS cdate,date::date,product_id,location_dest_id FROM stock_move WHERE state='done') moves
                ORDER BY product_id ,location_id,date

            )""")
    