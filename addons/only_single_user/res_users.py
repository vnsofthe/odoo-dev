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
from openerp.tools.translate import _
from openerp.http import request

_logger = logging.getLogger(__name__)

class res_users(osv.osv):
    _inherit="res.users"

    _columns={
        "session_id":fields.char("SessionID",size=50)
    }
