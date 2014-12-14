# -*- encoding: utf-8 -*-
# __author__ = jeff@openerp.cn;joshua@openerp.cn
# __thanks__ = [oldrev@gmail.com]
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from  openerp.osv import osv, fields
from openerp.tools.translate import _
import logging

_logger = logging.getLogger(__name__)

class detail_ledger(osv.osv_memory):
    '''
    Cash journal,Foreign currency journal,Stock ledger,Three columns ledger
    '''
    _name = 'detail.ledger'
    _descript = 'Detail Ledger(Cash journal, Foreign Currency journal, Stock Ledger, Three columns ledger)'
    _columns = {
        'account_id':fields.many2one('account.account', 'Account', required=True, domain=[('type','!=','view')]),
        'company_id':fields.many2one('res.company', 'Company', required=True),
        'period_from':fields.many2one('account.period', 'Period From', required=True, domain=[('special','=',False)]),
        'period_to':fields.many2one('account.period', 'Period To', required=True, domain=[('special','=', False)]),
        'partner':fields.many2one('res.partner', 'Partner'),
        'product':fields.many2one('product.product','Product'),
    }

    def _get_period_from(self, cr, uid, data, context=None):
        ids = self.pool.get('account.period').find(cr, uid, context=context)
        fiscalyear_id = self.pool.get('account.period').browse(cr, uid, ids[0]).fiscalyear_id
        cr.execute(("SELECT date_start ,fiscalyear_id,id "\
                "FROM account_period "\
                "WHERE fiscalyear_id='%s' and special = 'False' "\
                "ORDER BY date_start asc ")% (int(fiscalyear_id)))
        res = cr.dictfetchall()
        return res[0]['id']

    _defaults = {
        'company_id':lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'account.account', context=c),
        'period_to':lambda s, cr, uid, c:s.pool.get('account.period').find(cr, uid, context={'account_period_prefer_normal':True})[0],
        'period_from':_get_period_from
    }

    def print_report(self, cr, uid, ids, context=None):
        """
        Check account type to know which format should be #print
        1. Account code start with '1001' or '1002', with currency, #print currency cash journal
        2. Account code start with '1001' or '1002', without currency, #print cash journal
        3. If user input product, #print stock ledger
        4. If user didn't input product, #print three columns ledger
        """
        datas = self.read(cr, uid, ids[0], ['account_id','period_from','period_to','product','partner','company_id'], context=context)

        datas['ids'] = [datas['account_id'][0]]
        account = self.pool.get('account.account').browse(cr, uid, datas['account_id'][0], context=context)
        if(account.code[0:4] == '1001' or account.code[0:4] == '1002'):
            datas['account_code'] = account.code[0:4]
            if(account.currency_id):
                report_name = 'oecn_account_print.report_currency_cash_journal'
            else:
                report_name = 'oecn_account_print.report_cash_journal'
        elif datas.get('product', False):
            report_name =  'oecn_account_print.report_stock_ledger'
        else:
            report_name = 'oecn_account_print.report_threecolumns_ledger'
        datas['report_name'] = report_name
        #数据必须放在datas[‘form’]中，因为几个报表使用的是同一个类里面的方法解析，必须保证格式统一
        datas.update({'form': datas.copy() })
        datas['form'].update({'ids': datas['ids']})
        #返回的格式变了
        return self.pool['report'].get_action(cr, uid, ids, report_name, data=datas, context=context)
        #return {
                #'type':'ir.actions.report.xml',
                #'report_name':report_name,
                #'datas':datas
        #}


detail_ledger()

class general_ledger(osv.osv_memory):
    '''
    General Ledger
    '''
    _name = 'general.ledger'
    _description = 'General Ledger'
    _columns = {
        'account_ids':fields.many2many('account.account', 'general_ledger_account_account_rel','general_ledger_id','account_id', 'Account', required=True, domain=[('type','!=','view')]),
        'company_id':fields.many2one('res.company', 'Company', required=True),
        'period_from':fields.many2one('account.period', 'Period From', required=True, domain=[('special','=',False)]),
        'period_to':fields.many2one('account.period', 'Period To', required=True, domain=[('special','=',False)]),
    }

    def print_report(self, cr, uid, ids, context=None):
        res = self.read(cr, uid, ids[0], ['account_ids','company_id','period_from','period_to'])
        datas = {
            'ids':res['account_ids'],
            'model': 'account.account',
            'form': res,
        }
        #datas = {'ids':res['account_ids'],'company_id':res['company_id'],'period_from':res['period_from'],'period_to':res['period_to']}
        datas['form']['ids'] = datas['ids']
        return self.pool['report'].get_action(cr, uid, ids, 'oecn_account_print.report_general_ledger', data=datas,  context=context)

    def _get_period_from(self, cr, uid, data, context=None):
        period_obj = self.pool.get('account.period')
        ids = period_obj.find(cr, uid, context=context)
        fiscalyear_id = period_obj.browse(cr, uid, ids[0]).fiscalyear_id.id
        period_ids = period_obj.search(cr, uid, [('special','=','False'),('fiscalyear_id','=',fiscalyear_id)],order='date_start asc')
        #cr.execute(("SELECT date_start ,fiscalyear_id,id "\
                #"FROM account_period "\
                #"WHERE fiscalyear_id='%s' and special = 'False' "\
                #"ORDER BY date_start asc ")% (int(fiscalyear_id)))
        #res = cr.dictfetchall()
        return period_ids[0]

    _defaults = {
        'company_id':lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'account.account', context=c),
        'period_to':lambda s, cr, uid, c:s.pool.get('account.period').find(cr, uid, context={'account_period_prefer_normal':True})[0],
        'period_from':_get_period_from
    }

general_ledger()
# vim:expandtab:smartindent:tabstop=4;softtabstop=4;shiftwidth=4;

