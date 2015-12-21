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
    "name" : "自动创建订货点",
    "version" : "1.8",
    "description" : '''
     在创建产品后，用户需要手工创建自动订货点，这样才是使用“按库存量补货”的规则。
     为了避免在mrp运行时才提示遗漏了此信息，我们为每个新建的产品都创建一个订货点。
     如果产品是“按单补货”,订货点并非必需，但有它也不影响逻辑，所以此方案也适用。
    ''',
    "author" : "开阖软件 jeff@osbzr.com",
    "website" : "http://www.osbzr.com",
    "depends" : ['stock'],
    "data" : [],
    "installable" : True,
    "certificate" : "",
    'auto_install': False,
    "category":'Warehouse Management'
}
