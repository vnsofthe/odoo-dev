# coding=utf-8

from openerp import SUPERUSER_ID,api
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
import datetime
import openerp
import logging

class web_material(osv.osv):
    _name = "rhwl.web.material"

    def _get_picking_state(self,cr,uid,ids,field_names,args,context=None):
        res={}
        for i in self.browse(cr,uid,ids,context=context):
            res[i.id] = ""
            picking_id = self.pool.get("stock.picking").search(cr,uid,[("origin","=",i.name),("state","!=","cancel")])
            if not picking_id:
                res[i.id] = u"无出库单"
            else:
                done_count = total_count = 0
                for p in self.pool.get("stock.picking").browse(cr,uid,picking_id,context=context):
                    if p.state=="done":
                        done_count += 1
                    total_count += 1
                if done_count==total_count:
                    res[i.id] = u"已出库"
                elif done_count>0:
                    res[i.id] = u"部分已出库"
                else:
                    res[i.id] = u"未出库"
        return res

    _columns={
        "name":fields.char(u"申请单号",size=10),
        "date":fields.date(u"申请日期"),
        "user_id":fields.many2one("res.users",string=u"申请人"),
        "hospital":fields.many2one("res.partner",string=u"申请医院(机构)",domain="[('is_company', '=', True), ('customer', '=', True),'|',('sjjysj','!=',False),'|',('yg_sjjysj','!=',False),'|',('ys_sjjysj','!=',False),('el_sjjysj','!=',False)]"),
        "wh_level":fields.selection([("hospital",u"医院级"),("proxy",u"代理级"),("person",u"销售员级")],string=u"库存归属"),
        "address_id":fields.many2one("res.partner",string="Address ID"),
        "receiver_user":fields.char(u"收件人",size=10),
        "receiver_address":fields.char(u"收件地址",size=100),
        "receiver_tel":fields.char(u"收件人电话",size=20),
        "state":fields.selection([("draft",u"草稿"),("confirm",u"确认"),("approve1",u"核准1"),("approve2",u"核准2"),("done",u"完成")],string=u"状态"),
        "line":fields.one2many("rhwl.web.material.line","parent_id",string="Line"),
        "express_partner":fields.selection([("sf",u"顺丰"),("sto",u"申通"),("yto",u"圆通"),("yunda",u"韵达")],u"快递公司"),
        "express_no":fields.char(u"快递单号",size=20),
        "note":fields.text(u"备注"),
        "approve1_user":fields.many2one("res.users",string=u"核准人1"),
        "approve2_user":fields.many2one("res.users",string=u"核准人2"),
        "approve1_date":fields.datetime(u"核准时间"),
        "approve2_date":fields.datetime(u"核准时间"),
        "done_date":fields.datetime(u"完成时间"),
        "picking_state":fields.function(_get_picking_state,type="char",string=u"出库单状态"),
    }
    _defaults={
        "date":fields.date.today,
        "user_id":lambda obj,cr,uid,context:uid,
        "state":"draft",
        "wh_level":"person"
    }

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if vals.get('name', '/') == '/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'rhwl.web.material') or '/'
        id = super(web_material,self).create(cr,uid,vals,context)
        obj = self.browse(cr,uid,id,context=context)
        if obj.state=="confirm":
            send_text = "申请单[%s]已确认，请及时审核。" %(obj.name.encode("utf-8"),)
            self.pool.get("rhwl.weixin.base").send_qy_text(cr,SUPERUSER_ID,"rhwlyy","is_material_approve",send_text,context=context)
        return id

    def write(self,cr,uid,ids,vals,context=None):
        res = super(web_material,self).write(cr,uid,ids,vals,context=context)
        if vals.get("state") in ("confirm","approve1","approve2","done"):
            if isinstance(ids,(int,long)):
                ids = [ids]
            for i in self.browse(cr,uid,ids,context=context):
                if(i.state=="confirm"):
                    send_text = "申请单[%s]已确认，请及时审核。" %(i.name.encode("utf-8"),)
                    self.pool.get("rhwl.weixin.base").send_qy_text(cr,SUPERUSER_ID,"rhwlyy","is_material_approve",send_text,context=context)
                elif(i.state=="approve1"):
                    send_text = "申请单[%s]已通过第一次核准，请通知第二核准人处理。" %(i.name.encode("utf-8"),)
                    self.pool.get("rhwl.weixin.base").send_qy_text(cr,SUPERUSER_ID,"rhwlyy","is_material_approve",send_text,context=context)
                elif(i.state=="approve2"):
                    send_text = "申请单[%s]已通过第二次核准，请及时处理发货。" %(i.name.encode("utf-8"),)
                    self.pool.get("rhwl.weixin.base").send_qy_text(cr,SUPERUSER_ID,"rhwlyy","is_material_express",send_text,context=context)
                elif(i.state=="done"):
                    send_text = "申请单[%s]已发货，快递公司[%s]，快递单号[%s]，请注意查收。" %(i.name.encode("utf-8"),i.express_partner.encode("utf-8"),i.express_no.encode("utf-8"))
                    u_ids = self.pool.get("rhwl.weixin").search(cr,SUPERUSER_ID,[("base_id.code","=","rhwlyy"),("user_id.id","=",i.user_id.id)],context=context)
                    self.pool.get("rhwl.weixin.base").send_qy_text_ids(cr,SUPERUSER_ID,u_ids,send_text,context=context)
        return res

    def action_state_confirm(self,cr,uid,ids,context=None):
        self.write(cr,uid,ids,{"state":"confirm"},context=context)

    def action_state_approve1(self,cr,uid,ids,context=None):
        self.write(cr,uid,ids,{"state":"approve1","approve1_user":uid,"approve1_date":fields.datetime.now()},context=context)

    def action_state_approve2(self,cr,uid,ids,context=None):
        self.write(cr,uid,ids,{"state":"approve2","approve2_user":uid,"approve2_date":fields.datetime.now()},context=context)

    def action_state_done(self,cr,uid,ids,context=None):
        for i in self.browse(cr,uid,ids,context=context):
            if not (i.express_partner and i.express_no):
                raise osv.except_osv("Error",u"确认完成时，请输入快递公司和快递单号。")
        self.write(cr,uid,ids,{"state":"done","done_date":fields.datetime.now()},context=context)

    def action_create_picking(self,cr,uid,ids,context=None):
        obj = self.browse(cr,uid,ids,context=context)
        stock_warehouse = self.pool.get("stock.warehouse")

        location_id = self.pool.get("stock.location").search(cr,uid,[("usage","=","internal"),("loc_barcode","=","OFFICE")])
        wh = stock_warehouse.search(cr,uid,[("partner_id","=",1)])
        picking_type = self.pool.get("stock.picking.type").search(cr,uid,[("warehouse_id","=",wh[0]),("code","=","internal")])
        if obj.wh_level=="person":
            partner_id = obj.user_id.partner_id.id
        else:
            partner_id = obj.hospital.id

        wh_id = stock_warehouse.search(cr, SUPERUSER_ID, [('partner_id', '=',partner_id)],context=context)
        if not wh_id:
            raise osv.except_osv('Error', u"[%s]没有归属仓库。"%(obj.user_id.partner_id.name if obj.wh_level=="person" else obj.hospital.name,))
        wh_obj = stock_warehouse.browse(cr,SUPERUSER_ID,wh_id[0],context=context)
        location_dest_id = wh_obj.lot_stock_id.id
        val_0={
            "partner_id":1,
            "min_date":fields.datetime.now(),
            "origin":obj.name,
            "picking_type_id":picking_type[0],
            "move_lines":[],
        }
        for l in obj.line:
            if l.qty==0:continue
            move_val={
                "product_id":l.product_id.id
            }
            res=self.pool.get("stock.move").onchange_product_id(cr,uid,0,l.product_id.id)
            move_val.update(res["value"])
            move_val["product_uom_qty"]=l.qty
            move_val["product_uos_qty"]=l.qty

            move_val["location_dest_id"]=location_dest_id
            move_val["location_id"] = location_id[0]

            move_id = self.pool.get("stock.move").create(cr,uid,move_val,context=context)
            val_0["move_lines"].append([4,move_id])

        if val_0["move_lines"]:
            self.pool.get("stock.picking").create(cr,uid,val_0,context=context)


    def action_view_picking(self,cr,uid,ids,context=None):
        obj = self.browse(cr,uid,ids,context)
        picking_id = self.pool.get("stock.picking").search(cr,uid,[("origin","=",obj.name),("state","!=","cancel")])
        if not picking_id:
            self.action_create_picking(cr,uid,ids,context=context)
            picking_id = self.pool.get("stock.picking").search(cr,uid,[("origin","=",obj.name),("state","!=","cancel")])
        for p in self.pool.get("stock.picking").browse(cr,uid,picking_id,context=context):
            back_id = self.pool.get("stock.picking").search(cr,uid,[("origin","=",p.name)])
            if back_id:
                picking_id = picking_id+back_id

        mod_obj = self.pool.get('ir.model.data')
        dummy, action_id = tuple(mod_obj.get_object_reference(cr, uid, 'stock', 'action_picking_tree'))
        action = self.pool.get('ir.actions.act_window').read(cr, uid, action_id, context=context)
        action['context'] = {}
        if len(picking_id) > 1:
            action['domain'] = "[('id','in',[" + ','.join(map(str, picking_id)) + "])]"
        else:
            res = mod_obj.get_object_reference(cr, uid, 'stock', 'view_picking_form')
            action['views'] = [(res and res[1] or False, 'form')]
            action['res_id'] = picking_id and picking_id[0] or False

        return action

class web_material_line(osv.osv):
    _name="rhwl.web.material.line"
    _columns={
        "parent_id":fields.many2one("rhwl.web.material",string="Parent"),
        "product_id":fields.many2one("product.product","Product",required=True,domain=[("is_web","=",True)]),
        "uom_id":fields.related("product_id","uom_id",type="many2one",obj="product.uom",string="Unit",readonly=True),
        "qty":fields.float("Qty",digits_compute=dp.get_precision('Product Unit of Measure'),required=True,),
    }