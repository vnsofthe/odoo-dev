# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp import tools, api
import datetime
import logging

_logger = logging.getLogger(__name__)

class rhwl_product_template(osv.osv):
    _inherit = "product.template"

    _columns = {
        "brand":fields.char(u"品牌",size=20),
        "name2":fields.char(u"名称"),
    }
    def create(self, cr, uid, vals, context=None):
        ''' Store the initial standard price in order to be able to retrieve the cost of a product template for a given date'''
        product_template_id = super(rhwl_product_template, self).create(cr, uid, vals, context=context)

        related_vals = {}
        if vals.get('brand'):
            related_vals['brand'] = vals['brand']
        if vals.get('name2'):
            related_vals['name2'] = vals['name2']
        if related_vals:
            self.write(cr, uid, product_template_id, related_vals, context=context)

        return product_template_id

class vnsoft_sale_order(osv.osv):
    _inherit = "sale.order"
    def _chn_amt(self, cr, uid, ids, prop, arg, context=None):
        if isinstance(ids, (list, tuple)) and not len(ids):
            return {}
        if isinstance(ids, (long, int)):
            ids = [ids]
        res = {}
        for i in self.browse(cr,uid,ids,context=context):
            res[i.id] = self.num2chn(i.amount_total)
        return res

    _columns={
        "vn_delay":fields.char(u"货期",size=100),
        "chn_amount_total":fields.function(_chn_amt,type="char",string="chn amount total"),
    }


    def do_create_purchase(self,cr,uid,ids,context=None):
        res=self.browse(cr,uid,ids,context=context)
        res_id=[]
        detail_id = self.pool.get("purchase.order").search(cr,uid,[('origin','=',res.name)],context=context)
        if detail_id:
            result = self.pool.get("product.template")._get_act_window_dict(cr, uid, 'purchase.purchase_rfq', context=context)
            result['domain'] = "[('id','in',[" + ','.join(map(str, detail_id)) + "])]"
            return result

        #for i in res.order_line:
            #res_id.append(self.pool.get("sale.order.purchase").create(cr,uid,{"name":res.id,"product_id":i.product_id.id},context=context))
        return {'type': 'ir.actions.act_window',
                'res_model': 'sale.order.purchase',
                'view_mode': 'form',
                #'view_id':'vnsoft023_view_sale_purchase',
                #'res_id': res_id,
                'target': 'new',
                'context':{"id":res.id},
                'flags': {'form': {'action_buttons': False}}}

    def IIf(self, b, s1, s2):
       if b:
            return s1
       else:
            return s2

    def num2chn(self,nin=None):
        cs =('零','壹','贰','叁','肆','伍','陆','柒','捌','玖','◇','分','角','圆','拾','佰','仟',
                '万','拾','佰','仟','亿','拾','佰','仟','万')
        st = ''; st1=''
        s = '%0.2f' % (nin)
        sln =len(s)
        if sln >15: return None
        fg = (nin<1)
        for i in range(0, sln-3):
            ns = ord(s[sln-i-4]) - ord('0')
            st=self.IIf((ns==0) and (fg or (i==8) or (i==4) or (i==0)), '', cs[ns])+ self.IIf((ns==0)and((i<>8) and (i<>4) and (i<>0) or fg  and(i==0)),'', cs[i+13])+ st
            fg = (ns==0)
        fg = False
        for i in [1,2]:
            ns = ord(s[sln-i]) - ord('0')
            st1=self.IIf(ns==0 and (i==1 or i==2 and (fg or (nin<1))), '', cs[ns]) + self.IIf((ns>0), cs[i+10], self.IIf((i==2) or fg, '', '整')) + st1
            fg = (ns==0)
        st.replace('亿万','万')
        return self.IIf( nin==0, '零', st + st1)

class vnsoft_purchase(osv.osv_memory):
    _name = 'sale.order.purchase'
    _columns = {
        "name":fields.many2one("sale.order",u"销售单号"),
        "line":fields.one2many("sale.order.purchase.line","name",u"明细")
    }

    def default_get(self, cr, uid, fields, context=None):
        res = super(vnsoft_purchase,self).default_get(cr,uid,fields,context)
        if context.get("id"):
            id=context.get("id")
            obj=self.pool.get("sale.order").browse(cr,uid,id,context=context)
            res['name'] = id
            res['line']=[]
            for i in obj.order_line:
                res['line'].append({'product_id':i.product_id.id,'brand':i.product_id.brand,'product_qty':i.product_uom_qty})

        return res

    def do_create(self,cr,uid,ids,context=None):
        d={}
        res_id=[]
        obj=self.browse(cr,uid,ids)

        for i in obj.line:
            if d.has_key(i.partner_id.id):
               d[i.partner_id.id].append([i.product_id.id,i.product_qty])
            else:
               d[i.partner_id.id]=[[i.product_id.id,i.product_qty]]

        #遍历有多少不同的供应商
        for k,v in d.items():
            #遍历供应商下有多少不同的产品

            pline=[]
            pick = self.pool.get("purchase.order")._get_picking_in(cr,uid)
            local = self.pool.get("purchase.order").onchange_picking_type_id(cr,uid,0,pick,context=context)

            val = self.pool.get("purchase.order").onchange_partner_id(cr,uid,0,k,context=context).get("value")
            val.update(local.get('value'))
            val.update({'picking_type_id':pick,'partner_id':k,'origin':obj.name.name,})
            for j in v:
                detail_val = self.pool.get("purchase.order.line").onchange_product_id(cr, uid, 0, val.get("pricelist_id"),j[0], j[1], False, k,val.get("date_order"),val.get("fiscal_position"),val.get("date_planned"),False,False,'draft',context=context).get("value")

                detail_val.update({'product_id':j[0],'product_qty':j[1]})
                _logger.info(detail_val)
                pline.append([0,0,detail_val])

            val.update({'company_id':1,'order_line':pline})

            res_id.append(self.pool.get("purchase.order").create(cr,uid,val,context=context))

        result = self.pool.get("product.template")._get_act_window_dict(cr, uid, 'purchase.purchase_rfq', context=context)
        result['domain'] = "[('id','in',[" + ','.join(map(str, res_id)) + "])]"
        return result

