# -*- coding: utf-8 -*-
import pymongo

conn = pymongo.Connection("10.0.0.8",27017)
db1 = conn.topic #连接库
db2 = conn.character

content = db2.character.find()
#for i in
