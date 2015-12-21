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
    "name" : "Setting access for price fields",
    "version" : "1.8",
    "description" : '''
     产品价格是公司的关键隐私数据，针对企业内部，也要严格控制哪些用户只能看到产品的销售价格，哪些用户只能看到产品的采购价格
     本模块新增了两个角色，【读取销售价】 和【读取采购价】，并在产品的相应界面上做了限制。只有在这个组的用户才可以看到这个字段。
    使用方法：通过菜单“设置→用户→用户组”，分别向这两个组“允许查看产品销售价” 和“允许查看产品成本价”里面填加需要相应权限的用户。
    ''',
    "author" : "开阖软件 jeff@osbzr.com",
    "website" : "http://www.osbzr.com",
    "depends" : ['stock_account'],
    "data" : [
              'security/osbzr_show_price_security.xml',
              'osbzr_show_price_view.xml',
              ],
    "installable" : True,
    "certificate" : "",
    'auto_install': False,
    "category":'Generic Modules/Others'
}
