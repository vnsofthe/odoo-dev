# coding:utf-8
import xmlrpclib
import os, time


s_username = 'admin'  # OpenERP 登陆用户
s_pwd = '123asdqwe'
s_dbname = 'erpdb'
s_url = 'http://111.203.21.78:8069'

print "start:", time.strftime("%Y-%m-%d %H:%M:%S")
# Get the uid
s_sock_common = xmlrpclib.ServerProxy(s_url + '/xmlrpc/common')
s_uid = s_sock_common.login(s_dbname, s_username, s_pwd)
#replace localhost with the address of the server
s_sock = xmlrpclib.ServerProxy(s_url + '/xmlrpc/object')

import csv

reader = csv.reader(file('D:\\TDDOWNLOAD\\item_catalog.csv', 'rb'))
for line in reader:
    #print line
    vals={
			"default_code":line[1],
			"characteristic":line[2],
			"classify":line[3],
			"description":line[4],
			"name":line[5],
			"specification":line[8],
			"url":line[11],
			"vendor":line[12],
			"type":'product'
		}
		#id,catalog_no,characteristic,classify,description,name_cn,name_en,note,specification,state,storage,url,vendor,ciq_id,hs_id
    s_sock.execute(s_dbname,s_uid,s_pwd,"product.template","create",vals)

print "end:", time.strftime("%Y-%m-%d %H:%M:%S")
