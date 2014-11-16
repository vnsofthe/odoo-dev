# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import datetime


class rhwl_sample_info(osv.osv):
    _name = "sale.sampleone"
    _description = "样品信息表"
    # _inherit = "sale.order"

    SELECTION_TYPE = [
        (u'全血', u'全血'),
        (u'血浆', u'血浆'),
        (u'其它', u'其它')
    ]
    _columns = {
        "name": fields.char(u"样品编号", required=True, size=20),
        "sampletype": fields.selection(SELECTION_TYPE, u"样品类型", required=True),
        "cx_date": fields.date(u'采血时间', required=True),
        "cx_time": fields.selection([(7,u'7点'),(8,u'8点'),(9,u'9点'),(10,u'10点'),(11,u'11点'),(12,u'12点'),(13,u'13点'),(14,u'14点'),(15,u'15点'),(16,u'16点'),(17,u'17点'),(18,u'18点'),(19,u'19点'),(20,u'20点')],u'时间', required=True),
        "receiv_user": fields.many2one('res.users', string=u'收样人员'),
        "state_id": fields.many2one('res.country.state', string=u'样品区域（省）'),
        "city": fields.char(u"样品区域（市)"),
        "lyyy": fields.many2one('res.partner', string=u'来源医院',
                                domain="[('is_company', '=', True), ('customer', '=', True)]"),
        "cxyy": fields.many2one('res.partner', string=u'采血医院',
                                domain="[('is_company', '=', True), ('customer', '=', True)]", required=True),
        "lyys": fields.many2one('res.partner', string=u'来源医生',
                                domain="[('is_company', '=', False), ('customer', '=', True),('parent_id','=',lyyy)]"),
        "cxys": fields.many2one('res.partner', string=u'采血医生',
                                domain="[('is_company', '=', False), ('customer', '=', True),('parent_id','=',cxyy)]",
                                required=True),
        "fzr": fields.many2one('res.users', string=u'负责人'),
        # "state": fields.selection([('draf','draf')], u'状态'),
        "is_reused": fields.selection([('0', u'首次'), ('1', u'重采血')], u'是否重采血', required=True),
        "reuse_name": fields.many2one("sale.sampleone", u"重采血编号"),
        "reuse_type": fields.selection(SELECTION_TYPE, u"重采血类型"),
        "is_free": fields.selection([(u'是', u'是'), (u'否', u'否')], u'是否免费', required=True),
        "yfxm": fields.char(u"孕妇姓名", size=20, required=True),
        "yfyzweek": fields.integer(u"孕周_周"),
        "yfyzday": fields.integer(u"孕周_天"),
        "yfzjmc": fields.selection(
            [(u"身份证", u"身份证"), (u"护照", u"护照"), (u'军官证', u'军官证'), (u'士兵证', u'士兵证'), (u'工作证', u'工作证')], u"证件类型"),
        "yfzjmcother": fields.char(u"名称", size=10),
        "yfzjmc_no": fields.char(u"证件号码", size=30),
        "yfage": fields.integer(u"孕妇年龄(周岁)"),
        "yffqage": fields.integer(u"胎儿父亲年龄(周岁)"),
        "yflastyj": fields.date(u"末次月经"),
        "yfyjzq": fields.integer(u"月经周期"),
        "yftelno": fields.char(u"手机号", size=15),
        "yfjjlltel": fields.char(u"紧急联络电话", size=20),
        "yfpostaddr": fields.char(u"邮寄地址", size=50),
        "yfpostno": fields.char(u"邮编", size=6),
        "yfheight": fields.integer(u"身高(cm)"),
        "yfweight": fields.float(u"体重(kg)"),
        "yfycount": fields.integer(u'孕次数'),
        "yfzcount": fields.integer(u'产次数'),
        "yfblycs": fields.selection([('0', u'无'), ('1', u'有')], u'不良孕产史',required=True),
        "yfblycstext": fields.char(u"不良孕产史说明", size=20),
        "yfjzycb": fields.selection([('0', u'无'), ('1', u'有')], u'家族遗传病',required=True),
        "yfjzycbtext": fields.char(u"家族遗传病说明", size=20),
        "yffqsfrsthx": fields.selection([('0', u'无'), ('1', u'有')], u'夫妻双方染色体核型',required=True),
        "yffqsfrsthxtext": fields.char(u"夫妻双方染色体核型说明", size=20),
        "yfyczk": fields.selection([(u'单胎', u'单胎'), (u'双胎', u'双胎'), (u'其它', u'其它')], u"孕娠状况"),
        "yfyczktext": fields.char(u'孕娠说明', size=20),
        "yfissgyr": fields.selection([(u'否', u'否'), (u'是', u'是')], u'试管婴儿'),
        "yfcsjc": fields.selection([(u'未见异常', u'未见异常'), (u'提示异常', u'提示异常')], u"超声检查"),
        "yfcsjctext": fields.char(u'异常原因', size=20),
        "yfxqsc": fields.selection([(u'未做', u'未做'), (u'已做', u'已做')], u'血清筛查'),
        "yfxqsctext": fields.char(u'风险提示', size=20),
        "yfyyjrxccss": fields.selection([(u'无', u'无'), (u'已预约', u'已预约')], u'预约介入性穿刺手术'),
        "yfyyjrxccssdate": fields.date(u'预约日期'),
        "yfxbzl": fields.selection([(u'否', u'否'), (u'是', u'是')], u'细胞治疗'),
        "yfxbzltext": fields.char(u'细胞治疗说明', size=20),
        "yfzlfz": fields.selection([(u'否', u'否'), (u'是', u'是')], u'肿瘤患者'),
        "yfzlfztext": fields.char(u'肿瘤患者说明', size=20),
        "yfynnytsx": fields.selection([(u'否', u'否'), (u'是', u'是')], u'一年内异体输血'),
        "yfynnytsxtext": fields.char(u'一年内异体输血说明', size=20),
        "yftsqkbz": fields.char(u'特殊情况备注', size=100),
        "note": fields.text(u'备注'),
        "state": fields.selection([('draft', u'草稿'), ('done', u'完成'), ('cancel', u'取消')], u'状态'),
        "check_state": fields.selection(
            [(u'已接收', u'已接收'), (u'已进实验室', u'已进实验室'), (u'已上机', u'已上机'), (u'需重采血', u'需重采血'), (u'检验结果正常', u'检验结果正常'),
             (u'检验结果阳性', u'检验结果阳性')], u'检验状态'),
    }
    _defaults = {
        "state": lambda obj, cr, uid, context: "draft",
        "sampletype": lambda obj, cr, uid, context: u"全血",
        "receiv_user": lambda obj, cr, uid, context: uid,
        "is_free": lambda obj, cr, uid, context: u"否",
        "fzr": lambda obj, cr, uid, context: uid,
        "yfzjmc": lambda obj, cr, uid, context: u"身份证",
        "check_state": lambda obj, cr, uid, context: u'已接收',
        "yfblycs": lambda obj,cr,uid,context:"0",
        "yffqsfrsthx": lambda obj,cr,uid,context:"0",
        "yfjzycb": lambda obj,cr,uid,context:"0",
    }
    _sql_constraints = [
        ('sample_number_uniq', 'unique(name)', u'样品编号不能重复!'),
    ]
    def _check_zjno(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context=context)
        if obj.yfzjmc == u'身份证':
            if obj.yfzjmc_no and obj.yfzjmc_no.__len__()<>15 and obj.yfzjmc_no.__len__()<>18:
                return False
        return True

    _constraints = [
        (_check_zjno, 'ID Error.', ['yfzjmc_no']),
    ]

    def onchange_reused(self, cr, uid, ids, name, arg, context=None):
        if name and name == '1':
            return {
                "value": {
                    "reuse_type": arg,
                    "is_free":u"是",
                }
            }
    def onchange_lyyy(self, cr, uid, ids,context=None):
         return {
                "value": {
                    "lyys":False,
                }
            }
    def onchange_cxyy(self, cr, uid, ids,context=None):
         return {
                "value": {
                    "cxys":None,
                }
            }
    def onchange_ys(self, cr, uid, ids, lyyy,cxyy,val,name, context=None):
        if lyyy and cxyy and lyyy==cxyy:
            return {
                "value": {
                    name: val,
                }
            }
    def onchange_zjmcno(self, cr, uid, ids, tno,name, context=None):
        if tno and name and name == u'身份证':

            if tno and tno.__len__()<>15 and tno.__len__()<>18:
                 raise osv.except_osv(_('Error'), u"身份证号码不正确。")
            if tno.__len__()==15:
                str = tno[6:12]
            else:
                str = tno[6:14]

            return {
                "value": {
                    "yfage": (datetime.datetime.today() - datetime.datetime.strptime(str,"%Y%m%d")).days/365+1,
                }
            }

    def onchange_check_sample(self, cr, uid, ids, name, context=None):
        detail = self.pool.get("stock.picking.express").search(cr, uid, [("detail_ids.number_seq", "=", name)],
                                                               context=context)
        if not detail:
            return {}
        express = self.pool.get("stock.picking.express").browse(cr, uid, detail, context=context)
        if not express:
            return {}
        vals = {}
        id = self.pool.get("res.partner").search(cr, uid, [("zydb", "=", express.deliver_user.id)],
                                                 context=context)  # 检查用户是否为某客户的驻院代表
        partner = self.pool.get("res.partner").browse(cr, uid, id, context=context)
        if id:
            vals["lyyy"] = id
            vals["cxyy"] = id
            vals["state_id"] = partner.state_id
            vals["city"] = partner.city
        else:
            user = self.pool.get('res.users').browse(cr, uid, express.deliver_user.id, context=context)
            if user.partner_id:
                if user.partner_id.parent_id:
                    vals["lyyy"] = user.partner_id.parent_id.id
                    vals["cxyy"] = user.partner_id.parent_id.id
                    vals["state_id"] = user.partner_id.parent_id.state_id
                    vals["city"] = user.partner_id.parent_id.city

        return {
            "value": vals
        }

    def action_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'cancel'}, context=context)

    def action_done(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'done'}, context=context)
        cxys = self.browse(cr, uid, ids, context=context)

        warehouse = self.pool.get("stock.warehouse")
        w_id = warehouse.search(cr, uid, [("partner_id", "=", cxys.cxyy.id)], context=context)
        if isinstance(w_id, (list, tuple)):
            w_id = w_id[0]
        vals = {
            "partner_id": cxys.cxys.id,
            "client_order_ref": cxys.name,
            "warehouse_id": w_id,
            "pricelist_id": 1,
            "date_order": cxys.cx_date,
        }
        order_id = self.pool.get("sale.order").create(cr, uid, vals, context=context)

        partner = self.pool.get("res.partner").browse(cr, uid, cxys.cxyy.id, context=context)
        express = self.pool.get("stock.picking.express").search(cr, uid, [("detail_ids.number_seq", "=", cxys.name)],
                                                                context=context)
        express = self.pool.get("stock.picking.express").browse(cr, uid, express, context=context)
        if isinstance(express, (list, tuple)):
            express = express[0]
        orderline = self.pool.get("sale.order.line")
        orderline_id = orderline.create(cr, uid, {"order_id": order_id, "product_id": express.product_id.id,
                                                  "price_unit": partner.amt, "product_uom_qty": 1}, context=context)
        self.pool.get("sale.order").write(cr, uid, order_id, {'order_line': [(6, 0, [orderline_id])]})
        self.pool.get("sale.order").action_button_confirm(cr, uid, order_id)


