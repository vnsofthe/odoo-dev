# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
import datetime

class vnsoft_sale(osv.osv):
    _inherit = "sale.order"

    _columns={
        "research_group":fields.char("Research Group",size=50),
        "order_user":fields.many2one("res.partner",string="Order User")
    }

    def action_invoice_create(self, cr, uid, ids, grouped=False, states=None, date_invoice = False, context=None):
        order_group={}
        for i in self.browse(cr,uid,ids,context=context):
            order_group.setdefault((i.partner_invoice_id.id or i.partner_id.id,i.research_group),[]).append(i.id)
        for id in order_group.values():
            res = super(vnsoft_sale,self).action_invoice_create(cr,uid,id,grouped,states,date_invoice,context)
            for o in self.browse(cr,uid,id,context):
                inv_ids=[v.id for v in o.invoice_ids]
                self.pool.get("account.invoice").write(cr,uid,inv_ids,{"research_group":o.research_group},context)
        return res