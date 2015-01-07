#!/usr/bin/python
# -*- coding: utf-8 -*-
import suds

BODY="""
<Request service='OrderService' lang='zh-CN'>
<Head>rhwlswkj,N7rU89emENtDzJeUJKnk2QJ3nYT6I27E</Head><Body>
<Order        express_type='%s'
              j_company='%s'
              j_contact='%s'
              j_tel='%s'
              j_mobile='%s'
              j_province='%s'
              j_city='%s'
              j_county='%s'
              j_address='%s'
              d_company='%s'
              d_contact='%s'
              d_tel='%s'
              d_mobile='%s'
              d_province='%s'
              d_city='%s'
              d_county='%s'
              d_address='%s'
              parcel_quantity='1'
              pay_method='1'
              custid='7310713279'
              cargo_total_weight='%s'
              remark=''
              orderid='%s'>
       <Cargo name='%s' count='%s'></Cargo>
</Order>
</Body>
</Request>
"""

ROUTE="""<Request service='RouteService' lang='zh-CN'>
<Head>rhwlswkj,N7rU89emENtDzJeUJKnk2QJ3nYT6I27E</Head>
<Body>
<RouteRequest tracking_type='1'  method_type='1' tracking_number='%s' />
</Body>
</Request>"""

#url = 'http://bsp-oisp.test.sf-express.com:6080/bsp-oisp/ws/expressService?wsdl'
url = "http://bsp-oisp.sf-express.com/bsp-oisp/ws/expressService?wsdl"
def get_e_express(vals,devals):
    body = BODY.decode("utf-8") % (vals[0],devals[0],devals[1],devals[2],devals[3],devals[4],devals[5],devals[6],devals[7],vals[1],vals[2],vals[3],vals[4],vals[5],vals[6],vals[7],vals[8],str(vals[9]),vals[10],vals[11],vals[12])
    if vals[0]=="12":
        body = body.replace("remark=''","remark='' temp_range='1' ")
    client = suds.client.Client(url)
    service = client.service
    sum_result = service.sfexpressService(body)
    client.last_received()
    return sum_result

def get_route(no):
    body = ROUTE.decode("utf-8") % (no,)
    client = suds.client.Client(url)
    service = client.service
    sum_result = service.sfexpressService(body)
    client.last_received()
    return sum_result