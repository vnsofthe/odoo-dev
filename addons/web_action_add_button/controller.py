import openerp.addons.web.http as openerpweb


class WebActionAddButton(openerpweb.Controller):

    _cp_path = '/web/action/add/button'

    @openerpweb.jsonrequest
    def get_buttons(self, request, action_id):
        obj = request.session.model('ir.actions.act_window')
        return obj.get_menus_and_buttons([action_id])[action_id]
