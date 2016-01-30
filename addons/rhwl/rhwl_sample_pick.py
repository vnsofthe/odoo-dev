# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID,api
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import datetime,time
import logging

class rhwl_picking(osv.osv):
    _name = "rhwl.sample.picking"
    _columns = {
        "name":fields.char(u"发货单号",size=10,required=True),
        "batch_no":fields.char(u"批号",size=10,required=True),
        "date":fields.date(u"日期",required=True),
        "state":fields.selection([("draft",u"草稿"),("confirm",u"确认"),("done",u"完成")],string=u"状态",required=True),
        "user_id":fields.many2one("res.users",string=u"处理人员",required=True),
        "line":fields.one2many("rhwl.sample.picking.line","parent_id",string="Detail"),
        "express":fields.one2many("rhwl.sample.picking.express","parent_id",string="express")
    }
    _defaults={
        "user_id":lambda obj,cr,uid,context:uid,
        "state":"draft",
        "date":fields.date.today,
    }

    _sql_constraints = [
        ('rhwl_sample_picking_name_uniq', 'unique(name)', u'发货单号不能重复!'),
    ]

    @api.onchange("batch_no")
    def _change_batch_no(self):
        if self.batch_no:
            ids = self.env["sale.sampleone"].search([('batch_no','=',self.batch_no)])
            if not ids:
                self.batch_no=""

                return
            res=[]
            for i in ids:
                res.append({"name":i})
            self.line = res

    def action_send_sms(self,cr,uid,ids,context=None):
        obj = self.browse(cr,uid,ids,context=context)
        err_count = 0
        for i in obj.line:
            if i.name.check_state=="ok" and (not i.name.has_sms):
                try:
                    self.pool.get("sale.sampleone").action_sms(cr,uid,i.name.id,context=context)
                except:
                    err_count += 1
        cr.commit()
        if err_count>0:
            raise osv.except_osv("ERROR",u"有[%s]笔短信没有发送成功，请检查孕妇姓名是否有生僻字。"%(err_count))

    def action_state_confirm(self,cr,uid,ids,context=None):
        if self.pool.get("rhwl.sample.picking.line").search_count(cr,uid,[("parent_id","=",ids)])==0:
            raise osv.except_osv("ERROR",u"发货单未建立明细，不可以确认。")
        self.write(cr,uid,ids,{"state":"confirm"},context=context)

    def action_state_done(self,cr,uid,ids,context=None):
        self.write(cr,uid,ids,{"state":"done"},context=context)

    def action_create_express(self,cr,uid,id,context=None):
        if isinstance(id,(list,tuple)):
            id=id[0]
        #判断装箱明细中是否已经有产生快递单
        box_ids = self.pool.get("rhwl.sample.picking.express").search(cr,uid,[("parent_id","=",id),("express_id.id","!=",False)])
        if box_ids:
            raise osv.except_osv("Error",u"装箱明细中已经有产生对应的快递单，不可以重复产生。")
        box_ids = self.pool.get("rhwl.sample.picking.express").search(cr,uid,[("parent_id","=",id)])
        if box_ids:
            self.pool.get("rhwl.sample.picking.express").unlink(cr,uid,box_ids)

        genes_ids = self.pool.get("rhwl.sample.picking.line").search(cr,uid,[("parent_id.id","=",id)],context=context)
        if genes_ids:
            box_dict={}
            for g in self.pool.get("rhwl.sample.picking.line").browse(cr,uid,genes_ids,context=context):
                if g.name.single_post:
                    self.pool.get("rhwl.sample.picking.express").create(cr,uid,{"parent_id":id,
                                                                               "partner_text":g.name.yfxm,
                                                                               "address":g.name.yfpostaddr,
                                                                               "mobile":g.name.yftelno,
                                                                               "qty":1},context=context)
                else:
                    if box_dict.has_key(g.name.cxyy.id):
                        box_dict[g.name.cxyy.id]["qty"] +=1
                        box_dict[g.name.cxyy.id]["detail_no"].append(g.name.name)
                    else:
                        if g.name.cxyy.wc_report:
                            p_id = g.name.cxyy.wc_report.id
                        else:
                            p_id = g.name.cxyy.user_id.partner_id.id
                        if not p_id:
                            raise osv.except_osv("error",u"送检机构[%s]没有设置无创报告收件人，同时也没有对应的销售人员。"%(g.name.cxyy.name))

                        add_dict = self.pool.get("res.partner").get_detail_address_dict(cr,uid,p_id,context=context)
                        partner_obj = self.pool.get("res.partner").browse(cr,uid,p_id,context=context)
                        box_dict[g.name.cxyy.id]={
                            "parent_id":id,
                            "partner_id":g.name.cxyy.id,
                           "partner_text":partner_obj.name,
                           "qty":1,
                           "state_id":add_dict["state_id"],
                           "city_id":add_dict["city_id"],
                           "area_id":add_dict["area_id"],
                           "address":"".join([x for x in [add_dict["street"],add_dict["street2"]] if x]),
                           "mobile":partner_obj.mobile,
                            "detail_no":[g.name.name]
                        }
            if box_dict:
                for b in box_dict.values():
                    b["detail_no"] = ",".join(b["detail_no"])
                    self.pool.get("rhwl.sample.picking.express").create(cr,uid,b,context=context)

