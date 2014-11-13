# coding:utf-8
import xmlrpclib
import os, time

os.system('service odoo restart')
time.sleep(5)
s_username = 'admin'  # OpenERP 登陆用户
#s_pwd = 'admin'      # 登陆密码
#s_dbname = "Odoo80_140917"    # OpenERP 帐套
#s_url= "http://www.osbzr.net:8899"
s_pwd = '123456'
s_dbname = 'dev'
s_url = 'http://localhost:8069'

t_username = 'admin'  # OpenERP 登陆用户
t_pwd = '123456'  # 登陆密码
t_dbname = "dev"  # OpenERP 帐套
t_url = "http://localhost:8069"
print "start:", time.strftime("%Y-%m-%d %H:%M:%S")
# Get the uid
s_sock_common = xmlrpclib.ServerProxy(s_url + '/xmlrpc/common')
s_uid = s_sock_common.login(s_dbname, s_username, s_pwd)

#replace localhost with the address of the server
s_sock = xmlrpclib.ServerProxy(s_url + '/xmlrpc/object')

# Get the uid
t_sock_common = xmlrpclib.ServerProxy(t_url + '/xmlrpc/common')
t_uid = t_sock_common.login(t_dbname, t_username, t_pwd)

#replace localhost with the address of the server
t_sock = xmlrpclib.ServerProxy(t_url + '/xmlrpc/object')

ids = t_sock.execute(t_dbname, t_uid, t_pwd, 'ir.translation', 'search', [("lang", "=", "zh_CN")])
print "Rows count:%s" % (ids.__len__())
for i in ids:
    data = t_sock.execute(t_dbname, t_uid, t_pwd, 'ir.translation', 'read', i, [])  #ids is a list of id
    #if data['value']!='' and  data['src']!=data['value']:continue
    s_ids = s_sock.execute(s_dbname, s_uid, s_pwd, 'ir.translation', 'search',
                           [("lang", "=", "zh_CN"), ("src", "=", data['src']),
                            ("display_name", "=", data['display_name']), ("name", "=", data['name']),
                            ("type", "=", data['type']), ("module", "=", data['module'])])
    if not s_ids:
        s_ids = s_sock.execute(s_dbname, s_uid, s_pwd, 'ir.translation', 'search',
                               [("lang", "=", "zh_CN"), ("src", "=", data['src']), ("type", "=", data['type'])])
    if not s_ids:
        s_ids = s_sock.execute(s_dbname, s_uid, s_pwd, 'ir.translation', 'search',
                               [("lang", "=", "zh_CN"), ("src", "=", data['src'])])
    if s_ids:
        s_data = s_sock.execute(s_dbname, s_uid, s_pwd, 'ir.translation', 'read', s_ids[0], [])
        s_data['value'] = s_data['value'].replace(u"公司", u"医院").replace(u"产品", u"物料")
        if data['value'] != s_data['value']:
            data['state'] = s_data['state']
            data['value'] = s_data['value']
            try:
                t_sock.execute(t_dbname, t_uid, t_pwd, 'ir.translation', 'write', i, data)
            except:
                print "write error", data
    else:
        print "search error:", data

print "end:", time.strftime("%Y-%m-%d %H:%M:%S")
