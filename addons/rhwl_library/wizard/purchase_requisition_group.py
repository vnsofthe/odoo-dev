# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import time

from openerp.osv import fields, osv
from openerp.tools.translate import _

class purchase_requisition_group(osv.osv_memory):
    _name = "purchase.requisition.group"
    _description = "Purchase Requisition Merge"

    def merge_requisitions(self, cr, uid, ids, context=None):
        """
             To merge similar type of purchase orders.

             @param self: The object pointer.
             @param cr: A database cursor
             @param uid: ID of the user currently logged in
             @param ids: the ID or list of IDs
             @param context: A standard dictionary

             @return: purchase order view

        """
        obj = self.pool.get('purchase.requisition')

        if context is None:
            context = {}

        ids = context.get('active_ids',[])
        id = self.pool.get("purchase.requisition").create(cr,uid,{},context=context)

        pid = self.pool.get("procurement.order").search(cr,uid,[("requisition_id","in",ids)],context=context)
        self.pool.get("procurement.order").write(cr,uid,pid,{"requisition_id":id},context=context)

        for i in self.pool.get("purchase.requisition").browse(cr,uid,ids,context=context):
            val={}
            if i.line_ids:
                val["line_ids"]=[]
                for p in i.line_ids:
                    val["line_ids"].append([4,p.id])
            if i.purchase_ids:
                val["purchase_ids"]=[]
                for p in i.purchase_ids:
                    val["purchase_ids"].append([4,p.id])
            self.pool.get("purchase.requisition").write(cr,uid,id,val,context=context)
            i.signal_workflow('cancel_requisition')

        return {
            'domain': "[('id','in', [" + str(id) + "])]",
            'name': _('Purchase Requisition'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'purchase.requisition',
            'view_id': False,
            'type': 'ir.actions.act_window'
        }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
