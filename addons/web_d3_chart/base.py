# -*- coding: utf-8 -*-
from openerp.osv import osv
from openerp.tools.translate import _
from openerp.addons.base.ir.ir_actions import VIEW_TYPES
from logging import getLogger
from lxml import etree


_logger = getLogger(__name__)
VIEW_TYPE = ('chart-d3', _('Chart D3'))
VIEW_TYPES.append(VIEW_TYPE)


class IrUiView(osv.Model):
    _inherit = 'ir.ui.view'

    def __init__(self, pool, cr):
        res = super(IrUiView, self).__init__(pool, cr)
        select = [k for k, v in self._columns['type'].selection]
        if VIEW_TYPE[0] not in select:
            self._columns['type'].selection.append(VIEW_TYPE)
        return res

    def valid_type_chart_d3_field_exist(self, cr, uid, model, field,
                                        context=None):
        domain = [
            ('model', '=', model),
            ('name', '=', field),
        ]
        if not self.pool.get('ir.model.fields').search(cr, uid, domain,
                                                       context=context):
            return False
        return True

    def valid_type_chart_d3_options(self, cr, uid, arch, context=None):
        res = True
        #TODO
        return res

    def valid_type_chart_d3_x_axis(self, cr, uid, arch, model, context=None):
        axis = 'x-axis'
        res = True
        _axis = arch.xpath(axis)
        if not _axis:
            res = False
            _logger.error("The %r node must have %r node" % (
                VIEW_TYPE[0], axis))
        elif len(_axis) > 1:
            res = False
            _logger.error(
                "the %r node must only have 1 %r node" % (VIEW_TYPE[0], axis))
        else:
            field = _axis[0].attrib.get('field')
            if not self.valid_type_chart_d3_field_exist(cr, uid, model, field,
                                                        context=context):
                res = False
                _logger.error(
                    "the field %r in the %r node doesn't exist" %
                    (_axis[0].text, axis))

        return res

    def valid_type_chart_d3_y_axis(self, cr, uid, arch, model, context=None):
        axis = 'y-axis'
        res = True
        _axis = arch.xpath(axis)
        if not _axis:
            res = False
            _logger.error("The %r node must have %r node" % (
                VIEW_TYPE[0], axis))
        elif len(_axis) > 1:
            res = False
            _logger.error(
                "the %r node must only have 1 %r node" % (VIEW_TYPE[0], axis))
        else:
            fields = _axis[0].getchildren()
            if not fields:
                res = False
                _logger.error("the %r.%r node must have %r nodes" % (
                    VIEW_TYPE[0], axis, 'field'))

            for field in fields:
                fname = field.attrib.get('name')
                if not self.valid_type_chart_d3_field_exist(cr, uid, model,
                                                            fname,
                                                            context=context):
                    res = False
                    _logger.error(
                        "the field %r in the %r.%r node doesn't exist" %
                        (fname, axis, 'field'))

        return res

    def valid_type_chart_d3(self, cr, uid, arch, model, context=None):
        res = True

        if arch.tag == VIEW_TYPE[0] and not arch.attrib.get('type'):
            res = False
            _logger.error(
                "The %r node must have 'type' attribute" % VIEW_TYPE[0])

        if not self.valid_type_chart_d3_x_axis(cr, uid, arch, model,
                                               context=context):
            res = False

        if not self.valid_type_chart_d3_y_axis(cr, uid, arch, model,
                                               context=context):
            res = False

        if not self.valid_type_chart_d3_options(cr, uid, arch, context=context):
            res = False

        return res

    def _check_xml_chart_d3(self, cr, uid, ids, context=None):
        domain = [
            ('id', 'in', ids),
            ('type', '=', VIEW_TYPE[0]),
        ]
        view_ids = self.search(cr, uid, domain, context=context)
        for view in self.browse(cr, uid, view_ids, context=context):
            fvg = self.pool.get(view.model).fields_view_get(
                cr, uid, view_id=view.id, view_type=view.type, context=context)
            view_arch_utf8 = fvg['arch']
            view_docs = [etree.fromstring(view_arch_utf8)]
            if view_docs[0].tag == 'data':
                view_docs = view_docs[0]
            for view_arch in view_docs:
                if not self.valid_type_chart_d3(cr, uid, view_arch, view.model,
                                                context=context):
                    return False

        return True

    _constraints = [
        (
            _check_xml_chart_d3,
            'Invalide XML for chart D3 view architecture',
            ['arch'],
        ),
    ]
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
