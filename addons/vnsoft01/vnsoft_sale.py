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