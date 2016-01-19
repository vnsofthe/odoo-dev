# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
import datetime
import re
"""
探针号,浓度,单位,易感61位点,常见肿瘤3项,常见肿瘤6项,常见肿瘤10项
rs671,20*,1uL,35.5,,55.38461538,45
rs2069514,20*,1uL,35.5,,,
rs1800566,20*,1uL,35.5,51.42857143,55.38461538,45
rs2066702,20*,1uL,35.5,,,
rs662,20*,1uL,35.5,,,
rs12720461,20*,1uL,35.5,,,
rs1229984,20*,1uL,35.5,,55.38461538,45
rs1695,20*,1uL,35.5,51.42857143,55.38461538,45
rs1050152,20*,1uL,35.5,,,
rs731236,40*,1uL,71,,,
rs34637584,40*,1uL,71,,,
rs25487,40*,1uL,71,,,
rs231775,40*,1uL,71,,,
rs1884444,40*,1uL,71,,,
rs1799782,40*,1uL,71,,,
rs1799724,40*,1uL,71,,,
rs16944,40*,1uL,71,,,
rs1136410,40*,1uL,71,,,90
rs31480,40*,1uL,71,,,
rs1234315,40*,1uL,71,,,
rs660339,40*,1uL,71,,,
rs6682925,40*,1uL,71,,,
rs708272,40*,1uL,71,,,
rs7412,40*,1uL,71,,,
rs769214,40*,1uL,71,,,
rs9344,40*,1uL,71,,,
rs9642880,40*,1uL,71,,,
rs13306517,40*,1uL,71,,,
rs285,40*,1uL,71,,,
rs34778348,40*,1uL,71,,,
rs429358,40*,1uL,71,,,
rs4673,40*,1uL,71,,,
rs4880,40*,1uL,71,102.8571429,110.7692308,90
rs5051,40*,1uL,71,,,
rs5186,40*,1uL,71,,,
rs5443,40*,1uL,71,,,
rs1801133,40*,1uL,71,102.8571429,110.7692308,90
rs2073618,40*,1uL,71,,,
rs2107538,40*,1uL,71,,,
rs2221903,40*,1uL,71,,,
rs2228570,40*,1uL,71,,,
rs2230806,40*,1uL,71,,,
rs2241766,40*,1uL,71,102.8571429,110.7692308,90
rs2274223,40*,1uL,71,102.8571429,110.7692308,90
rs1042713,40*,1uL,71,,,
rs1799793,40*,1uL,71,,,
rs1799895,40*,1uL,71,,,
rs1799983,40*,1uL,71,,,
rs1799998,40*,1uL,71,,,
rs1800629,40*,1uL,71,102.8571429,110.7692308,90
rs1800795,40*,1uL,71,,,
rs1801131,40*,1uL,71,102.8571429,110.7692308,90
rs1051266,40*,1uL,71,,,
rs2031920,40*,1uL,71,,,
rs4646903,40*,1uL,71,,,
rs1544410,40*,1uL,71,,,
rs320,40*,1uL,71,,,
rs693,40*,1uL,71,,,
rs1799929,20*,1uL,,,,45
rs1042522,40*,1uL,,102.8571429,110.7692308,90
rs4444903,40*,1uL,,102.8571429,110.7692308,90
rs2273535,40*,1uL,,102.8571429,110.7692308,90
rs10380,40*,1uL,,,,90
rs138213197,40*,1uL,,,110.7692308,90
rs1801155,40*,1uL,,102.8571429,110.7692308,90
rs16969968,40*,1uL,,102.8571429,110.7692308,90
rs3212227,40*,1uL,,,,90
rs4919510,40*,1uL,,,,90
rs6505162,40*,1uL,,,110.7692308,90
rs1052133,40*,1uL,,,,90
rs2294008,40*,1uL,,102.8571429,110.7692308,90
rs2070600,40*,1uL,,102.8571429,110.7692308,90
rs1867277,40*,1uL,,,,90
rs1800562,40*,1uL,,102.8571429,110.7692308,90
rs10936599,40*,1uL,,,,90
rs4680,20*,1uL,,51.42857143,55.38461538,45
rs2736098,40*,1uL,,,,90
rs11614913,40*,1uL,,102.8571429,110.7692308,90
rs12255372,40*,1uL,,102.8571429,110.7692308,90
rs16901979,40*,1uL,,,110.7692308,90
rs2011077,40*,1uL,,,110.7692308,90
rs2074356,40*,1uL,,,110.7692308,90
rs2107301,40*,1uL,,,110.7692308,90
rs29232,40*,1uL,,,,90
rs3790844,40*,1uL,,,,90
rs401681,40*,1uL,,,,90
rs505922,40*,1uL,,,,90
rs6983267,40*,1uL,,102.8571429,110.7692308,90
rs710521,40*,1uL,,,,90
rs944289,40*,1uL,,,,90
rs9510787,40*,1uL,,,,90
rs965513,40*,1uL,,,,90
GSTM1-F,200µM,1uL,394.4444444,,,
GSTM1-R,200µM,1uL,394.4444444,,,
GSTM1-Probe,100µM,1uL,887.5,,,
GSTT1-Probe,100µM,1uL,887.5,,,
GSTT1-F,200µM,1uL,394.4444444,,,
GSTT1-R,200µM,1uL,394.4444444,,,
"""
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

    def check_unit(self,cr,uid,uom,uom_po,factor,context=None):
        if factor:
            unit_id1 = self.pool.get("product.uom").search(cr,uid,[("category_id.id","=",1),("name","=",uom+"(1/"+factor+uom_po+")")])
            if not unit_id1:
                unit_id1 = self.pool.get("product.uom").create(cr,uid,{"category_id":1,"name":uom+"(1/"+factor+uom_po+")","rounding":0.001,"factor":factor,"uom_type":"smaller"})
            else:
                unit_id1 = unit_id1[0]
        else:
            unit_id1 = self.pool.get("product.uom").search(cr,uid,[("category_id.id","=",1),("name","=",uom)])
            if not unit_id1:
                unit_id1 = self.pool.get("product.uom").create(cr,uid,{"category_id":1,"name":uom,"rounding":0.001,"factor":1,"uom_type":"smaller"})
            else:
                unit_id1 = unit_id1[0]
        if uom==uom_po:
            unit_id2 = unit_id1
        else:
            unit_id2 = self.pool.get("product.uom").search(cr,uid,[("category_id.id","=",1),("name","=",uom_po)])
            if not unit_id2:
                unit_id2 = self.pool.get("product.uom").create(cr,uid,{"category_id":1,"name":uom_po,"rounding":0.001,"factor":1,"uom_type":"smaller"})
            else:
                unit_id2 = unit_id2[0]

        return unit_id1,unit_id2

    def action_done(self,cr,uid,ids,context=None):
        ids = self.search(cr,uid,[],context=context)
        product_template = self.pool.get("product.template")
        for i in self.browse(cr,uid,ids,context=context):
            pt_id = product_template.search_count(cr,uid,[("default_code","=",i.col1)])
            if pt_id>0:
                pt_id = product_template.search(cr,uid,[("default_code","=",i.col1)])
                if i.col2:
                    if self.pool.get("rhwl.product.project").search_count(cr,uid,[("product_id.product_tmpl_id","in",pt_id),("project_id","=",21)])==0:
                        project_id = self.pool.get("product.product").search(cr,uid,[("product_tmpl_id","in",pt_id)])
                        for p in project_id:
                            self.pool.get("rhwl.product.project").create(cr,uid,{"product_id":p,"project_id":21,"sample_count":i.col2},context=context)
                if i.col3:
                    if self.pool.get("rhwl.product.project").search_count(cr,uid,[("product_id.product_tmpl_id","in",pt_id),("project_id","=",20)])==0:
                        project_id = self.pool.get("product.product").search(cr,uid,[("product_tmpl_id","in",pt_id)])
                        for p in project_id:
                            self.pool.get("rhwl.product.project").create(cr,uid,{"product_id":p,"project_id":20,"sample_count":i.col3},context=context)
                if i.col4:
                    if self.pool.get("rhwl.product.project").search_count(cr,uid,[("product_id.product_tmpl_id","in",pt_id),("project_id","=",22)])==0:
                        project_id = self.pool.get("product.product").search(cr,uid,[("product_tmpl_id","in",pt_id)])
                        for p in project_id:
                            self.pool.get("rhwl.product.project").create(cr,uid,{"product_id":p,"project_id":22,"sample_count":i.col4},context=context)
                continue
            p_project=[]
            if i.col2:
                p_project.append([0,0,{"project_id":21,"sample_count":i.col2}])
            if i.col3:
                p_project.append([0,0,{"project_id":20,"sample_count":i.col3}])
            if i.col4:
                p_project.append([0,0,{"project_id":22,"sample_count":i.col4}])

            vals={
                "name":u"探针:"+i.col1,
                "sale_ok":False,
                "uom_id":146,
                "default_code":i.col1,
                "cost_allocation":True,
                "uom_po_id":146,
                "categ_id":68,
                "project_ids":p_project
            }
            product_template.create(cr,uid,vals)

        ids = self.pool.get("product.product").search(cr,uid,[("name","ilike",u"探针:")],context=context)
        if ids:
            for i in self.pool.get("product.product").browse(cr,uid,ids,context=context):
                point_id = self.pool.get("stock.warehouse.orderpoint").search(cr,uid,[("product_id","=",i.id)])
                if point_id:continue
                res_qty = self.pool.get("stock.warehouse.orderpoint").onchange_min_work_days(cr,uid,0,45,i.id,context=context)
                vals={
                    'warehouse_id':1,
                    'location_id':12,
                    'product_id':i.id,
                    "min_work_days":45,
                    'product_min_qty':0,
                    'product_max_qty':0,
                }
                if res_qty["value"]:
                    vals.update(res_qty["value"])
                self.pool.get("stock.warehouse.orderpoint").create(cr,uid,vals,context=context)

    def action_done_old(self,cr,uid,ids,context=None):
        ids = self.search(cr,uid,[],context=context)
        product_template = self.pool.get("product.template")
        product_attribute = self.pool.get("product.attribute")
        product_attribute_value = self.pool.get("product.attribute.value")

        attribute_id = product_attribute.search(cr,uid,[("name","=","规格")])
        if not attribute_id:
            attribute_id = product_attribute.create(cr,uid,{"name":"规格"},context=context)
        else:
            attribute_id = attribute_id[0]
        template_ids = product_template.search(cr,uid,[("type","=","product"),'|',("default_code","=",False),("default_code","!=","P001")])
        product_template.write(cr,uid,template_ids,{"active":False})
        for i in self.browse(cr,uid,ids,context=context):
            categ_id = self.check_product_category(cr,uid,i.col1,i.col2,context)
            template_id = product_template.search(cr,uid,[("name","=",i.col11),("description","=",i.col5)])
            if template_id:continue
            unit_id1,unit_id2=self.check_unit(cr,uid,i.col12,i.col13,i.col14,context=context)
            val = {
                "name":i.col11,
                "default_code":i.col4,
                "categ_id":categ_id,
                "type":"product",
                "uom_id":unit_id1,
                "uom_po_id":unit_id2,
                "cost_allocation":bool(i.col15),
                "sale_ok":False,
                "landed_cost_ok":True,
                "description":i.col5,
                "cost_method":"real",
                "track_all":True,
                "valuation":"real_time"
            }
            #耗用单位
            if i.col16:
                unit_id1,unit_id2=self.check_unit(cr,uid,i.col16,i.col13,i.col17,context=context)
                val["uol_id"]=unit_id1

            if i.col5:
                attribute_value_id = product_attribute_value.search(cr,uid,[("name","=",i.col5),("attribute_id","=",attribute_id)],context=context)
                if not attribute_value_id:
                    attribute_value_id = product_attribute_value.create(cr,uid,{"name":i.col5,"attribute_id":attribute_id},context=context)
                else:
                    attribute_value_id = attribute_value_id[0]
            else:
                attribute_value_id = 0
            template_id = product_template.create(cr,uid,val,context=context)
            if attribute_value_id:
                product_attribute_line_id = self.pool.get("product.attribute.line").create(cr,uid,{"product_tmpl_id":template_id,"attribute_id":attribute_id,"value_ids":[[4,attribute_value_id]]})
            if i.col18:
                project_id = self.pool.get("res.company.project").search(cr,uid,[('name','=',i.col18)])
                if not project_id:
                    project_id = self.pool.get("res.company.project").create(cr,uid,{'name':i.col18,"company_id":1},context=context)
                else:
                    project_id = project_id[0]
                product_id = self.pool.get("product.product").search(cr,uid,[("product_tmpl_id","=",template_id)],context=context)
                self.pool.get("rhwl.product.project").create(cr,uid,{"product_id":product_id[0],"project_id":project_id,"sample_count":i.col19},context=context)
            if i.col20:
                project_id = self.pool.get("res.company.project").search(cr,uid,[('name','=',i.col20)])
                if not project_id:
                    project_id = self.pool.get("res.company.project").create(cr,uid,{'name':i.col20,"company_id":1},context=context)
                else:
                    project_id = project_id[0]
                product_id = self.pool.get("product.product").search(cr,uid,[("product_tmpl_id","=",template_id)],context=context)
                self.pool.get("rhwl.product.project").create(cr,uid,{"product_id":product_id[0],"project_id":project_id,"sample_count":i.col21},context=context)

    def action_purchase(self,cr,uid,ids,context=None):
        ids = self.search(cr,uid,[],context=context)
        product_template = self.pool.get("product.template")
        vals={
            "partner_id":1
        }
        pline=[]
        pick = self.pool.get("purchase.order")._get_picking_in(cr,uid)
        local = self.pool.get("purchase.order").onchange_picking_type_id(cr,uid,0,pick,context=context)

        val = self.pool.get("purchase.order").onchange_partner_id(cr,uid,0,vals["partner_id"],context=context).get("value")
        val.update(local.get('value'))
        val.update({'picking_type_id':pick,'partner_id':vals["partner_id"]})
        for i in self.browse(cr,uid,ids,context=context):
            if i.col8=="0":continue
            template_id = product_template.search(cr,uid,[("name","=",i.col11),("description","=",i.col5)])
            if not template_id:
                raise osv.except_osv("error","name[%s] is not exists." %(i.col11))
            product_id = self.pool.get("product.product").search(cr,uid,[("product_tmpl_id","=",template_id)])
            product_obj = self.pool.get("product.product").browse(cr,uid,product_id[0],context=context)
            #onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,partner_id, date_order=False, fiscal_position_id=False, date_planned=False,name=False, price_unit=False, state='draft', context=None):
            detail_val = self.pool.get("purchase.order.line").onchange_product_id(cr, uid, 0, val.get("pricelist_id"),product_id[0], float(i.col8), product_obj.uom_id.id, 1,val.get("date_order"),val.get("fiscal_position"),val.get("date_planned"),False,False,'draft',context=context).get("value")
            detail_val.update({'product_id':product_id[0],'product_qty':float(i.col8),'price_unit':float(i.col10)/float(i.col8)})
            pline.append([0,0,detail_val])

        val.update({'company_id':1,'order_line':pline})
        self.pool.get("purchase.order").create(cr,uid,val,context=context)