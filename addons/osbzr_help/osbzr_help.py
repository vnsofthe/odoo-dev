#-*- ecoding: utf-8 -*-
# __author__ = jeff@osbzr.com

from openerp.osv import fields, osv
from lxml import etree

class osbzr_help(osv.osv):
    '''
	Add help on each module
	'''
    _inherit= 'ir.module.module'
    def open_osbzr_help(self, cr, uid, ids, context=None):
        return {
            'type':'ir.actions.act_url',
            'url':'http://www.osbzr.com/index.php?page='+self.browse(cr, uid, ids, context)[0].name or '',
            'target':'new',
        }
class res_config_settings(osv.osv_memory):
    _inherit = 'res.config.settings'
    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        res = super(res_config_settings,self).fields_view_get(cr, uid, view_id=view_id,
                view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        if view_type != 'form':
            return res
        doc = etree.XML(res['arch'])

        xml_start = etree.Element("a")
        xml_start.set('class','osbzr_model_help')
        xml_start.set('href','http://www.osbzr.com/index.php?page='+self._name)
        xml_start.set('title',u'在线中文帮助')
        xml_start.set('target','new')

        xml_img = etree.Element("img")
        xml_img.set('src','/web/static/src/img/icons/gtk-help.png')
        xml_start.append(xml_img)

        first_node = doc.xpath("//header")
        if first_node and len(first_node)>0:
            first_node[0].insert(0, xml_start)
            res['arch'] = etree.tostring(doc)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
