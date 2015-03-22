# -*- coding: utf-8 -*-
import openerp.addons.web.http as openerpweb
from openerp.pooler import RegistryManager
import simplejson
import base64


class ChartD3(openerpweb.Controller):

    _cp_path = '/web/chartd3'

    @openerpweb.jsonrequest
    def get_data(self, request, model=None, xaxis=None, yaxis=None, domain=None,
                 group_by=None, options=None):

        if domain is None:
            domain = []

        if group_by is None:
            group_by = []

        if options is None:
            options = {}

        obj = request.session.model(model)
        context = request.context
        registry = RegistryManager.get(request.session._db)
        if hasattr(registry.get(model), 'chart_d3_get_data'):
            return obj.chart_d3_get_data(
                xaxis, yaxis, domain, group_by, options, context=context)

        view = request.session.model('ir.ui.view.chart.d3')
        return view.get_data(
            model, xaxis, yaxis, domain, group_by, options, context=context)

    @openerpweb.httprequest
    def export(self, request, data, token):
        kwargs = simplejson.loads(data)
        ext = kwargs.get('ext')
        img = kwargs.get('img')
        title = kwargs.get('title')
        if ext != 'svg':
            head = "data:image/" + ext + ";base64,"
            img = img[len(head):]
            img = base64.decodestring(img)

        header = [
            ('Content-Disposition', 'attachment; filename="%s.%s"' % (title,
                                                                      ext)),
            ('Content-Type', 'image/%s' % ext),
        ]
        return request.make_response(
            img, header, cookies={'fileToken': int(token)})
