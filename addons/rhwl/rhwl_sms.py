#codeing=utf-8
import requests

arg={
    "id":"vnsoft",
    "pwd":"rhwl2015",
    "to":"",
    "content":'',
    "time":None
}
"""000/Send:1/Consumption:.1/Tmoney:.4/sid:1121102038224252"""
def send_sms(tel,text):
    #s=requests.post('http://service.winic.org/sys_port/gateway/?id=vnsoft&pwd=10261121sms&to=18657130579&content=%s&time='
    arg['to']=tel
    arg['content']=text.encode('gb2312')
    s=requests.post("http://service.winic.org/sys_port/gateway/",params=arg)
    ref = s.content
    s.close()
    return ref

