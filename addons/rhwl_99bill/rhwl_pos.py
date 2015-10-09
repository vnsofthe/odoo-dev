# -*- coding: utf-8 -*-

from openerp.osv import fields, osv

class rhwl_pos(osv.osv):
    _name = "rhwl.base.pos"
    _columns={
        "provide":fields.selection([('KQ',u"快钱")],string=u"机器提供商",required=True),
        "terminal_id":fields.char(u"终端编号",size=20,required=True),
        "date":fields.date(u"采购日期",required=True),
        "manage":fields.many2one("res.users",string=u"财产管理员",required=True),
        "user_id":fields.many2one("res.users",string=u"领用人员"),
        "date_out":fields.date(u"领用日期"),
        "partner":fields.many2one("res.partner",string=u"使用客户"),
        "note":fields.text(u"备注"),
        "company":fields.selection([("rhwl",u"人和未来"),("xy",u"湘雅")],string=u"收款机构")
    }
    _defaults={
        "provide":"KQ",
        "date":fields.date.today,
        "manage":lambda obj,cr,uid,context:uid,
    }

    _sql_constraints = [
        ('terminal_uniq', 'unique(provide,terminal_id)', u'相同提供商下，终端号不能重复!'),
    ]