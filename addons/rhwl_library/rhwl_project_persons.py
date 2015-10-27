# -*- coding: utf-8 -*-
from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp import tools, api
import datetime
import logging

_logger = logging.getLogger(__name__)

class rhwl_persons(osv.osv):
    _name = "rhwl.project.persons"

    def _check_date(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context=context)
        if obj.date.split("-")[-1]!='01':
            return False
        return True

    _columns={
        "date":fields.date("Cost Date",required=True),
        "user_id":fields.many2one("res.users",string="User",readonly=True),
        "state":fields.selection([("draft","Draft"),("done","Done")],string="State"),
        "line":fields.one2many("rhwl.project.persons.line","parent_id",string="Detail"),

    }
    _defaults={
        "user_id":lambda obj,cr,uid,context:uid,
        "state":"draft",
    }
    _sql_constraints = [
        ('rhwl_project_persons_uniq', 'unique(date)', u'成本日期不能重复!'),
    ]
    _constraints = [
        (_check_date, u'成本日期只能是每月的1号。', ['date']),
    ]

class rhwl_persons_line(osv.osv):
    _name = "rhwl.project.persons.line"
    _columns={
        "parent_id":fields.many2one("rhwl.project.persons",string="Parent"),
        "project_id":fields.many2one("res.company.project","Project",ondelete="restrict",required=True),
        "sample_count":fields.integer(u"当月样本数",required=True),
    }