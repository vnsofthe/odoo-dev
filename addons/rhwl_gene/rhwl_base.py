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