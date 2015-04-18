# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
import datetime

class vnsoft_purchase(osv.osv):
    _inherit = "purchase.order"

    _columns={
        "order_kind":fields.selection([("internal",u"国内"),("export",u"进口"),("export_approve",u"进口审批")],string="Order Kind"),
        "tariff":fields.float('Tariff', digits_compute=dp.get_precision('Product Price')),
        "web_receive":fields.boolean("Web Receive"),
        "web_id":fields.integer('Web ID'),
    }

    _defaults={
        "web_receive":False
    }

    def get_columns_values(self,cr,uid,partner_id,context=None):
        pick = self.pool.get("purchase.order")._get_picking_in(cr,uid)
        local = self.pool.get("purchase.order").onchange_picking_type_id(cr,uid,0,pick,context=context)
        val = self.pool.get("purchase.order").onchange_partner_id(cr,uid,0,partner_id,context=context).get("value")
        val.update(local.get('value'))
        val.update({'picking_type_id':pick,'partner_id':partner_id})
        return val

class vnsoft_purchase_line(osv.osv):
    _inherit="purchase.order.line"
    _columns={
        "qualification":fields.selection([('draft','draft'),('done','done'),('cancel','cancel')],"Qualification"),
        "web_id":fields.integer('Web ID'),
        "active":fields.boolean("Active"),
    }
    _defaults={
        "qualification":'draft',
        "active":True
    }
    def write(self,cr,uid,ids,val,context=None):
        if val.get("qualification","draft")=="cancel":
            val['active']=False
        return super(vnsoft_purchase_line,self).write(cr,uid,ids,val,context=context)

class vnsoft_sale_purchase(osv.osv_memory):
    _inherit = 'sale.order.purchase'

    def do_create(self,cr,uid,ids,context=None):
        result = super(vnsoft_sale_purchase,self).do_create(cr,uid,ids,context=context)
        obj=self.browse(cr,uid,ids)
        sale_obj = self.pool.get("sale.order").browse(cr,uid,obj.name.id,context=context)
        id = self.pool.get("purchase.order").search(cr,uid,[('origin','=',obj.name.name)],context=context)
        self.pool.get("purchase.order").write(cr,uid,id,{"order_kind":sale_obj.order_kind},context=context)
        return result

class vnsoft_purchase_order_group(osv.osv_memory):
    _inherit = "purchase.order.group"

    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        res = super(vnsoft_purchase_order_group,self).fields_view_get(cr,uid,view_id,view_type,context,toolbar,submenu)
        if context.get('active_model','') == 'purchase.order':

            for i in self.pool.get("purchase.order").browse(cr,uid,context['active_ids']):
                if i.order_kind!="internal":
                    raise osv.except_osv(u"错误",u"选择的采购订单中，有进口订单，不可以合并。")
        return res
