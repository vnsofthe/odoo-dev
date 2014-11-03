# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2013 Elico Corp. All Rights Reserved.
#    Author: LIN Yu <lin.yu@elico-corp.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.addons.base_status.base_state import base_state as bs
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import ustr


class res_partner(osv.Model):
    _inherit = 'res.partner'
    _columns = {
        'is_deliver':  fields.boolean(u'物流公司'),
    }
    _defaults = {
        'is_deliver': False,
    }


class stock_picking_express(bs, osv.Model):
    _name = "stock.picking.express"
    # _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Stock Picking Express"
    _order = 'date,deliver_id'

    def _get_url_express(self, cursor, user, ids, name, arg, context=None):
        res = {}
        default_url = "http://www.kuaidi100.com/chaxun?com=%s&nu=%s"
        for express in self.browse(cursor, user, ids, context=context):
            res[express.id] = default_url % (express.deliver_id.ref,
                                             express.num_express)
        return res

    _columns = {
        'deliver_id': fields.many2one(
            'res.partner', 'Deliver Company',
            domain=[('is_deliver', '=', 1)],required=True),
        'state': fields.selection(
            [('draft', 'Draft Quotation'),
             ('cancel', 'Cancelled'),
             ('progress', 'Progress'),
             ('manual', 'Sale to Invoice'),
             ('done', 'Done')],
            'Status',required=True, readonly=True, copy=False),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'num_express':  fields.char('No. Express',required=True),
        'url_express': fields.function(
            _get_url_express, method=True, type='char',
            string='Link', readonly=1),
        'date': fields.datetime('Date Deliver',required=True),
    }

    _defaults = {
        'state': 'draft',
        }

    def action_send(self,cr,uid,ids,context=None):
         self.write(cr, uid, ids, {'state': 'progress'}, context=context)

    def action_ok(self,cr,uid,ids,context=None):
        self._write(cr,uid,ids,{'state':'done'},context=context)

    def action_cancel(self,cr,uid,ids,context=None):
        self._write(cr,uid,ids,{'state':'cancel'},context=context)