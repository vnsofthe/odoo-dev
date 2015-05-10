# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2014 OpenERP s.a. (<http://openerp.com>).
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
import itertools
import logging
from functools import partial
from itertools import repeat

from lxml import etree
from lxml.builder import E

import openerp
from openerp import SUPERUSER_ID, models
from openerp import tools
import openerp.exceptions
from openerp.osv import fields, osv, expression

class vnsoft04(osv.osv):
    _inherit = "sale.order"

    def _get_pay_state(self,cr,uid,ids,fields_name,arg,context=None):
        pass

    def _get_picking_state(self,cr,uid,ids,fields_name,arg,context=None):
        pass

    _columns={
        'pay_status': fields.function(_get_pay_state, type='selection',
            selection=[('0',u'未收款'),('1',u'已收款'),('2',u'收款未完结'),('3',u'已退款'),('4',u'部分退款')],
            string=u'收款状况', required=True, store=True),
        'deliver_status': fields.function(_get_picking_state, type='selection',
            selection=[('0',u'未发货'),('1',u'已发货'),('2',u'部分退货'),('3',u'已退货'),('4',u'发货未完结')],
            string=u'发货状况', required=True, store=True),

    }