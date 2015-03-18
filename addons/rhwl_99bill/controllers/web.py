# -*- coding: utf-8 -*-

from openerp import http
from openerp.http import request
from openerp.addons.base.res.res_users import res_users
import json,simplejson
import openerp.tools.config as config
import openerp
from openerp import SUPERUSER_ID
from openerp.modules.registry import RegistryManager
import openerp.addons.web.controllers.main as db
import datetime
import logging
from openerp.tools.translate import _
from lxml import etree

_logger = logging.getLogger(__name__)
class WebClient(http.Controller):
    @http.route("/web/api/99bill/mas/",type="http",auth="none")
    def get_mas(self,**kw):
        _logger.warn(kw)
        return "0"