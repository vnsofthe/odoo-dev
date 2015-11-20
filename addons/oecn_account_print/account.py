# -*- encoding: utf-8 -*-
# __author__ = jeff@openerp.cn
from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp import tools
import openerp.addons.decimal_precision as dp

import logging

_logger = logging.getLogger(__name__)


class account_move(osv.osv):
    _inherit = 'account.move'
    """
    添加制单、审核、附件数三个字段
    """
    _columns = {
        'write_uid':fields.many2one('res.users', u'审核', readonly=True),
        'create_uid':fields.many2one('res.users', u'制单', readonly=True, select=True),
        'proof':fields.integer(u'附件数', required=False, help='该记账凭证对应的原始凭证数量'),
    }
    """
    附件数默认为1张
    凭证业务类型默认为总帐
    """
    _defaults = {
        'proof': lambda *args: 1,
        'journal_id': lambda self, cr, uid, context:self.pool.get('account.journal').search(cr, uid, [('type', '=', 'general')], limit=1)[0],
    }

class account_account(osv.osv):
    _inherit = 'account.account'

    def get_balance(self, cr, uid, ids, date_start=False, date_stop=False, product=False, partner=False ):
        '''
        Get the balance from date_start to date_stop,fielter by product or partner
        '''
        result = {
            'debit':0.0,
            'debit_quantity':0.0,
            'debit_amount_currency':0.0,
            'credit':0.0,
            'credit_quantity':0.0,
            'credit_amount_currency':0.0,
            'balance':0.0,
            'amount_currency':0.0,
            'quantity':0.0,
        }
        account_move_line_obj = self.pool.get('account.move.line')
        journal_obj = self.pool.get('account.journal')
        account_obj = self.pool.get('account.account')

        journal_ids = journal_obj.search(cr, uid, [('type','!=','situation')])
        account_ids = account_obj.search(cr, uid, [('parent_id', 'child_of', ids)])
        search_condition = [('account_id','in',account_ids),('state','=','valid'),('journal_id','in',journal_ids)]
        if date_start:
            search_condition.append(('date', '>=', date_start))
        if date_stop:
            search_condition.append(('date', '<=', date_stop))
        if product:
            search_condition.append(('product_id', '=', product[0]))
        if partner:
            search_condition.append(('partner_id', '=', partner[0]))

        line_ids = account_move_line_obj.search(cr, uid, search_condition)
        lines = account_move_line_obj.browse(cr, uid, line_ids)
        for line in lines:
            if line.debit > 0:
                result['debit_quantity'] += line.quantity or 0
                result['debit_amount_currency'] += line.amount_currency or 0
            else:
                result['credit_quantity'] += line.quantity or 0
                result['credit_amount_currency'] += abs(line.amount_currency) or 0
            result['balance'] += line.debit-line.credit
            result['quantity'] =  result['debit_quantity'] - result['credit_quantity']
            result['amount_currency'] =  result['debit_amount_currency'] - result['credit_amount_currency']
            result['debit'] += line.debit or 0
            result['credit'] += line.credit or 0

        return result

class account_periodly(osv.osv):
    _name = "account.periodly"
    _description = "科目余额表"
    _auto = False

    def _compute_balances(self, cr, uid, ids, field_names, arg=None, context=None,
                  query='', query_params=()):
        all_periodly_lines = self.search(cr, uid, [], context=context)
        all_companies = self.pool.get('res.company').search(cr, uid, [], context=context)
        all_accounts = self.pool.get('account.account').search(cr, uid, [], context=context)
        current_sum = dict((company, dict((account, 0.0) for account in all_accounts)) for company in all_companies)
        res = dict((id, dict((fn, 0.0) for fn in field_names)) for id in all_periodly_lines)
        for record in self.browse(cr, uid, all_periodly_lines, context=context):
            res[record.id]['starting_balance'] = current_sum[record.company_id.id][record.account_id.id]
            current_sum[record.company_id.id][record.account_id.id] += record.balance
            res[record.id]['ending_balance'] = current_sum[record.company_id.id][record.account_id.id]
        return res

    _columns = {
        'fiscalyear_id': fields.many2one('account.fiscalyear', 'Fiscalyear', readonly=True),
        'period_id': fields.many2one('account.period', '期间', readonly=True),
        'account_id':fields.many2one('account.account','科目',readonly=True),
        'debit': fields.float('借方', readonly=True),
        'credit': fields.float('贷方', readonly=True),
        'balance': fields.float('Balance', readonly=True),
        'date': fields.date('Beginning of Period Date', readonly=True),
        'starting_balance': fields.function(_compute_balances, digits_compute=dp.get_precision('Account'), string='期初余额', multi='balance'),
        'ending_balance': fields.function(_compute_balances, digits_compute=dp.get_precision('Account'), string='期末余额', multi='balance'),
        'company_id': fields.many2one('res.company', 'Company', readonly=True),
    }

    _order = 'date asc,account_id,company_id'


    def init(self, cr):
        tools.drop_view_if_exists(cr, 'account_periodly')
        cr.execute("""
            create or replace view account_periodly as (
            select
                min(l.id) as id,
                p.fiscalyear_id as fiscalyear_id,
                p.id as period_id,
                l.account_id as account_id,
                sum(l.debit) as debit,
                sum(l.credit) as credit,
                sum(l.debit-l.credit) as balance,
                p.date_start as date,
                am.company_id as company_id
            from
                account_move_line l
                left join account_account a on (l.account_id = a.id)
                left join account_move am on (am.id=l.move_id)
                left join account_period p on (am.period_id=p.id)
            where l.state != 'draft'
            group by p.id, l.account_id, p.fiscalyear_id, p.date_start, am.company_id
            )
        """)
