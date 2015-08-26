# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
import datetime
import re

class rhwl_import(osv.osv):
    _name = "rhwl.import.temp"

    _columns = {
        "col1":fields.char("col1",size=150),
        "col2":fields.char("col2",size=150),
        "col3":fields.char("col3",size=150),
        "col4":fields.char("col4",size=150),
        "col5":fields.char("col5",size=150),
        "col6":fields.char("col6",size=150),
        "col7":fields.char("col7",size=150),
        "col8":fields.char("col8",size=150),
        "col9":fields.char("col9",size=150),
        "col10":fields.char("col10",size=150),
        "col11":fields.char("col11",size=150),
        "col12":fields.char("col12",size=150),
        "col13":fields.char("col13",size=150),
        "col14":fields.char("col14",size=150),
        "col15":fields.char("col15",size=150),
        "col16":fields.char("col16",size=150),
        "col17":fields.char("col17",size=150),
        "col18":fields.char("col18",size=150),
        "col19":fields.char("col19",size=150),
        "col20":fields.char("col20",size=150),
        "col21":fields.char("col21",size=150),
        "col22":fields.char("col22",size=150),
        "col23":fields.char("col23",size=150),
        "col24":fields.char("col24",size=150),
        "col25":fields.char("col25",size=150),
    }

    def check_product_category(self,cr,uid,parent_cate,cate,context=None):
        cate_obj = self.pool.get("product.category")
        pcate_id = cate_obj.search(cr,uid,[("parent_id.id","=",1),("name","=","实验用品")])
        if not pcate_id:
            pcate_id = cate_obj.create(cr,uid,{"parent_id":1,"name":"实验用品"},context=context)
        else:
            pcate_id = pcate_id[0]
        parent_id = cate_obj.search(cr,uid,[("parent_id.id","=",pcate_id),("name","=",parent_cate)])
        if not parent_id:
            parent_id = cate_obj.create(cr,uid,{"parent_id":pcate_id,"name":parent_cate},context=context)
        else:
            parent_id = parent_id[0]
        id = cate_obj.search(cr,uid,[("parent_id.id","=",parent_id),("name","=",cate)])
        if not id:
            id = cate_obj.create(cr,uid,{"parent_id":parent_id,"name":cate},context=context)
        else:
            id = id[0]
        return id

    def action_done(self,cr,uid,ids,context=None):
        ids = self.search(cr,uid,[],context=context)
        product_template = self.pool.get("product.template")
        for i in self.browse(cr,uid,ids,context=context):
            categ_id = self.check_product_category(cr,uid,i.col1,i.col2,context)
            product_template.create(cr,uid,{
                "name":i.col11,
                "categ_id":categ_id,
                "type":"product"
            },context=context)