class rhwl_picking_line(osv.osv):
    _name = "rhwl.sample.picking.line"
    _columns={
        "name":fields.many2one("sale.sampleone",string=u"样本编号",ondelete="restrict"),
        "parent_id":fields.many2one("rhwl.sample.picking",string="Parent"),
        "yfxm": fields.related('name', 'yfxm', type='char', string=u'孕妇姓名', readonly=1),
        "cx_date": fields.related('name', 'cx_date', type='char', string=u'采血日期', readonly=1),
        "yfage": fields.related('name', 'yfage', type='integer', string=u'年龄(周岁)', readonly=1),
        "yfyzweek": fields.related('name', 'yfyzweek', type='integer', string=u'孕周', readonly=1),
        "yftelno": fields.related('name', 'yftelno', type='char', string=u'孕妇电话', readonly=1),
        "cxys": fields.related('name', 'cxys', relation="res.partner", type='many2one', string=u'采血医生', readonly=1),
        "cxyy": fields.related('name', 'cxyy', relation="res.partner", type='many2one', string=u'采血医院', readonly=1),
    }

class rhwl_picking_express(osv.osv):
    _name = "rhwl.sample.picking.express"
    _columns={
        "parent_id":fields.many2one("rhwl.sample.picking",u"发货单号",ondelete="restrict"),
        "partner_id":fields.many2one("res.partner",string=u"收件机构",),
        "partner_text":fields.char(u"收件人",size=100),
        "address":fields.char(u"详细地址",size=150),
        "mobile": fields.char(u"手机号码", size=20),
        "qty":fields.integer(u"数量"),
        "state_id": fields.many2one("res.country.state",string=u'省'),
        "city_id": fields.many2one("res.country.state.city",string=u'市',domain="[('state_id','=',state_id)]"),
        "area_id":fields.many2one("res.country.state.city.area",string=u"区/县",domain="[('city_id','=',city_id)]"),
        "express_id":fields.many2one("stock.picking.express",u"快递单"),
        "detail_no":fields.text("Detail No")
    }

    def action_create_express(self,cr,uid,id,context=None):
        obj = self.browse(cr,uid,id,context=context)
        product_id = self.pool.get("product.product").search(cr,uid,[("default_code","=","WCREPORT")])
        val={
            "expres_type":'1',
            "receive_type":"external",
            "receiv_user_text":obj.partner_text,
            "receiv_addr":"".join([x for x in [obj.state_id.name,obj.city_id.name,obj.area_id.name,obj.address] if x]),
            "mobile":obj.mobile,
            "product_id":product_id[0],
            "product_qty":obj.qty,
            "receiv_real_qty":obj.qty
        }
        express_id = self.pool.get("stock.picking.express").create(cr,uid,val,context=context)
        self.write(cr,uid,obj.id,{"express_id":express_id},context=context)
        if obj.detail_no:
            for d in obj.detail_no.split(","):
                self.pool.get("stock.picking.express.detail").create(cr,uid,{"parent_id":express_id,"number_seq":d},context=context)

    def action_open_express(self,cr,uid,id,context=None):
        obj = self.browse(cr,uid,id,context=context)

        mod_obj = self.pool.get('ir.model.data')
        dummy, action_id = tuple(mod_obj.get_object_reference(cr, uid, 'l10n_cn_express_track', 'action_stock_express'))
        action = self.pool.get('ir.actions.act_window').read(cr, uid, action_id, context=context)
        action['context'] = {}

        res = mod_obj.get_object_reference(cr, uid, 'rhwl', 'rhwl_stock_picking_express_form')
        action['views'] = [(res and res[1] or False, 'form')]
        action['res_id'] = obj.express_id.id and obj.express_id.id or False

        return action