#!/usr/bin/python
# -*- coding: utf-8 -*-
import suds

BODY="""
<Request service='OrderService' lang='zh-CN'>
<Head>RHWLSW,iuGAN2Ib44IHkk8R</Head><Body>
<Order orderid='XJFS_07110001'
              express_type='1'
              j_company='人和未来生物科技(长沙)有限公司'
              j_contact='发货组'
              j_tel='0731-89703873'
              j_mobile='18657130579'
              j_province='湖南省'
              j_city='长沙市'
              j_county='岳麓区'
              j_address='麓谷企业广场C2栋1101'
              d_company='顺丰速运'
              d_contact='小顺'
              d_tel='0755-33992159'
              d_mobile='15602930913'
              d_province='广东省'
              d_city='深圳市'
              d_county='福田区'
              d_address='广东省深圳市福田区新洲十一街万基商务大厦10楼'
              parcel_quantity='1'
              pay_method='1'
              custid='7310713279'
              cargo_total_weight='2.18'
              sendstarttime='2014-07-11 12:07:11'
              remark='' >
       <Cargo name='采血包装袋' count='10' unit='袋' weight='2.36' amount='2000' currency='CNY' source_area='中国'></Cargo>
</Order>
</Body>
</Request>
"""
url = 'http://bsp-oisp.test.sf-express.com:6080/bsp-oisp/ws/expressService?wsdl'

def get_e_express(vals):
    client = suds.client.Client(url)
    service = client.service
    sum_result = service.sfexpressService(BODY.decode('utf-8'))
    client.last_received()
    return sum_result