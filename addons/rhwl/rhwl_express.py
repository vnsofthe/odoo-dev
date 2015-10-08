# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
import datetime
import re
import rhwl_sf
from lxml import etree
class rhwl_express(osv.osv):
    _inherit = "stock.picking.express"
    _rec_name = "num_express"
    _order = "id desc"
    def _get_check_user(self, cr, uid, context=None):
        """判断用户是内部人员还是外部人员。"""
        if context is None:
            context = {}
        id = self.pool.get("res.partner").search(cr, SUPERUSER_ID, [("zydb", "=", uid)],
                                                 context=context)  # 检查用户是否为某客户的驻院代表
        if id:
            return [False, id]  # 某用户是驻院代表，则直接判断为外部人员
        else:
            user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, uid, context=context)
            if not user.partner_id:
                return [False, None]
            id = user.partner_id.parent_id.id and user.partner_id.parent_id.id or user.partner_id.id

            return [id == 1, id]


    def _get_partner_address(self, cr, uid, ids, context=None):
        """得取用户对应业务伙伴的联系地址。"""
        if context is None:
            context = {}
        user = self._get_check_user(cr, ids, context=context)
        id = user[-1]
        if id:
            if isinstance(id, (list, tuple)):
                id = id[0]
            res = self.pool.get("res.partner").get_detail_address(cr,uid,id,context)
        else:
            res = ""

        return (id,res)

    def _get_addr(self, cr, uid, context=None):
        """新增时，带出作业人员对应的联系地址。"""
        return self._get_partner_address(cr, uid, uid, context)[1]

    def get_address(self, cr, uid, ids, user, colname, context=None):
        """人员栏位修改时，带出对应的联系地址。"""
        res = self._get_partner_address(cr, uid, user, context)
        val = {
            "value":{
                 colname: res[1]
            }
        }
        if colname=='deliver_addr':
            val['value']['deliver_partner']=res[0]
        elif colname=="receiv_addr":
            val['value']['receiv_partner']=res[0]
            u = self.pool.get("res.users").browse(cr,uid,user,context=context)
            val['value']['receiv_user_text']=u.name
            val['value']['mobile']=u.mobile
        return val

    def get_num_express(self, cr, uid, ids, deliver, context=None):
        partner = self.pool.get("res.partner").browse(cr, uid, deliver, context=context)
        if partner.comment:
            listno = re.split('[^0-9]', partner.comment)
            lastnum = listno[-1]
            newnum = str(long(lastnum) + 1).zfill(lastnum.__len__())
            self.pool.get("res.partner").write(cr, uid, deliver,
                                               {"comment": partner.comment[0:-newnum.__len__()] + newnum},
                                               context=context)
        return {
            "value": {
                "num_express": partner.comment
            }
        }

    def _get_first_deliver(self, cr, uid, context=None):
        deliver = self.pool.get("res.partner").search(cr, uid, [("is_deliver", "=", True)], context=context)
        if isinstance(deliver, (long, int)):
            return deliver
        if isinstance(deliver, (list, tuple)):
            return deliver[0]
        return False

    def _get_product_id(self, cr, uid, context=None):
        product_id = self.pool.get("product.product").search(cr, uid, [('sale_ok', '=', True), ("active", "=", True),("default_code","=","P001")],
                                                             context=context)
        if isinstance(product_id, (list, tuple)):
            product_id = product_id[0]
        return product_id

    def _fun_get_weight(self,cr,uid,ids,prop,arg,context=None):
        if isinstance(ids, (list, tuple)) and not len(ids):
            return {}
        if isinstance(ids, (long, int)):
            ids = [ids]
        res=[]
        for i in self.browse(cr,uid,ids,context=context):
            res.append((i.id,round(i.product_qty * i.product_id.weight,2)))
        return dict(res)

    def _fun_get_deliver_addr(self,cr,uid,ids,prop,arg,context=None):
        if isinstance(ids, (list, tuple)) and not len(ids):
            return {}
        if isinstance(ids, (long, int)):
            ids = [ids]
        res=[]
        for i in self.browse(cr,uid,ids,context=context):
            if prop=="deliver_addr1":
                res.append((i.id,i.deliver_addr[:25]))
            else:
                res.append((i.id,i.deliver_addr[25:]))
        return dict(res)
    def _fun_get_receiv_addr(self,cr,uid,ids,prop,arg,context=None):
        if isinstance(ids, (list, tuple)) and not len(ids):
            return {}
        if isinstance(ids, (long, int)):
            ids = [ids]
        res=[]
        for i in self.browse(cr,uid,ids,context=context):
            if prop=="receiv_addr1":
                res.append((i.id,i.receiv_addr[:25]))
            else:
                res.append((i.id,i.receiv_addr[25:]))
        return dict(res)

    def _fun_is_company(self, cr, uid, ids, prop, arg, context=None):
        if isinstance(ids, (list, tuple)) and not len(ids):
            return {}
        if isinstance(ids, (long, int)):
            ids = [ids]
        # if SUPERUSER_ID == uid:
        # return dict([(id, True) for id in ids])
        user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, uid, context=context)
        if not user.partner_id:
            return dict([(id, False) for id in ids])
        if user.partner_id.is_company:
            curr_company = user.partner_id.id
        else:
            if not user.partner_id.parent_id:
                return dict([(id, False) for id in ids])
            curr_company = user.partner_id.parent_id.id

        res = self.browse(cr, SUPERUSER_ID, ids, context=context)
        if not res:
            return {}
        result = []
        for k in res:
            if prop == "is_deliver":
                userid = k.deliver_user
            elif prop == "is_receiv":
                userid = k.receiv_user
            else:
                userid = None

            if not userid:
                result.append((k.id, False))
            else:
                if not userid.partner_id:
                    result.append((k.id, False))
                if userid.partner_id.is_company:
                    result.append((k.id, userid.partner_id.id == curr_company))
                else:
                    if not userid.partner_id.parent_id:
                        result.append((k.id, False))
                    else:
                        result.append((k.id, userid.partner_id.parent_id.id == curr_company))
        return dict(result)

    def get_express_list(self, cr, uid, ids, context=None):
        obj = self.browse(cr,uid,ids,context=context)
        return {
            'type': 'ir.actions.client',
            'tag': 'get_sf_express_list',
            'target': 'new',
            'params':{'num_express':obj.num_express},
        }

    _columns = {
        "deliver_user": fields.many2one('res.users', string=u'发货人员'),
        "deliver_addr": fields.char(size=120, string=u"发货地址",required=True),
        "deliver_partner":fields.many2one("res.partner",string=u"发货医院",domain=[('is_company','=',True),('customer','=',True)]),
        "receiv_user": fields.many2one('res.users', string=u'收货人员'),
        "receiv_date": fields.datetime('Date Receiv', required=True),
        "receiv_addr": fields.char(size=120, string=u"收货地址",required=True),
        "receiv_partner":fields.many2one("res.partner",string=u"收货医院",domain=[('is_company','=',True),('customer','=',True)]),
        "product_id": fields.many2one('product.product', 'Product',
                                      domain=[('sale_ok', '=', True), ("active", "=", True)], required=True,
                                      change_default=True),
        "product_qty": fields.float(u'发货数量', digits_compute=dp.get_precision('Product Unit of Measure'),
                                    required=True),
        "receiv_real_user": fields.many2one('res.users', string=u'实际收货人员'),
        "receiv_real_date": fields.datetime('Realy Date Receiv'),
        "receiv_real_qty": fields.float(u'实际收货数量', digits_compute=dp.get_precision('Product Unit of Measure'),
                                        required=True),
        "is_deliver": fields.function(_fun_is_company, type="boolean", string=u"发货方"),
        "is_receiv": fields.function(_fun_is_company, type="boolean", string=u"收货方"),
        "detail_ids": fields.one2many("stock.picking.express.detail", "parent_id",readonly=True,states={'draft':[('readonly',False)]},string=u"收货明细"),
        "destcode":fields.char("destcode"),
        "origincode": fields.char("origincode"),
        "weight":fields.function(_fun_get_weight,type="float",string="Weight"),
        "deliver_addr1":fields.function(_fun_get_deliver_addr,type="char",string="deliver_addr1"),
        "deliver_addr2":fields.function(_fun_get_deliver_addr,type="char",string="deliver_addr2"),
        "receiv_addr1":fields.function(_fun_get_receiv_addr,type="char",string="receiv_addr1"),
        "receiv_addr2":fields.function(_fun_get_receiv_addr,type="char",string="receiv_addr2"),
        "express_type":fields.selection([("1",u"标准快递"),("11",u"医药常温"),("12",u"医药温控")],string=u"快递类型",required=True),
        "mobile": fields.char(u"手机号码", size=20),
        "receive_type":fields.selection([("internal",u"内部人员"),("external",u"外部人员")],string=u"收件方类型"),
        "receiv_user_text":fields.char(u"收货人员",size=20),
        "state_id": fields.many2one("res.country.state",string=u'省'),
        "city_id": fields.many2one("res.country.state.city",string=u'市',domain="[('state_id','=',state_id)]"),
        "area_id":fields.many2one("res.country.state.city.area",string=u"区/县",domain="[('city_id','=',city_id)]"),
    }

    _defaults = {
        'date': fields.datetime.now,
        'deliver_user': lambda obj, cr, uid, context: uid,
        "receiv_date": lambda obj, cr, uid, context: datetime.timedelta(3) + datetime.datetime.now(),
        "deliver_addr": _get_addr,
        "deliver_id": _get_first_deliver,
        "product_id": _get_product_id,
        "num_express": lambda obj,cr, uid,context: "0000000000",
        "express_type":lambda obj,cr,uid,context:"11",
        "receive_type":"internal"
    }

    def create(self, cr, uid, vals, context=None):
        if vals.has_key('product_qty') and vals.has_key('detail_ids') and vals['product_qty']==0 and vals['detail_ids'].__len__()>0:
            vals['product_qty'] =  vals['detail_ids'].__len__()
        return super(rhwl_express,self).create(cr,uid,vals,context=context)

    def action_send(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'progress'}, context=context)
        rec = self.browse(cr, uid, ids, context=context)
        for i in rec.detail_ids:
            i.write({"out_flag": True})
        move_obj = self.pool.get("stock.move")
        if isinstance(ids,(long,int)):
            ids = [ids,]
        move_ids = move_obj.search(cr,SUPERUSER_ID,[('move_dest_id.id','>',0),('state','not in',['done','cancel']),('express_no','in',ids)],context=context)
        if move_ids:move_obj.action_done(cr, SUPERUSER_ID, move_ids, context=None)

    def action_ok(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'done'}, context=context)
        rec = self.browse(cr, uid, ids, context=context)
        for i in rec.detail_ids:
            i.write({"in_flag": True})
        move_obj = self.pool.get("stock.move")
        if isinstance(ids,(long,int)):
            ids = [ids,]
        move_ids = move_obj.search(cr,SUPERUSER_ID,[('move_dest_id','=',False),('state','not in',['done','cancel']),('express_no','in',ids)],context=context)
        if move_ids:move_obj.action_done(cr, SUPERUSER_ID, move_ids, context=None)

    def action_sf(self,cr,uid,ids,context=None):
        rec = self.browse(cr,uid,ids,context=context)
        vals=[]
        devals=[]
        for i in rec:
            vals.append(i.express_type)
            if i.receive_type=="internal":
                vals.append(i.receiv_partner.name)
                vals.append(i.receiv_user.name)
                vals.append(i.receiv_partner.phone)
                vals.append(i.receiv_user.partner_id.mobile)
                vals.append(i.receiv_partner.state_id.name)
                vals.append(i.receiv_partner.city_id.name)
                vals.append(i.receiv_partner.area_id.name)
            else:
                vals.append(i.receiv_user_text)
                vals.append(i.receiv_user_text)
                vals.append(i.mobile)
                vals.append(i.mobile)
                vals.append(i.state_id.name)
                vals.append(i.city_id.name)
                vals.append(i.area_id.name)

            vals.append(i.receiv_addr)
            vals.append(i.weight)
            vals.append(str(i.id).zfill(12))
            vals.append(i.product_id.name)
            vals.append(str(i.product_qty))

            devals.append(i.deliver_partner.name)
            devals.append(i.deliver_user.name)
            devals.append(i.deliver_partner.phone)
            devals.append(i.deliver_user.partner_id.mobile)
            devals.append(i.deliver_partner.state_id.name)
            devals.append(i.deliver_partner.city_id.name)
            devals.append(i.deliver_partner.area_id.name)
            devals.append(i.deliver_addr)

            xmlstr= rhwl_sf.get_e_express(vals,devals)
            xml = etree.fromstring(xmlstr.encode('utf-8'))#进行XML解析
            if xml.find("Head").text=="ERR":
                raise osv.except_osv("生成电子运单出错：",xml.find("ERROR").text)
            elif xml.find("Head").text=="OK":
                body = xml.find("Body").getchildren()[0]
                self.write(cr,uid,ids,{"num_express":body.get("mailno"),"destcode":body.get("destcode"),"origincode":body.get("origincode")},context=context)


    def action_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'cancel'}, context=context)

