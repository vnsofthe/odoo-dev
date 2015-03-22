from openerp.osv import osv
from openerp.tools.translate import _


class NoOrdonalValue(Exception):
    pass


class IrUiViewChartD3(osv.AbstractModel):
    """ Only modele to not put the methods in ir.ui.view """

    _name = 'ir.ui.view.chart.d3'
    _description = 'View for Chart D3'

    def available_values(self, cr, uid, model, domain, field, context=None):
        obj = self.pool.get(model)
        obj_ids = obj.search(cr, uid, domain, context=context)
        r = obj.read(
            cr, uid, obj_ids, [field], load='_classic_write', context=context)
        return list(set(x[field] for x in r))

    def get_data_fields_ordinal_values_many2one(self, cr, uid, fg, field,
                                                model, domain, context=None):
        res = []
        if context is None:
            context = {}

        ctx = context.copy()
        ctx['shortname'] = True
        obj = self.pool.get(fg['relation'])
        obj_ids = self.available_values(cr, uid, model, domain, field,
                                        context=context)
        if not obj_ids:
            return res

        ngs = []
        if False in obj_ids:
            ngs.append((False, _('Without value')))
            obj_ids.remove(False)

        ngs.extend(obj.name_get(cr, uid, obj_ids, context=ctx))

        if len(ngs) == 0:
            raise NoOrdonalValue(_('No data for : %s') % obj._description)

        color = {}
        if hasattr(obj, 'chart_d3_get_color'):
            color.update(obj.chart_d3_get_color(
                cr, uid, obj_ids, model, fg, context=context))

        for order, ng in enumerate(ngs):
            f = {
                'value': ng[0],
                'label': ng[1],
                'order': order,
            }
            if ng[0] in color:
                f['color'] = color[ng[0]]

            res.append(f)

        return res

    def get_data_fields_ordinal_values_selection(self, cr, uid, fg, field,
                                                 model, domain, context=None):
        obj = self.pool.get(model)
        res = []
        color = {}
        if hasattr(obj, 'chart_d3_get_color'):
            color.update(obj.chart_d3_get_color(
                cr, uid, None, model, fg, field, context=context))

        selection = dict(fg['selection'])
        orders = [x[0] for x in fg['selection']]
        vals = self.available_values(
            cr, uid, model, domain, field, context=context)

        for value in vals:
            label = selection.get(value, _('Without value'))
            order = len(orders)
            if value in orders:
                order = orders.index(value)

            f = {
                'value': value,
                'label': label,
                'order': order,
            }
            if value in color:
                f['color'] = color[value]

            res.append(f)

        return res

    def get_data_fields_ordinal_values_other(self, cr, uid, fg, field, model,
                                             domain, context=None):
        obj = self.pool.get(model)
        res = []
        color = {}
        if hasattr(obj, 'chart_d3_get_color'):
            color.update(obj.chart_d3_get_color(
                cr, uid, None, model, fg, field, context=context))

        vals = self.available_values(
            cr, uid, model, domain, field, context=context)
        vals.sort()

        for order, x in enumerate(vals):
            f = {
                'value': x,
                'order': order,
            }
            if x[0] in color:
                f['color'] = color[x]

            res.append(f)

        return res

    def get_data_fields(self, cr, uid, fields_get, domain, fields, model,
                        context=None):
        res = []
        for field in fields:
            fg = fields_get[field]
            ordinal_values = []
            if fg['type'] == 'many2one':
                ordinal_values.extend(
                    self.get_data_fields_ordinal_values_many2one(
                        cr, uid, fg, field, model, domain, context=context))
            elif fg['type'] == "selection":
                ordinal_values.extend(
                    self.get_data_fields_ordinal_values_selection(
                        cr, uid, fg, field, model, domain, context=context))
            else:
                ordinal_values.extend(
                    self.get_data_fields_ordinal_values_other(
                        cr, uid, fg, field, model, domain, context=context))

            res.append({
                'field': field,
                'label': fg['string'],
                'ordinal_values': ordinal_values,
            })

        return res

    def get_data_values(self, cr, uid, obj, xaxis, yaxis, domain, group_by,
                        options, fields_get, d3_fields, context=None):
        values = []
        orderby = obj._order

        def get_keys(keys, field, value):
            if fields_get[field]['type'] == 'many2one':
                if value:
                    value = value[0]

            k = {'key': field, 'value': value}
            return keys + [k]

        def read_group(keys, _domain, _group_by):
            rgs = obj.read_group(cr, uid, _domain, yaxis + _group_by,
                                 _group_by, orderby=orderby, context=context)
            if len(_group_by) == 1:
                for rg in rgs:
                    value = {
                        'keys': get_keys(keys, _group_by[0], rg[_group_by[0]]),
                        'values': [],
                    }
                    for y in yaxis:
                        value['values'].append({
                            'field': y,
                            'value': rg[y],
                        })

                    values.append(value)

            else:
                for rg in rgs:
                    k = get_keys(keys, _group_by[0], rg[_group_by[0]])
                    read_group(k, rg['__domain'], _group_by[1:])

        read_group([], domain, group_by)

        return values

    def get_data(self, cr, uid, model, xaxis, yaxis, domain, groupby, options,
                 context=None):
        obj = self.pool.get(model)
        group_by = []
        for gb in groupby:
            if gb not in group_by:
                group_by.append(gb)

        if not group_by:
            group_by = [xaxis]

        fields_get = obj.fields_get(cr, uid, group_by, context=context)

        try:
            d3_fields = self.get_data_fields(
                cr, uid, fields_get, domain, group_by, model, context=context)
        except NoOrdonalValue, e:
            options.update({'no-data': {'value': e.message}})
            return {
                'fields': [{'field': 'no-field', 'ordinal_values': []}],
                'values': [],
            }, options

        d3_values = self.get_data_values(cr, uid, obj, xaxis, yaxis, domain,
                                         group_by, options, fields_get,
                                         d3_fields, context=context)

        if hasattr(obj, 'chart_d3_update_options'):
            options.update(obj.chart_d3_update_options(
                cr, uid, group_by, options, context=context))

        return {
            'fields': d3_fields,
            'values': d3_values,
        }, options
