#!/usr/bin/python
# -*- coding: utf-8 -*-
import suds

BODY="""
<Request service='OrderService' lang='zh-CN'>
<Head>RHWLSW,iuGAN2Ib44IHkk8R</Head><Body>
<Order        express_type='1'
              j_company='人和未来生物科技(长沙)有限公司'
              j_contact='发货组'
              j_tel='0731-89703873'
              j_mobile='18657130579'
              j_province='湖南省'
              j_city='长沙市'
              j_county='岳麓区'
              j_address='麓谷企业广场C2栋1101'
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
       <Cargo name='%s'></Cargo>
</Order>
</Body>
</Request>
"""
url = 'http://bsp-oisp.test.sf-express.com:6080/bsp-oisp/ws/expressService?wsdl'

def get_e_express(vals):
    print vals
    body = BODY.decode("utf-8") % (vals[0],vals[1],vals[2],vals[3],vals[4],vals[5],vals[6],vals[7],str(vals[8]),vals[9],vals[10])
    client = suds.client.Client(url)
    service = client.service
    sum_result = service.sfexpressService(body)
    client.last_received()
    return sum_result