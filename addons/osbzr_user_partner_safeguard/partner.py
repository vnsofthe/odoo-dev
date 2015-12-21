# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-Today 上海开阖软件有限公司 (<http://www.osbzr.com>).
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

from openerp.osv import osv
from openerp.tools.translate import _

class res_partner(osv.osv):
    _inherit = 'res.partner'
    def write(self, cr, uid, ids, vals, context=None):
        user = self.pool.get('res.users').browse(cr,uid,uid,context=context)
        for partner in self.browse(cr,uid,ids,context=context):
            if partner.user_ids and not user.has_group('base.group_erp_manager'):
                raise osv.except_osv(_('Error!'), _('You are not allowed to change other user\'s information!'))
        res = super(res_partner, self).write(cr, uid, ids, vals, context)
        return res
