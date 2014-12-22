# coding:utf-8
import xmlrpclib
import os, time


s_username = 'admin'  # OpenERP 登陆用户
s_pwd = '123'
s_dbname = 'test'
s_url = 'http://localhost:8069'

print "start:", time.strftime("%Y-%m-%d %H:%M:%S")
# Get the uid
s_sock_common = xmlrpclib.ServerProxy(s_url + '/xmlrpc/common')
s_uid = s_sock_common.login(s_dbname, s_username, s_pwd)
#replace localhost with the address of the server
s_sock = xmlrpclib.ServerProxy(s_url + '/xmlrpc/object')

t_sock_common = xmlrpclib.ServerProxy('http://120.24.58.11:8069/xmlrpc/common')
t_uid = t_sock_common.login("dev", "admin", "123456")
#replace localhost with the address of the server
t_sock = xmlrpclib.ServerProxy('http://120.24.58.11:8069/xmlrpc/object')

ids = s_sock.execute(s_dbname, s_uid, s_pwd, 'rhwl.import.temp', 'search', [])

for i in ids:
   rows = s_sock.execute(s_dbname, s_uid, s_pwd, 'rhwl.import.temp', 'read', i,[])
   print rows
   cate_id = t_sock.execute("dev", t_uid, "123456", 'product.category', 'search', [("name","ilike",rows.get("col1")+"-")])
   if not cate_id:
       cate_id = t_sock.execute("dev", t_uid, "123456", 'product.category', 'create', {"name":rows.get("col1"),"parent_id":1})
   if isinstance(cate_id,(list,tuple)):
       cate_id = cate_id[0]
   product_id = t_sock.execute("dev", t_uid, "123456", 'product.template', 'search', [("name","=",rows.get("col2"))])
   if not product_id:
       product_id = t_sock.execute("dev", t_uid, "123456", 'product.template', 'create', {"name":rows.get("col2"),"sale_ok":False,"type":"product","brand":rows.get("col3"),"default_code":rows.get("col4"),"categ_id":cate_id,"standard_price":rows.get("col6"),"qty_available":rows.get("col7")})
   else:
       t_sock.execute("dev", t_uid, "123456", 'product.template', 'write',product_id,{"brand":rows.get("col3"),"default_code":rows.get("col4"),"categ_id":cate_id,"standard_price":rows.get("col6"),"qty_available":rows.get("col7")})

print "end:", time.strftime("%Y-%m-%d %H:%M:%S")
