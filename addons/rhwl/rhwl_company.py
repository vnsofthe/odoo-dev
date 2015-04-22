# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

import datetime
import re

class rhwl_company(osv.osv):
    _inherit = "res.company"

    _columns = {
        "project_id":fields.one2many("res.company.project","company_id","Project")
    }

class rhwl_project(osv.osv):
    _name = "res.company.project"

    _columns={
        "company_id":fields.many2one("res.company","Company"),
        "name":fields.char("Project Name"),
        "month_qty":fields.integer("Qty of Month")
    }


    def create(self,cr,uid,val,context=None):
        id = super(rhwl_project,self).create(cr,uid,val,context)
        self.pool.get("stock.warehouse.orderpoint").compute_all_orderpoint(cr,uid,context=context)
        return id

    def write(self, cr, uid, ids, vals, context=None):
        id= super(rhwl_project,self).write(cr,uid,ids,vals,context)
        self.pool.get("stock.warehouse.orderpoint").compute_all_orderpoint(cr,uid,context=context)
        return id

    def unlink(self, cr, uid, ids, context=None):
        id = super(rhwl_project,self).unlink(cr,uid,ids,context)
        self.pool.get("stock.warehouse.orderpoint").compute_all_orderpoint(cr,uid,context=context)
        return id