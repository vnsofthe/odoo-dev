# coding:utf-8
import xmlrpclib
import os, time

#os.system('service odoo restart')
time.sleep(5)
s_username = 'demo'  # OpenERP 登陆用户
#s_pwd = 'admin'      # 登陆密码
#s_dbname = "Odoo80_140917"    # OpenERP 帐套
#s_url= "http://www.osbzr.net:8899"
s_pwd = 'demo'
s_dbname = 'Manual'
s_url = 'http://odoo9.yuandeyun.com/'

t_username = 'admin'  # OpenERP 登陆用户
t_pwd = '123'  # 登陆密码
t_dbname = "odoo9"  # OpenERP 帐套
t_url = "http://127.0.0.1:8099"
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

ids = s_sock.execute_kw(s_dbname, s_uid, s_pwd, 'ir.translation', 'search', [[("lang", "=", "zh_CN")]])

print "Rows count:%s" % (ids.__len__())
for i in ids:
    try:
        data = s_sock.execute_kw(s_dbname, s_uid, s_pwd, 'ir.translation', 'read', [i])
    except:
        continue
    s_ids = t_sock.execute_kw(t_dbname, t_uid, t_pwd, 'ir.translation', 'search',
                           [[("lang", "=", "zh_CN"), ("src", "=", data['src']),
                            ("display_name", "=", data['display_name']), ("name", "=", data['name']),
                            ("type", "=", data['type']), ("module", "=", data['module'])]])
    if not s_ids:
        s_ids = t_sock.execute_kw(t_dbname, t_uid, t_pwd, 'ir.translation', 'search',
                               [[("lang", "=", "zh_CN"), ("src", "=", data['src']), ("type", "=", data['type'])]])
    if not s_ids:
        s_ids = t_sock.execute_kw(t_dbname, t_uid, t_pwd, 'ir.translation', 'search',
                               [[("lang", "=", "zh_CN"), ("src", "=", data['src'])]])
    if s_ids:
        #s_data['value'] = s_data['value'].replace(u"公司", u"医院").replace(u"产品", u"物料")
        val = {
            "state":data["state"],
            "value":data["value"]
        }

        try:
            t_sock.execute_kw(t_dbname, t_uid, t_pwd, 'ir.translation', 'write', [s_ids,val])
        except Exception,e:
            print "=======write error", data,s_ids,val,e
    else:
        pass#print "search error:", data

print "end:", time.strftime("%Y-%m-%d %H:%M:%S")
