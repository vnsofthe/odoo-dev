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
    "name" : "发送不抄送关注者的消息",
    "version" : "1.8",
    "description" : '''
    OpenERP的两个程序员分别在8.0的两个commit中里去掉了这个功能的入口。至今未修复。
    
         为了不影响10.0beta版的开发进度，我们写个模块实现它。
    ''',
    "author" : "开阖软件 jeff@osbzr.com",
    "website" : "http://www.osbzr.com",
    "depends" : ['mail'],
    "data" : [
              'osbzr_private_mail_view.xml',
              ],
    "installable" : True,
    "certificate" : "",
    'auto_install': False,
    "category":'Generic Modules/Others'
}
