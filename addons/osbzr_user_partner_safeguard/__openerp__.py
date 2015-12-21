# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-Today 上海开阖软件有限公司 (<http://www.osbzr.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': '阻止越权修改用户信息',
    'category': 'osbzr',
    'summary': '阻止普通用户越权修改用户信息',
    'version': '1.0',
    'description': """https://github.com/odoo/odoo/issues/8751 此bug的patch，
                                                       如用户没有权限则会在保存时报错""",
    'author': '开阖软件Jeff Wang',
    'depends': ['base'],
    'data': [],
    'installable': True,
    'auto_install': False,
}
