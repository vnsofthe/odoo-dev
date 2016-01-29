from openerp.osv import osv, fields


class IrActionsActWindowMenu(osv.Model):
    _name = 'ir.actions.act_window.menu'
    _description = 'Menu on the actions'

    _columns = {
        'name': fields.char('Label', size=64, required=True, translate=True),
        'active': fields.boolean(
            'Active', help='if check, this object is always available'),
    }

    _defaults = {
        'active': True,
    }


class IrActionsActWindowButton(osv.Model):
    _name = 'ir.actions.act_window.button'
    _description = 'Button to display'

    _order = 'name'

    _columns = {
        'action_from_id': fields.many2one('ir.actions.act_window', 'from Action',
                                          required=True),
        'action_to_open_id': fields.many2one('ir.actions.actions', 'to Action',
                                             required=True),
        'name': fields.char('Label', size=64, required=True, translate=True),
        'menu_id': fields.many2one('ir.actions.act_window.menu', 'Menu'),
        'active': fields.boolean(
            'Active', help='if check, this object is always available'),
        'visibility_model_name': fields.char(u"Modele",
                                             help=u"Model where visible_button_method_name is"
                                                  u"define to manage the button visibility."),
        'visible_button_method_name': fields.char('Visibility method name',
                                                  help=u"Method that tell if the button should be "
                                                       u"visible or not, return True if it must "
                                                       u"be visible False otherwise."
                                                       u"def Method(cr, uid, context=None)"),
    }

    _defaults = {
        'active': True,
    }

    def format_buttons(self, cr, uid, ids, context=None):
        res = {}
        action = self.pool.get('ir.actions.actions')

        def get_action(action_id):
            model = self.pool.get(action.read(cr, uid, action_id, ['type'],
                                              context=context)['type'])
            return model.read(cr, uid, action_id, [], load="_classic_write",
                              context=context)

        for this in self.browse(cr, uid, ids, context=context):
            if not this.active:
                continue

            if this.menu_id:
                if not this.menu_id.active:
                    continue

            if this.visibility_model_name and this.visible_button_method_name:
                model = self.pool.get(this.visibility_model_name)
                if not getattr(model, this.visible_button_method_name)(
                        cr, uid, context=context):
                    continue

            menu = this.menu_id.name if this.menu_id else False

            if menu not in res.keys():
                res[menu] = []

            val = get_action(this.action_to_open_id.id)
            val.update({'name': this.name})
            res[menu].append(val)

        return res


class IrActionsActWindow(osv.Model):
    _inherit = 'ir.actions.act_window'

    _columns = {
        'buttons_ids': fields.one2many('ir.actions.act_window.button',
                                       'action_from_id', 'Buttons'),
    }

    def get_menus_and_buttons(self, cr, uid, ids, context=None):
        res = {}
        button = self.pool.get('ir.actions.act_window.button')
        for this in self.browse(cr, uid, ids, context=context):
            res[this.id] = button.format_buttons(
                cr, uid, [x.id for x in this.buttons_ids], context=context)

        return res
