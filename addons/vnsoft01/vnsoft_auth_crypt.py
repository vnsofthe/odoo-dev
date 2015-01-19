import openerp
from openerp.osv import fields, osv

class vnsoft_auth_crypt(osv.osv):
    _inherit = "res.users"

    def set_pwd(self, cr, uid, id, name, value):
        self._set_password(cr, uid, id, value, context=None)
        return True