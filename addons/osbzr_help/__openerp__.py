#-*- encoding: utf-8 -*-
# __author__ = jeff@osbzr.com
##############################################################################
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

{
    "name" : "Get help from osbzr",
    "version" : "1.8",
    "description" : '''
    在每个表单界面的左上角增加了帮助按钮。
    在每个模块的名称后增加了帮助按钮
    
    帮助按钮会根据您当前所处页面打开对应的开阖软件wiki页面
    我们会有专人负责实时更新这些页面
    
    ''',
    "author" : "开阖软件 jeff@osbzr.com",
    "website" : "http://www.osbzr.com",
    "depends" : ['web'],
    "data" : ['osbzr_help_view.xml'],
    "installable" : True,
    "qweb":[
        "static/src/xml/osbzr_help.xml",
    ],
    "certificate" : "",
    'auto_install': True,
    "category":'Generic Modules/Others'
}
