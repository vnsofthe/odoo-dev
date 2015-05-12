# coding=utf-8

from openerp import SUPERUSER_ID,api
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
import datetime
import openerp
import logging

class rhwl_lib(osv.osv):
    _name="rhwl.library.request"
    _columns={
        "name":fields.char("Name",size=15,readonly=True),
        "date":fields.date("Date"),
        "user_id":fields.many2one("res.users","User",readonly=True),
        "location_id":fields.many2one("stock.location","Location",required=True,domain=[('usage', '=', 'internal')],readonly=True,states={'draft':[('readonly',False)]}),
        "state":fields.selection([("draft","Draft"),("confirm","Confirm"),("done","Done"),("cancel","Cancel")],"State"),
        "line":fields.one2many("rhwl.library.request.line","name","Line",readonly=True,states={'draft':[('readonly',False)]}),
        "note":fields.text("Note"),
        "active":fields.boolean("Active"),
    }

    _defaults={
        "state":'draft',
        "user_id":lambda obj,cr,uid,context=None:uid,
        "date":fields.date.today,
        "active":True
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
        location_dest_id = self.pool.get("stock.location").search(cr,uid,[("usage","=","production")])
        wh = self.pool.get("stock.warehouse").search(cr,uid,[("partner_id","=",1)])
        picking_type = self.pool.get("stock.picking.type").search(cr,uid,[("warehouse_id","=",wh[0]),("code","=","internal")])
        val={
            "partner_id":1,
            "min_date":fields.datetime.now(),
            "origin":obj.name,
            "picking_type_id":picking_type[0],
            "move_lines":[]
        }
        for l in obj.line:
            move_val={
                "product_id":l.product_id.id
            }
            res=self.pool.get("stock.move").onchange_product_id(cr,uid,0,l.product_id.id)
            move_val.update(res["value"])
            move_val["product_uom_qty"]=l.qty
            move_val["location_id"]=obj.location_id.id
            move_val["location_dest_id"]=location_dest_id[0]
            move_id = self.pool.get("stock.move").create(cr,uid,move_val,context=context)
            val["move_lines"].append([4,move_id])


        self.pool.get("stock.picking").create(cr,uid,val,context=context)
        self.write(cr,uid,ids,{"state":"done"},context=context)

    def action_view_picking(self,cr,uid,ids,context=None):
        obj = self.browse(cr,uid,ids,context)
        picking_id = self.pool.get("stock.picking").search(cr,uid,[("origin","=",obj.name)])
        if not picking_id:
            return
        value = {
            'domain': "[('id','in',[" + ','.join(map(str, picking_id)) + "])]",
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'stock.picking',
            'res_id': picking_id[0],
            'view_id': False,
            'context': context,
            'type': 'ir.actions.act_window',

        }
        return value



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
    }
    _sql_constraints = [
        ('rhwl_lib_request_line_uniq', 'unique(name,product_id)', u'明细清单中相同产品不能重复!'),
    ]

    @api.onchange("product_id")
    def _onchange_product(self):
        if self.product_id:
            obj = self.env["product.product"].browse(self.product_id.id)
            self.brand = obj.brand
            self.default_code = obj.default_code
            self.attribute = obj.attribute_value_ids
            self.uom_id = obj.uom_id