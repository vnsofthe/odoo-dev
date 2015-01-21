# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
import datetime
from openerp.tools.translate import _
from openerp import tools

class vnsof_stock_change(osv.osv):
    _name = "stock.change"
    _description = "库存产品拆分"

    _columns = {
        "name":fields.char("Name",readonly=True),
        "product_from":fields.many2one("product.product","Product From",required=True,readonly=True,states={'draft':[('readonly',False)]}),
        "location_from":fields.many2one("stock.location","From Location",required=True,domain=[('usage', '=', 'internal')],readonly=True,states={'draft':[('readonly',False)]}),
        "from_qty":fields.float("Qty of From",digits_compute=dp.get_precision('Product Unit of Measure'),required=True,readonly=True,states={'draft':[('readonly',False)]}),
        "date":fields.date("Date"),
        "user_id":fields.many2one("res.users","User",readonly=True),
        "state":fields.selection([("draft","Draft"),("done","Done"),("cancel","Cancel")],"State"),
        "line":fields.one2many("stock.change.line","change_id",string="Line",required=True,readonly=True,states={'draft':[('readonly',False)]})
    }
    _defaults={
        "state":"draft",
        "date":fields.date.today,
        "user_id":lambda obj,cr,uid,context:uid
    }


    def _check_product(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context=context)
        for i in obj.line:
            if obj.product_from and i.product_to and obj.product_from==i.product_to:
                return False
        return True

    def _check_qty(self,cr,uid,ids,context=None):
        obj = self.browse(cr, uid, ids[0], context=context)
        for i in obj.line:
            if obj.from_qty<=0 or i.rate<=0:
                return False
        return True

    _constraints = [
        (_check_product, u'拆分前产品不能与拆分后产品相同.', ["product_from","product_to"]),
        (_check_qty,u"拆分前后的数量都必须大于0",["from_qty","to_qty"]),
    ]

    def action_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'cancel'}, context=context)

    def action_done(self, cr, uid, ids, context=None):
        if context is None:
           context = {}

        inventory_obj = self.pool.get('stock.inventory')
        inventory_line_obj = self.pool.get('stock.inventory.line')

        for i in self.browse(cr,uid,ids,context):
            if not i.line:
                raise osv.except_osv(u"错误",u"没有拆分出子产品，不可以确认。")

            product = i.product_from.with_context(location=i.location_from.id)
            if i.from_qty > product.qty_available:
                raise osv.except_osv(u"错误",u"拆包原产品数量[%d]不能大于产品在手数量[%d]。" %(i.from_qty,i.product_from.qty_available))
            #处理拆包前的产品调整
            inventory_id = inventory_obj.create(cr, uid, {
                'name': u'拆包: %s' % tools.ustr(i.product_from.name),
                'product_id': i.product_from.id,
                'location_id': i.location_from.id}, context=context)
            th_qty = product.qty_available
            line_data = {
                'inventory_id': inventory_id,
                'product_qty': th_qty - i.from_qty,
                'location_id': i.location_from.id,
                'product_id': i.product_from.id,
                'product_uom_id': i.product_from.uom_id.id,
                'theoretical_qty': th_qty
            }
            inventory_line_obj.create(cr , uid, line_data, context=context)
            inventory_obj.action_done(cr, uid, [inventory_id], context=context)
            #处理拆包后产品调整
            amt = i.product_from.standard_price * i.from_qty #拆包前产品的总计成本金额
            amt_line={} #记录每个子产品拆分后数量*成本价的金额
            for l in i.line:
                if l.product_to.cost_method=="average":
                    amt_line[l.product_to.id] = l.product_to.standard_price * i.from_qty * l.rate
            for l in i.line:
                #调整拆包后产品的成本单价
                if amt_line.get(l.product_to.id):
                    #新的单价 = (库存单价*库存数量 + 原产品总成本金额*(子产品拆分成本/总计子产品拆分成本)) / (库存数量 + 子产品拆分数量)
                    new_price = (l.product_to.standard_price * l.product_to.qty_available + amt*((l.product_to.standard_price*l.rate*i.from_qty)/sum(amt_line.values()))) / (l.product_to.qty_available+l.rate*i.from_qty)
                    self.pool.get("product.product").write(cr,uid,l.product_to.id,{"standard_price":new_price})
                product = l.product_to.with_context(location=l.location_to.id)
                inventory_id = inventory_obj.create(cr, uid, {
                    'name': u'拆包: %s' % tools.ustr(l.product_to.name),
                    'product_id': l.product_to.id,
                    'location_id': l.location_to.id}, context=context)
                th_qty = product.qty_available
                line_data = {
                    'inventory_id': inventory_id,
                    'product_qty': th_qty + i.from_qty*l.rate,
                    'location_id': l.location_to.id,
                    'product_id': l.product_to.id,
                    'product_uom_id': l.product_to.uom_id.id,
                    'theoretical_qty': th_qty
                }
                inventory_line_obj.create(cr , uid, line_data, context=context)
                inventory_obj.action_done(cr, uid, [inventory_id], context=context)
        self.write(cr, uid, ids, {'state': 'done'}, context=context)

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if vals.get('name', '/') == '/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'stock.change') or '/'
        return super(vnsof_stock_change,self).create(cr,uid,vals,context)

class vnsof_stock_change_line(osv.osv):
    _name = "stock.change.line"
    _description = "库存产品拆分明细"

    _columns={
        "change_id":fields.many2one("stock.change","Change ID"),
        "product_to":fields.many2one("product.product","Product To",required=True),
        "location_to":fields.many2one("stock.location","To Location",required=True,domain=[('usage', '=', 'internal')]),
        "rate":fields.float("Rate",digits_compute=dp.get_precision('Product Unit of Measure'),required=True,help=u"1个单位原产品可以拆分成多少个单位的子产品？"),
    }
    _sql_constraints = [
        ('stock_change_line_uniq', 'unique(change_id,product_to)', u'明细清单中相同产品不能重复!'),

    ]