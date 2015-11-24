# -*- coding: utf-8 -*-
# author: cysnake4713
#
from openerp.report import report_sxw
from openerp.tools.translate import _
from openerp.osv import osv

from openerp.addons.account.report.account_financial_report import report_account_common


class report_account_pal(report_account_common):
    def get_lines(self, data):
        lines = []
        ids2 = self.pool.get('account.financial.report')._get_children_by_order(self.cr, self.uid, [data['form']['account_report_id'][0]],
                                                                                context=data['form']['used_context'])
        total_value = 0.0
        total_debit = 0.0
        total_credit = 0.0
        total_cmp = 0.0
        extend_id_list = self.pool.get('account.financial.report').get_external_id(self.cr, self.uid, ids2)
        for report in self.pool.get('account.financial.report').browse(self.cr, self.uid, ids2, context=data['form']['used_context']):
            vals = {
                'e_id': extend_id_list[report.id],
                'name': report.name,
                'balance': report.balance * report.sign or 0.0,
                'type': 'report',
                'level': bool(report.style_overwrite) and report.style_overwrite or report.level,
                'account_type': report.type == 'sum' and 'view' or False,  # used to underline the financial report balances
                'plus_word': '',
            }
            if data['form']['debit_credit']:
                vals['debit'] = report.debit
                vals['credit'] = report.credit
            if data['form']['enable_filter']:
                vals['balance_cmp'] = self.pool.get('account.financial.report').browse(self.cr, self.uid, report.id, context=data['form'][
                    'comparison_context']).balance * report.sign or 0.0
            if vals['level'] == 1:
                total_value += vals['balance'] * report.sign
                if data['form']['debit_credit']:
                    total_debit += vals['debit'] * report.sign
                    total_credit += vals['credit'] * report.sign
                if data['form']['enable_filter']:
                    total_cmp += vals['balance_cmp'] * report.sign

            # process print value
            e_id = vals['e_id'].split('.')
            # add 减
            if len(e_id) == 2 and e_id[1] in ['financial_report_pal_2', 'financial_report_pal_24', 'financial_report_pal_31']:
                vals['plus_word'] = u'减:'
            # add 加
            if len(e_id) == 2 and e_id[1] in ['financial_report_pal_20', 'financial_report_pal_22', 'financial_report_pal_31']:
                vals['plus_word'] = u'加:'
            # add 其中
            if len(e_id) == 2 and e_id[1] in ['financial_report_pal_4', 'financial_report_pal_12', 'financial_report_pal_15',
                                              'financial_report_pal_19', 'financial_report_pal_23', 'financial_report_pal_25']:
                vals['plus_word'] = u'其中:'
            # 序号:
            if len(e_id) == 2 and e_id[1] in ['financial_report_pal_1']:
                vals['plus_word'] = u'一:'
            if len(e_id) == 2 and e_id[1] in ['financial_report_pal_21']:
                vals['plus_word'] = u'二:'
                vals['balance'] = total_value * -1
                if data['form']['enable_filter']:
                    vals['balance_cmp'] = total_cmp * -1
            if len(e_id) == 2 and e_id[1] in ['financial_report_pal_30']:
                vals['plus_word'] = u'三:'
                vals['balance'] = total_value * -1
                if data['form']['enable_filter']:
                    vals['balance_cmp'] = total_cmp * -1
            if len(e_id) == 2 and e_id[1] in ['financial_report_pal_32']:
                vals['plus_word'] = u'四:'
                vals['balance'] = total_value * -1
                if data['form']['enable_filter']:
                    vals['balance_cmp'] = total_cmp * -1

            lines.append(vals)

        return lines


class report_account_aab(report_account_pal):
    def get_lines(self, data):
        ids2 = self.pool.get('account.financial.report')._get_children_by_order(self.cr, self.uid, [data['form']['account_report_id'][0]],
                                                                                context=data['form']['used_context'])
        result = {'asset': [], 'liability': []}
        temp = result['asset']
        extend_id_list = self.pool.get('account.financial.report').get_external_id(self.cr, self.uid, ids2)
        for report in self.pool.get('account.financial.report').browse(self.cr, self.uid, ids2, context=data['form']['used_context']):
            vals = {
                'e_id': extend_id_list[report.id],
                'name': report.name,
                'balance': report.balance * report.sign or 0.0,
                'type': 'report',
                'level': bool(report.style_overwrite) and report.style_overwrite or report.level,
                'account_type': report.type == 'sum' and 'view' or False,  # used to underline the financial report balances
                'plus_word': '',
            }
            if data['form']['debit_credit']:
                vals['debit'] = report.debit
                vals['credit'] = report.credit
            if data['form']['enable_filter']:
                vals['balance_cmp'] = self.pool.get('account.financial.report').browse(self.cr, self.uid, report.id, context=data['form'][
                    'comparison_context']).balance * report.sign or 0.0
            e_id = vals['e_id'].split('.')
            if len(e_id) == 2 and e_id[1] in ['financial_report_aab_57']:
                temp = result['liability']
            temp.append(vals)

        return result


class report_pal_financial(osv.AbstractModel):
    _name = 'report.oecn_account_print.report_oe_cn_pal_financial'
    _inherit = 'report.abstract_report'
    _template = 'oecn_account_print.report_pal_financial'
    _wrapped_report_class = report_account_pal


class report_aab_financial(osv.AbstractModel):
    _name = 'report.oecn_account_print.report_oe_cn_aab_financial'
    _inherit = 'report.abstract_report'
    _template = 'oecn_account_print.report_aab_financial'
    _wrapped_report_class = report_account_aab
