# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID, api
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import datetime,time
import logging
import os
import shutil
import re
from openerp import tools
from lxml import etree
from openerp.osv import osv, fields, expression
_logger = logging.getLogger(__name__)

class rhwl_base(osv.osv):
    _name="rhwl.genes.base.customer"

    _columns={
        "name":fields.char("Name",size=20,required=True),
        "code":fields.char("Code",size=10,required=True),
        "detail":fields.one2many("rhwl.genes.base.lang","parent_id",string="Detail")
    }

    _sql_constraints = [
        ('rhwl_genes_base_customer_code_uniq', 'unique(code)', u'代号不能重复!'),
    ]

    def name_get(self, cr, user, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        if not len(ids):
            return []
        res=[]
        for i in self.browse(cr,user,ids,context=context):
            res.append((i.id,i.name+"("+i.code+")"))
        return res

class rhwl_base_lang(osv.osv):
    _name="rhwl.genes.base.lang"
    _columns={
        "parent_id":fields.many2one("rhwl.genes.base.customer",string="Parent"),
        "name":fields.char("Name",size=20,required=True),
        "code":fields.char("Code",size=10,required=True),
        "detail":fields.one2many("rhwl.genes.base.set","parent_id",string="Detail")
    }
    _sql_constraints = [
        ('rhwl_genes_base_lang_code_uniq', 'unique(parent_id,code)', u'代号不能重复!'),
    ]

    def name_get(self, cr, user, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        if not len(ids):
            return []
        res=[]
        for i in self.browse(cr,user,ids,context=context):
            parent_name=i.parent_id.name+"("+i.parent_id.code+")"
            res.append((i.id,parent_name+" / "+i.name+"("+i.code+")"))
        return res

class rhwl_base_set(osv.osv):
    _name = "rhwl.genes.base.set"
    _columns={
        "parent_id":fields.many2one("rhwl.genes.base.lang",string="Parent",required=True),
        "name":fields.char("Name",size=20,required=True),
        "code":fields.char("Code",size=20,required=True),
        "detail":fields.one2many("rhwl.genes.base.package","parent_id",string="Detail")
    }
    _sql_constraints = [
        ('rhwl_genes_base_set_code_uniq', 'unique(parent_id,code)', u'代号不能重复!'),
    ]

class rhwl_base_package(osv.osv):
    _name = "rhwl.genes.base.package"
    _columns={
        "parent_id":fields.many2one("rhwl.genes.base.set",string="Parent"),
        "name":fields.char("Name",size=20,required=True),
        "code":fields.char("Code",size=50,required=True)
    }
    _sql_constraints = [
        ('rhwl_genes_base_package_code_uniq', 'unique(parent_id,code)', u'代号不能重复!'),
    ]

    def name_get(self, cr, user, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        if not len(ids):
            return []
        res=[]
        for i in self.browse(cr,user,ids,context=context):
            parent_name="%s(%s) / %s(%s) / %s(%s)" % (i.parent_id.parent_id.parent_id.name,i.parent_id.parent_id.parent_id.code,i.parent_id.parent_id.name,i.parent_id.parent_id.code,i.parent_id.name,i.parent_id.code,)
            res.append((i.id,parent_name+" / "+i.name+"("+i.code+")"))
        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if not context:
            context = {}
        if name:
            # Be sure name_search is symetric to name_get
            categories = name.split(' / ')
            parents = list(categories)
            child = parents.pop()
            domain = [('name', operator, child)]
            if parents:
                names_ids = self.name_search(cr, uid, ' / '.join(parents), args=args, operator='ilike', context=context, limit=limit)
                category_ids = [name_id[0] for name_id in names_ids]
                if operator in expression.NEGATIVE_TERM_OPERATORS:
                    category_ids = self.search(cr, uid, [('id', 'not in', category_ids)])
                    domain = expression.OR([[('parent_id', 'in', category_ids)], domain])
                else:
                    domain = expression.AND([[('parent_id', 'in', category_ids)], domain])
                for i in range(1, len(categories)):
                    domain = [[('name', operator, ' / '.join(categories[-1 - i:]))], domain]
                    if operator in expression.NEGATIVE_TERM_OPERATORS:
                        domain = expression.AND(domain)
                    else:
                        domain = expression.OR(domain)
            ids = self.search(cr, uid, expression.AND([domain, args]), limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context)