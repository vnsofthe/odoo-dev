# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp import tools, api
import datetime
import logging

_logger = logging.getLogger(__name__)
class vnsoft_sale_order(osv.osv):
    _inherit = "sale.order"

    def do_create_purchase(self,cr,uid,ids,context=None):
        res=self.browse(cr,uid,ids,context=context)
        res_id=[]
        detail_id = self.pool.get("purchase.order").search(cr,uid,[('origin','=',res.name)],context=context)
        if detail_id:
            result = self.pool.get("product.template")._get_act_window_dict(cr, uid, 'purchase.purchase_rfq', context=context)
            result['domain'] = "[('id','in',[" + ','.join(map(str, detail_id)) + "])]"
            return result

        #for i in res.order_line:
            #res_id.append(self.pool.get("sale.order.purchase").create(cr,uid,{"name":res.id,"product_id":i.product_id.id},context=context))
        return {'type': 'ir.actions.act_window',
                'res_model': 'sale.order.purchase',
                'view_mode': 'form',
                #'view_id':'vnsoft023_view_sale_purchase',
                #'res_id': res_id,
                'target': 'new',
                'context':{"id":res.id},
                'flags': {'form': {'action_buttons': False}}}

class vnsoft_purchase_order_line(osv.osv):
    _inherit ="purchase.order.line"
    _columns={
        "sale_order_line_id":fields.integer("Sale Order Line ID"),
    }

class vnsoft_purchase(osv.osv_memory):
    _name = 'sale.order.purchase'
    _columns = {
        "name":fields.many2one("sale.order",u"销售单号",domain=[("state","in",["progress","manual"])]),
        "line":fields.one2many("sale.order.purchase.line","name",u"明细")
    }

    @api.onchange("name")
    def _onchange_salename(self):
        res=[]
        if self.line:
            self.line.unlink()
        if self.name:
            obj=self.env["sale.order"].browse(self.name.id)
            ids=[]
            for i in obj.order_line:
                id = self.env["purchase.order"].search([('origin','=',self.name.name),('order_line.product_id','=',i.product_id.id)])
                if not id:
                    ids.append({'name':self.id,'product_id':i.product_id.id,'product_qty':i.product_uom_qty,"sale_order_line_id":i.id})
            self.update({"line":ids})



    def default_get(self, cr, uid, fields, context=None):
        res = super(vnsoft_purchase,self).default_get(cr,uid,fields,context)
        if context.get("id"):
            id=context.get("id")
            obj=self.pool.get("sale.order").browse(cr,uid,id,context=context)
            res['name'] = id
            res['line']=[]
            for i in obj.order_line:
                res['line'].append({'product_id':i.product_id.id,'product_qty':i.product_uom_qty,"sale_order_line_id":i.id})

        return res

    def do_create(self,cr,uid,ids,context=None):
        d={}
        res_id=[]
        obj=self.browse(cr,uid,ids)

        for i in obj.line:
            if d.has_key(i.partner_id.id):
               d[i.partner_id.id].append([i.product_id.id,i.product_qty,i.sale_order_line_id])
            else:
               d[i.partner_id.id]=[[i.product_id.id,i.product_qty,i.sale_order_line_id]]

        #遍历有多少不同的供应商
        for k,v in d.items():
            #遍历供应商下有多少不同的产品

            pline=[]
            pick = self.pool.get("purchase.order")._get_picking_in(cr,uid)
            local = self.pool.get("purchase.order").onchange_picking_type_id(cr,uid,0,pick,context=context)

            val = self.pool.get("purchase.order").onchange_partner_id(cr,uid,0,k,context=context).get("value")
            val.update(local.get('value'))
            val.update({'picking_type_id':pick,'partner_id':k,'origin':obj.name.name,})
            for j in v:
                detail_val = self.pool.get("purchase.order.line").onchange_product_id(cr, uid, 0, val.get("pricelist_id"),j[0], j[1], False, k,val.get("date_order"),val.get("fiscal_position"),val.get("date_planned"),False,False,'draft',context=context).get("value")
                detail_val.update({'product_id':j[0],'product_qty':j[1],"sale_order_line_id":j[2]})
                pline.append([0,0,detail_val])

            val.update({'company_id':1,'order_line':pline})
            res_id.append(self.pool.get("purchase.order").create(cr,uid,val,context=context))

        result = self.pool.get("product.template")._get_act_window_dict(cr, uid, 'purchase.purchase_rfq', context=context)
        result['domain'] = "[('id','in',[" + ','.join(map(str, res_id)) + "])]"
        return result

class vnsoft_purchase_line(osv.osv_memory):
    _name = "sale.order.purchase.line"
    _columns = {
        "name":fields.many2one("sale.order.purchase",u"销售单号"),
         "product_id":fields.many2one("product.product",u"产品"),
         "product_qty": fields.float(u'数量', digits_compute=dp.get_precision('Product Unit of Measure'),
                                    required=True),
        "partner_id":fields.many2one("res.partner",u"供应商",domain="[('supplier','=',True)]"),
        "sale_order_line_id":fields.integer("Sale Order Line ID")
    }
