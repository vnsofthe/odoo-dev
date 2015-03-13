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
    }
    _defaults={
        "qualification":'draft'
    }