class vnsoft_purchase_line(osv.osv_memory):
    _name = "sale.order.purchase.line"
    _columns = {
        "name":fields.many2one("sale.order.purchase",u"销售单号"),
         "product_id":fields.many2one("product.product",u"产品"),
         "brand":fields.related('product_id', 'brand', type='char', string=u'品牌', readonly=1),
         "product_qty": fields.float(u'数量', digits_compute=dp.get_precision('Product Unit of Measure'),
                                    required=True),
        "partner_id":fields.many2one("res.partner",u"供应商",domain="[('is_company','=',False),('supplier','=',True)]")
    }

class vnsoft_purchase_order(osv.osv):
    _inherit = "purchase.order"
    def _chn_amt(self, cr, uid, ids, prop, arg, context=None):
        if isinstance(ids, (list, tuple)) and not len(ids):
            return {}
        if isinstance(ids, (long, int)):
            ids = [ids]
        res = {}
        for i in self.browse(cr,uid,ids,context=context):
            res[i.id] = self.num2chn(i.amount_total)
        return res

    _columns={
        "vn_delay":fields.char(u"货期",size=100),
        "chn_amount_total":fields.function(_chn_amt,type="char",string="chn amount total"),
    }

    def IIf(self, b, s1, s2):
       if b:
            return s1
       else:
            return s2

    def num2chn(self,nin=None):
        cs =('零','壹','贰','叁','肆','伍','陆','柒','捌','玖','◇','分','角','圆','拾','佰','仟',
                '万','拾','佰','仟','亿','拾','佰','仟','万')
        st = ''; st1=''
        s = '%0.2f' % (nin)
        sln =len(s)
        if sln >15: return None
        fg = (nin<1)
        for i in range(0, sln-3):
            ns = ord(s[sln-i-4]) - ord('0')
            st=self.IIf((ns==0) and (fg or (i==8) or (i==4) or (i==0)), '', cs[ns])+ self.IIf((ns==0)and((i<>8) and (i<>4) and (i<>0) or fg  and(i==0)),'', cs[i+13])+ st
            fg = (ns==0)
        fg = False
        for i in [1,2]:
            ns = ord(s[sln-i]) - ord('0')
            st1=self.IIf(ns==0 and (i==1 or i==2 and (fg or (nin<1))), '', cs[ns]) + self.IIf((ns>0), cs[i+10], self.IIf((i==2) or fg, '', '整')) + st1
            fg = (ns==0)
        st.replace('亿万','万')
        return self.IIf( nin==0, '零', st + st1)

class vnsoft_saleorderline(osv.osv):
     _inherit = "sale.order.line"
     _columns = {
         "brand":fields.related('product_id', 'brand', type='char', string=u'品牌', readonly=1),
     }

     def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        vals = super(vnsoft_saleorderline,self).product_id_change(cr,uid,ids,pricelist,product,qty,uom,qty_uos,uos,name,partner_id,
                                                                  lang,update_tax,date_order,packaging,fiscal_position,flag,context)
        if product:
            pobj = self.pool.get('product.product').browse(cr,uid,product,context)
            vals['value']['brand'] = pobj.brand
        return vals

class vnsoft_purchase_order_line(osv.osv):
     _inherit = "purchase.order.line"
     _columns = {
         "brand":fields.related('product_id', 'brand', type='char', string=u'品牌', readonly=1),
     }
     def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order=False, fiscal_position_id=False, date_planned=False,
            name=False, price_unit=False, state='draft', context=None):
         vals= super(vnsoft_purchase_order_line,self).onchange_product_id(cr,uid,ids,pricelist_id,product_id,qty,uom_id,partner_id,date_order,fiscal_position_id,date_planned,name,price_unit,state,context)
         if product_id:
             pobj = self.pool.get('product.product').browse(cr,uid,product_id,context)
             vals['value']['brand'] = pobj.brand
         return vals

class vnsoft_stock_move(osv.osv):
     _inherit = "stock.move"
     _columns = {
         "brand":fields.related('product_id', 'brand', type='char', string=u'品牌', readonly=1),
     }

class vnsoft_partner(osv.osv):
    _inherit  = "res.partner"
    _columns = {
        "tax_no":fields.char(u"税号",size=30)
    }