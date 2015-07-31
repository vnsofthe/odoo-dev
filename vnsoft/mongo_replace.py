# -*- coding: utf-8 -*-
import pymongo
import re

DB_SERVER="10.0.0.8"
DB_PORT = 27021
DB_NAME = "susceptibility"

conn = pymongo.Connection(DB_SERVER,DB_PORT)
db = conn[DB_NAME]
content = db.prodata.find() #取套餐数据

def str_replace(s,first,sencond):
    v = s.split(first)
    if len(v)>1:
        for k in v:
            pass
def dict_show(val):
    for k,v in val.items():
        if k in ("pic","snpids"):continue

        if isinstance(v,(dict,)):
            dict_show(v)
        elif isinstance(v,(int,long)):
            continue
        else:
            if v.count(";")>0 or v.count(u"；")>0:
                print k,v

for i in content:
    dict_show(i)