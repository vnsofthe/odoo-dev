#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os,sys

def monitor(app_name):
    pf ="/var/log/%s.lock"%(app_name)
    os.system("ps -A|grep %s>%s"% (app_name,pf))
    if not(os.path.getsize(pf)):
        os.system("service %s restart"%(app_name))
        os.system('curl -d "to=18657130579&content=%s restart&id=vnsoft&pwd=gamedemosms" "http://service.winic.org/sys_port/gateway/"'%(app_name,))
if __name__=="__main__":
    if len(sys.argv)==2:
        monitor(sys.argv[1])