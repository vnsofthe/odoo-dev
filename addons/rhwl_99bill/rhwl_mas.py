# -*- coding: utf-8 -*-

from openerp import http
from openerp.http import request
from openerp.osv import fields, osv
from openerp.addons.base.res.res_users import res_users
import json,simplejson
import openerp.tools.config as config
import openerp
from openerp import SUPERUSER_ID
from openerp.modules.registry import RegistryManager
import openerp.addons.web.controllers.main as db
import datetime
import logging

class rhwl_mas(osv.osv):
    _name = "rhwl.99bill.mas"
    _columns={
        "process_flag":fields.boolean(u"处理结果"),
        "txn_type":fields.selection([("PUR",u"消费交易"),("INP",u"分期消费交易"),("PRE",u"预授权交易"),("CFM",u"预授权完成交易"),("VTX",u"撤销交易"),("RFD",u"退货交易"),("00201",u"冲正交易")],u"交易类型"),
        "org_txn_type":fields.selection([("PUR",u"消费交易"),("INP",u"分期消费交易"),("PRE",u"预授权交易"),("CFM",u"预授权完成交易"),("VTX",u"撤销交易"),("RFD",u"退货交易"),("00201",u"冲正交易")],u"原始交易类型"),
        "amt":fields.float(u"交易金额"),
        "external_trace_no":fields.char(u"样本编号",size=50),
        "org_external_trace_no":fields.char(u"原始样本编号",size=50),
        "terminal_oper_id":fields.char(u"操作员编号",size=20),
        "terminal_id":fields.char(u"终端编号",size=20),
        "authcode":fields.char(u"授权码",size=10),
        "rrn":fields.char(u"系统参考号",size=20),
        "txn_time":fields.char(u"交易时间",size=15),
        "txntime":fields.datetime(u"交易时间"),
        "short_pan":fields.char(u"缩略卡号",size=10),
        "response_code":fields.char(u"交易返回码",size=3),
        "response_message":fields.char(u"交易返回信息",size=256),
        "card_type":fields.selection([("0000",u"银行卡"),("0001",u"信用卡"),("0002",u"借记卡"),("0003",u"私有卡（包含快钱卡和储值卡）")],u"卡类型"),
        "issuer_id":fields.char(u"发卡机构",size=10),
        "issuer_id_view":fields.char(u"发卡机构名称",size=128),
        "merchant_id":fields.char(u"商户编号",size=20),
        "signature":fields.char("signature")
    }
