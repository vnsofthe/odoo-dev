# -*- coding: utf-8 -*-
from openerp.osv import osv, fields


class ChartD3Color(osv.AbstractModel):
    _name = 'chart_d3.color'
    _description = 'Chart d3 color'

    _columns = {
        'color': fields.char(
            u"Couleur", size=64,
            help=u"Toutes couleur valid css, exemple blue ou #f57900"),
    }

    def chart_d3_get_color(self, cr, uid, ids, model, fields_get, context=None):
        colors = self.read(cr, uid, ids, ['color'], context=context)
        colors = [(x['id'], x['color']) for x in colors if x['color']]
        return dict(colors)