class rhwl_reuse(osv.osv):
    _name = "sale.sampleone.reuse"
    _description = "样本信息重采血"

    _columns = {
        "name": fields.many2one("sale.sampleone", u"样本单号"),
        "yfxm": fields.related('name', 'yfxm', type='char', string=u'孕妇姓名', readonly=1),
        "notice_user": fields.many2one("res.users", u"通知人员"),
        "notice_date": fields.date(u"通知日期"),
        "reuse_note": fields.char(u"重采原因", size=200),
        "note": fields.text(u"孕妇说明及备注"),
        "state": fields.selection(
            [(u"未通知", u"未通知"), (u"已通知", u"已通知"), (u"重复通知", u"重复通知"), (u"孕妇放弃", u"孕妇放弃"), (u"已重采血", u"已重采血")], u"状态"),
    }


class rhwl_exception(osv.osv):
    _name = "sale.sampleone.exception"
    _description = "样本阳性跟踪"

    _columns = {
        "name": fields.many2one("sale.sampleone", u"样本单号"),
        "lib_notice": fields.char(u"无创结论", size=100),
        "cs_notice": fields.char(u"客服备注", size=100),
        "notice_user": fields.many2one("res.users", u"通知人员"),
        "notice_date": fields.date(u"通知日期"),
        "fz_user": fields.many2one("res.users", u"阳性跟踪负责人"),
        "is_notice": fields.boolean(u"是否已通知"),
        "is_take": fields.boolean(u"是否取走检测报告"),
        "is_next": fields.boolean(u"是否行进一步诊断"),
        "next_date": fields.date(u"诊断时间"),
        "next_hospital": fields.char(u"诊断医院", size=20),
        "next_result": fields.char(u"诊断结果", size=100),
        "is_equal": fields.boolean(u"是否与无创结果一致"),
        "state": fields.selection(
            [(u"未通知", u"未通知"), (u"已通知", u"已通知"), (u"重复通知", u"重复通知"), (u"已取报告", u"已取报告"), (u"已进一步诊断", u"已进一步诊断"),
             (u"完成", u"完成")], u"状态"),
    }