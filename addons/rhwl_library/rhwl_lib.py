# coding=utf-8

from openerp import SUPERUSER_ID,api
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
import datetime
import openerp
import logging

_logger = logging.getLogger(__name__)
class rhwl_lib(osv.osv):
    _name="rhwl.library.request"
    _order = "date desc"

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
        "name":fields.char("Name",size=15,readonly=True),
        "date":fields.date("Date"),
        "user_id":fields.many2one("res.users","User",readonly=True),
        "location_id":fields.many2one("stock.location","Location",required=True,domain=[('usage', '=', 'internal')],readonly=True,states={'draft':[('readonly',False)]}),
        "state":fields.selection([("draft","Draft"),("confirm","Confirm"),("done","Done"),("cancel","Cancel")],"State"),
        "line":fields.one2many("rhwl.library.request.line","name","Line",readonly=True,states={'draft':[('readonly',False)]}),
        "note":fields.text("Note"),
        "active":fields.boolean("Active"),
        "project":fields.many2one("res.company.project","Project",required=True),
        "is_rd":fields.boolean("R&D"),
        "picking_state":fields.function(_get_picking_state,type="char",string=u"出库单状态"),
    }

    _defaults={
        "state":'draft',
        "user_id":lambda obj,cr,uid,context=None:uid,
        "date":fields.date.today,
        "active":True,
        "is_rd":False
    }

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if vals.get('name', '/') == '/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'rhwl.library.request') or '/'
        return super(rhwl_lib,self).create(cr,uid,vals,context)

    def action_state_confirm(self,cr,uid,ids,context=None):
        self.write(cr,uid,ids,{"state":"confirm"},context=context)

    def action_state_reset(self,cr,uid,ids,context=None):
        self.write(cr,uid,ids,{"state":"draft"},context=context)

    def action_state_done(self,cr,uid,ids,context=None):
        obj = self.browse(cr,uid,ids,context=context)
        location_dest_id_99 = self.pool.get("stock.location").search(cr,uid,[("usage","=","internal"),("loc_barcode","=","99")])
        location_dest_id_0 = self.pool.get("stock.location").search(cr,uid,[("usage","=","production")])
        wh = self.pool.get("stock.warehouse").search(cr,uid,[("partner_id","=",1)])
        picking_type = self.pool.get("stock.picking.type").search(cr,uid,[("warehouse_id","=",wh[0]),("code","=","internal")])
        val_99={
            "partner_id":1,
            "min_date":fields.datetime.now(),
            "origin":obj.name,
            "picking_type_id":picking_type[0],
            "move_lines":[],
            "project":obj.project.id,
            "is_rd":obj.is_rd,
        }
        val_0={
            "partner_id":1,
            "min_date":fields.datetime.now(),
            "origin":obj.name,
            "picking_type_id":picking_type[0],
            "move_lines":[],
            "project":obj.project.id,
            "is_rd":obj.is_rd,
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
            if l.product_id.cost_allocation:
                move_val["location_dest_id"]=location_dest_id_99[0]
            else:
                move_val["location_dest_id"]=location_dest_id_0[0]
            move_val["location_id"]=obj.location_id.id

            move_id = self.pool.get("stock.move").create(cr,uid,move_val,context=context)
            if l.product_id.cost_allocation:
                val_99["move_lines"].append([4,move_id])
            else:
                val_0["move_lines"].append([4,move_id])

        if val_99["move_lines"]:
            self.pool.get("stock.picking").create(cr,uid,val_99,context=context)
        if val_0["move_lines"]:
            self.pool.get("stock.picking").create(cr,uid,val_0,context=context)
        self.write(cr,uid,ids,{"state":"done"},context=context)

    def action_view_picking(self,cr,uid,ids,context=None):
        obj = self.browse(cr,uid,ids,context)
        picking_id = self.pool.get("stock.picking").search(cr,uid,[("origin","=",obj.name)])
        if not picking_id:
            self.action_state_done(cr,uid,ids,context=context)
            picking_id = self.pool.get("stock.picking").search(cr,uid,[("origin","=",obj.name)])
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


class rhwl_lib_line(osv.osv):
    _name="rhwl.library.request.line"
    _columns={
        "name":fields.many2one("rhwl.library.request","Name"),
        "product_id":fields.many2one("product.product","Product",required=True),
        "brand":fields.related("product_id","brand",type="char",string=u"品牌",readonly=True),
        "default_code":fields.related("product_id","default_code",type="char",string=u"货号",readonly=True),
        "attribute":fields.related("product_id","attribute_value_ids",obj="product.attribute.value", type="many2many",string=u"规格",readonly=True),
        "uom_id":fields.related("product_id","uom_id",type="many2one",obj="product.uom",string="Unit",readonly=True),
        "qty":fields.float("Qty",digits_compute=dp.get_precision('Product Unit of Measure'),required=True,),
        "real_qty":fields.float("Real Qty",digits_compute=dp.get_precision('Product Unit of Measure'),required=True ),
        "note":fields.char(u"备注",size=200),
    }
    #_sql_constraints = [
    #    ('rhwl_lib_request_line_uniq', 'unique(name,product_id)', u'明细清单中相同产品不能重复!'),
    #]

    _defaults={
        "qty":0,
        "real_qty":0
    }
    @api.onchange("product_id")
    def _onchange_product(self):
        if self.product_id:
            obj = self.env["product.product"].browse(self.product_id.id)
            self.brand = obj.brand
            self.default_code = obj.default_code
            self.attribute = obj.attribute_value_ids
            self.uom_id = obj.uom_id

class rhwl_stock(osv.osv):
    _inherit = "stock.picking"
    _columns = {
        "project":fields.many2one("res.company.project","Project"),
        "is_rd":fields.boolean("R&D"),
    }
class rhwl_purchase_requisition(osv.osv):
    _inherit="purchase.requisition"

    def purchase_requisition(self,cr,uid,id,context=None):
        obj = self.browse(cr,uid,id,context=context)
        if obj.origin:
            app_id = self.pool.get("purchase.order.apply").search(cr,uid,[("name","=",obj.origin)])
            if app_id:
                raise osv.except_osv("Error","该招标单已经有关联的采购申请单，不可以重复建立。")
        if obj.line_ids:
            app_id = self.pool.get("purchase.order.apply").create(cr,uid,{},context=context)
            apply_obj = self.pool.get("purchase.order.apply").browse(cr,uid,app_id,context=context)
        else:
            return

        for l in obj.line_ids:
            pid = self.pool.get("purchase.order.apply.line").create(cr,uid,{"product_id":l.product_id.id,"qty":l.product_qty},context=context)
            self.pool.get("purchase.order.apply").write(cr,uid,app_id,{"line":[[4,pid]]})

        self.write(cr,uid,id,{"origin":apply_obj.name},context=context)

        result = self.pool.get("product.template")._get_act_window_dict(cr, uid, 'rhwl.action_purchase_order_apply', context=context)
        result['domain'] = "[('id','in',[" + str(app_id) + "])]"
        return result