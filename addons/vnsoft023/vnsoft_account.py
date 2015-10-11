# -*- coding: utf-8 -*-
from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp import tools, api
import datetime


class vnsoft_account(osv.osv):
    _inherit = "account.invoice"

    _columns={
        "page_inv_no":fields.char(u"纸质发票号"),
    }

class vnsoft_partner(osv.osv):
    _inherit = "res.partner"

    def create(self,cr,uid,vals,context=None):
        #if vals.get("is_company",False) and (not vals.get("bank_ids")):
        #    raise osv.except_osv("Error",u"请设置银行帐号信息。")
        return super(vnsoft_partner,self).create(cr,uid,vals,context)

    def write(self,cr,uid,ids,vals,context=None):


        #if is_company and (not bank_ids):
        #   raise osv.except_osv("Error",u"请设置银行帐号信息。")
        return super(vnsoft_partner,self).write(cr,uid,ids,vals,context)