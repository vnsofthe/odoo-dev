# coding:utf-8

import requests
import time
import xmlrpclib

s_username = 'admin'  # OpenERP 登陆用户
s_pwd = '123456'
s_dbname = 'dev'
s_url = 'http://120.24.58.11:8069'

# Get the uid
s_sock_common = xmlrpclib.ServerProxy(s_url + '/xmlrpc/common')
s_uid = s_sock_common.login(s_dbname, s_username, s_pwd)

#replace localhost with the address of the server
s_sock = xmlrpclib.ServerProxy(s_url + '/xmlrpc/object')

def imp(arg1,arg2,arg3):
    global s_sock,s_dbname,s_uid,s_pwd
    ids = s_sock.execute(s_dbname, s_uid, s_pwd, 'res.country.state', 'search', [('name','=',arg1)])
    if not ids:
        print u"省"+arg1
        return
    ids2 = s_sock.execute(s_dbname, s_uid, s_pwd, 'res.country.state.city', 'search', [('name','=',arg2),("state_id","=",ids[0])])
    if not ids2:
        ids2 = s_sock.execute(s_dbname, s_uid, s_pwd, 'res.country.state.city', 'create', {'name':arg2,"state_id":ids[0]})
    if isinstance(ids2,(list,tuple)):
        ids2 = ids2[0]
    ids3 = s_sock.execute(s_dbname, s_uid, s_pwd, 'res.country.state.city.area', 'search', [('name','=',arg3),("city_id","=",ids2)])
    if not ids3:
        s_sock.execute(s_dbname, s_uid, s_pwd, 'res.country.state.city.area', 'create', {'name':arg3,"city_id":ids2})

req = requests.post("http://api.dangqian.com/apidiqu2/api.asp?format=json&id=000000000000&callback=dict")
no1 = req.content
no1 = eval(no1)
for k,v in no1.get("list").items():
    daima1 = v.get("daima").decode("utf-8").encode("gbk")

    req2 = requests.post("http://api.dangqian.com/apidiqu2/api.asp?format=json&id="+daima1+"&callback=dict")
    no2 = req2.content
    no2 = eval(no2)
    for k2,v2 in no2.get("list").items():
        daima2 = v2.get("daima").decode("utf-8").encode("gbk")

        req3 = requests.post("http://api.dangqian.com/apidiqu2/api.asp?format=json&id="+daima2+"&callback=dict")
        no3 = req3.content
        no3 = eval(no3)
        print daima2
        for k3,v3 in  no3.get("list").items():
            imp(no3.get("diming2").decode("utf-8"),no3.get("diming3").decode("utf-8"),v3.get("diming").decode("utf-8"))