class rhwl_express_in(osv.osv):
    _name = "stock.picking.express.detail"
    _columns = {
        'parent_id': fields.many2one("stock.picking.express", string="物流单号"),
        'number_seq': fields.char(u"样品编号", size=20),
        'number_seq_ori': fields.char(u"原样品编号", size=20),
        "in_flag": fields.boolean(u"收货"),
        "out_flag": fields.boolean(u'发货'),
        "invoice":fields.boolean(u"是否开票"),
    }

    def confirm_receive(self,cr,uid,no,context=None):
        id = self.search(cr,uid,[("number_seq","=",no)],context=context)
        if id:
            self.write(cr,uid,{"in_flag":True},context=context)

class sale_express(osv.osv):
    _name = 'rhwl.sampleone.express'
    _order = "id desc"
    def _get_url_express(self, cursor, user, ids, name, arg, context=None):
        res = {}
        default_url = "http://www.kuaidi100.com/chaxun?com=shunfeng&nu=%s"
        for express in self.browse(cursor, user, ids, context=context):
            res[express.id] = default_url % (express.name,)
        return res

    _columns={
        "name":fields.char(u"快递单号",size=20,required=True),
        "date":fields.date(u"发件日期",required=True),
        "user_id":fields.many2one("res.users",string=u"发件人"),
        'url_express': fields.function(
            _get_url_express, method=True, type='char',
            string='Link', readonly=1),
        "note":fields.text(u"备注"),
        "line":fields.one2many("rhwl.sampleone.express.line","name",string=u"样本明细"),
    }

class sale_express_line(osv.osv):
    _name = "rhwl.sampleone.express.line"
    _rec_name = "sample_id"
    _columns={
        "name":fields.many2one("rhwl.sampleone.express",string=u"快递单号"),
        "sample_id":fields.many2one("sale.sampleone",string=u"样本编号"),
        "yfxm":fields.related("sample_id","yfxm",type="char",string=u"孕妇姓名",readonly=True)
    }