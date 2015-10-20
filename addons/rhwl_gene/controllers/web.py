# -*- coding: utf-8 -*-

from openerp import http
import hashlib
from lxml import etree
from openerp.http import request
from openerp.modules.registry import RegistryManager
from openerp import SUPERUSER_ID
import time
import base64
import datetime,json
import cStringIO
import StringIO
import Image
import logging
import os
import openerp
import openerp.tools.config as config
import shutil
_logger = logging.getLogger(__name__)
content_m={"0":[("前言",1,1),("致辞",2,2),("个人信息",3,3),("基因检测报告的说明",8),("综合评估和指导建议",13),("遗传易感性评估及结果分析",35),("附录",273)],
           "8":[("服务项目介绍",8,8),("检测报告解读示例",9,12)],
           "13":[("肿瘤专项疾病预防",14),("代谢与营养能力疾病预防",19),("心脑血管疾病预防",23),("呼吸、消化、泌尿系统疾病预防",27),("皮肤、肌肉和骨关节疾病预防",31),("精神和行为障碍疾病预防",34)],
           "14":[("高危警示",14,14),("易感性综合评估",15,16),("环境风险因素分析与指导",17,18)],
           "19":[("高危警示",19,19),("易感性综合评估",20,21),("环境风险因素分析与指导",22,22)],
           "23":[("高危警示",23,23),("易感性综合评估",24,24),("环境风险因素分析与指导",25,26)],
           "27":[("高危警示",27,27),("易感性综合评估",28,28),("环境风险因素分析与指导",29,30)],
           "31":[("高危警示",31,31),("易感性综合评估",32,32),("环境风险因素分析与指导",33,33)],
           "34":[("易感性综合评估",34,34)],
           "35":[("肿瘤大类",36),("肿瘤大类推荐保健产品",109,109),("代谢与营养",110),
                    ("代谢与营养推荐保健产品",164,164),("心脑血管疾病",165),
                    ("心脑血管疾病推荐保健产品",206,206),("呼吸、消化、泌尿系统疾病",207),
                    ("呼吸、消化、泌尿系统疾病推荐保健产品",254,254),("皮肤、肌肉和骨关节疾病",255),("皮肤、肌肉和骨关节疾病推荐保健产品",265,265),("精神和行为障碍",266),("精神和行为障碍推荐保健产品",272,272)],
           "36":[("鼻咽癌",36,39),("食管癌",40,44),("胃癌",45,49),("小肠癌",50,52),("结肠癌",53,57),("大肠癌",58,60),("肝癌",61,64),("胆囊癌",65,69),
                    ("胆管癌",70,72),("胰腺癌",73,76),("肺癌",77,80),("黑色素瘤",81,83),("肾癌",84,86),("膀胱癌",87,91),("脑胶质瘤",92,94),("甲状腺癌",95,97),("霍奇金病",98,100),("急性髓系白血病",101,104),("前列腺癌",105,108),
                ],
           "110":[("贫血",110,112),("系统性红斑狼疮",113,115),("Ⅰ型糖尿病",116,118),("Ⅱ型糖尿病",119,122),
                    ("维生素A/C/E代谢",123,126),("维生素B6/12及叶酸代谢",127,129),("维生素D代谢",130,132),
                    ("单纯性肥胖",133,135),("能量代谢",136,139),("钙代谢紊乱",140,143),("磷吸收",144,147),
                    ("铅中毒",148,150),("黄曲霉素代谢",151,153),("紫外线损伤修复",154,156),("胆固醇代谢",157,159),
                    ("自由基代谢及氧化损伤修复",160,163),
                    ],
           "165":[("帕金森氏综合症",165,167),("阿茨海默症",168,171),("多发性硬化",172,175),("风湿性心脏病",176,178),
                    ("高血压",179,182),("心绞痛",183,185),("心肌梗死",186,188),("房颤",189,191),("脑梗死",192,194),
                    ("中风",195,198),("动脉粥样硬化",199,202),("深静脉血栓",203,205),],
           "207":[("哮喘",207,209),("过敏性鼻炎",210,212),("鼻息肉",213,215),("克隆氏病",216,219),
                    ("酒精性肝硬化",220,222),("原发性胆汁性肝硬化",223,225),("脂肪肝",226,228),("胆石症",229,231),
                    ("牙周炎",232,235),("食管炎",236,238),("胃溃疡",239,242),("十二指肠溃疡",243,246),
                    ("慢性萎缩性胃炎",247,250),("肾结石",251,253),],
           "255":[("类风湿性关节炎",255,258),("强直性脊柱炎",259,261),("骨质疏松",262,264),],
           "266":[("酒精中毒",266,268),("酒精成瘾",269,271),],
           "273":[("承诺与声明",273,273),("泰济生国际医院介绍",274,275)]
}
content_m_title={
    "0":"样本目录",
    "8":"报告说明",
    "13":"评估建议",
    "14":"肿瘤疾病预防",
    "19":"代谢与营养",
    "23":"心血管疾病",
    "27":"呼吸消化泌尿",
    "31":"皮肤肌肉关节",
    "34":"精神和行为障碍",
    "35":"易感性评估分析",
    "36":"肿瘤大类",
    "110":"代谢与营养",
    "165":"心脑血管疾病",
    "207":"呼吸消化泌尿",
    "255":"皮肤肌肉关节",
    "266":"精神和行为障碍",
    "273":"附录"
}

content_f={"0":[("前言",1,1),("致辞",2,2),("个人信息",3,3),("基因检测报告的说明",8),("综合评估和指导建议",13),("遗传易感性评估及结果分析",35),("附录",273)],
           "8":[("服务项目介绍",8,8),("检测报告解读示例",9,12)],
           "13":[("肿瘤专项疾病预防",14),("代谢与营养能力疾病预防",19),("心脑血管疾病预防",23),("呼吸、消化、泌尿系统疾病预防",27),("皮肤、肌肉和骨关节疾病预防",31),("精神和行为障碍疾病预防",34)],
           "14":[("高危警示",14,14),("易感性综合评估",15,16),("环境风险因素分析与指导",17,18)],
           "19":[("高危警示",19,19),("易感性综合评估",20,21),("环境风险因素分析与指导",22,22)],
           "23":[("高危警示",23,23),("易感性综合评估",24,24),("环境风险因素分析与指导",25,26)],
           "27":[("高危警示",27,27),("易感性综合评估",28,28),("环境风险因素分析与指导",29,30)],
           "31":[("高危警示",31,31),("易感性综合评估",32,32),("环境风险因素分析与指导",33,33)],
           "34":[("易感性综合评估",34,34)],
           "35":[("肿瘤大类",36),("肿瘤大类推荐保健产品",121,121),("代谢与营养",122),
                    ("代谢与营养推荐保健产品",176,176),("心脑血管疾病",177),
                    ("心脑血管疾病推荐保健产品",218,218),("呼吸、消化、泌尿系统疾病",219),
                    ("呼吸、消化、泌尿系统疾病推荐保健产品",266,266),("皮肤、肌肉和骨关节疾病",267),("皮肤、肌肉和骨关节疾病推荐保健产品",277,277),("精神和行为障碍",278),("精神和行为障碍推荐保健产品",284,284)],
           "36":[("鼻咽癌",36,39),("食管癌",40,44),("胃癌",45,49),("小肠癌",50,52),("结肠癌",53,57),("大肠癌",58,60),("肝癌",61,64),("胆囊癌",65,69),
                    ("胆管癌",70,72),("胰腺癌",73,76),("肺癌",77,80),("黑色素瘤",81,83),("肾癌",84,86),("膀胱癌",87,91),("脑胶质瘤",92,94),("甲状腺癌",95,97),
                    ("霍奇金病",98,100),("急性髓系白血病",101,104),("乳腺癌",105,107),("宫颈癌",108,113),("子宫内膜癌",114,116),("卵巢癌",117,120),
                ],
           "122":[("贫血",122,124),("系统性红斑狼疮",125,127),("Ⅰ型糖尿病",128,130),("Ⅱ型糖尿病",131,134),
                    ("维生素A/C/E代谢",135,138),("维生素B6/12及叶酸代谢",139,141),("维生素D代谢",142,144),
                    ("单纯性肥胖",145,147),("能量代谢",148,151),("钙代谢紊乱",152,155),("磷吸收",156,159),
                    ("铅中毒",160,162),("黄曲霉素代谢",163,165),("紫外线损伤修复",166,168),("胆固醇代谢",169,171),
                    ("自由基代谢及氧化损伤修复",172,175),
                    ],
           "177":[("帕金森氏综合症",177,179),("阿茨海默症",180,183),("多发性硬化",184,187),("风湿性心脏病",188,190),
                    ("高血压",191,194),("心绞痛",195,197),("心肌梗死",198,200),("房颤",201,203),("脑梗死",204,206),
                    ("中风",207,210),("动脉粥样硬化",211,214),("深静脉血栓",215,217),],
           "219":[("哮喘",219,221),("过敏性鼻炎",222,224),("鼻息肉",225,227),("克隆氏病",228,231),
                    ("酒精性肝硬化",232,234),("原发性胆汁性肝硬化",235,237),("脂肪肝",238,240),("胆石症",241,243),
                    ("牙周炎",244,247),("食管炎",248,250),("胃溃疡",251,254),("十二指肠溃疡",255,258),
                    ("慢性萎缩性胃炎",259,262),("肾结石",263,265),],
           "267":[("类风湿性关节炎",267,270),("强直性脊柱炎",271,273),("骨质疏松",274,276),],
           "278":[("酒精中毒",278,280),("酒精成瘾",281,283),],
           "285":[("承诺与声明",285,285),("泰济生国际医院介绍",286,287)]

}
content_f_title={
    "0":"样本目录",
    "8":"报告说明",
    "13":"评估建议",
    "14":"肿瘤疾病",
    "19":"代谢与营养",
    "23":"心血管疾病",
    "27":"呼吸消化泌尿",
    "31":"皮肤肌肉关节",
    "34":"精神和行为障碍",
    "35":"易感性评估分析",
    "36":"肿瘤大类",
    "122":"代谢与营养",
    "177":"心脑血管疾病",
    "219":"呼吸消化泌尿",
    "267":"皮肤肌肉关节",
    "278":"精神和行为障碍",
    "285":"附录"
}
class gene(http.Controller):
    CONTEXT={'lang': "zh_CN",'tz': "Asia/Shanghai"}

    def get_dbname(self):
        if config.get('api_db'):
            dname = config['api_db']
        else:
            db_names = openerp.service.db.exp_list(True)
            dname = db_names[0]
        return dname and dname or None

    def check_userinfo(self,kw=None):
        if request.httprequest.data or kw:
            data = {}
            if request.httprequest.data:
                data = json.loads(request.httprequest.data)
            if kw:
                data.update(kw)
                #data = json.JSONEncoder.encode(json.loads(kw))
            if data.get("openid",'0')=='0' and not (data.get('Username') and data.get('Pwd')):
                res={
                    "statu":500,
                    "errtext":u"参数中无登录帐号和密码信息。"
                }
            else:
                if data.get("Username"):
                    DBNAME = self.get_dbname()
                    uid = request.session.authenticate(DBNAME,data.get('Username'),data.get('Pwd'))
                elif data.get("openid"):
                    registry = RegistryManager.get(request.session.db)
                    weixin = registry.get("rhwl.weixin")

                    with registry.cursor() as cr:
                        id = weixin.search(cr,SUPERUSER_ID,[('openid','=',data.get("openid"))],context=self.CONTEXT)
                        if id:
                            obj= weixin.browse(cr,SUPERUSER_ID,id,context=self.CONTEXT)
                            uid = obj.user_id.id

                if uid:
                    res={"statu":200,"userid":uid,"params":data}
                else:
                    res={
                        "statu":500,
                        "errtext":u"登录名与密码不正确。"
                    }
        else:
            res={
                "statu":500,
                "errtext":u"请传入验证参数"
            }
        return res

    @http.route("/web/api/gene/pic/",type="http",auth="user")
    def imagepost(self,**kw):
        registry = RegistryManager.get(request.session.db)
        obj = registry.get("rhwl.easy.genes")
        with registry.cursor() as cr:
            id = obj.search(cr,request.uid,[("name","=",kw.get("no"))])
            if not id:
                return "NO_DATA_FOUND"
            file_like = cStringIO.StringIO(kw.get("img1").split(";")[-1].split(",")[-1].decode('base64','strict'))
            img = Image.open(file_like)
            width,height = img.size
            file_like2 = cStringIO.StringIO(kw.get("img2").split(";")[-1].split(",")[-1].decode('base64','strict'))
            img2 = Image.open(file_like2)

            region = img2.crop((0,0,width/2,height))
            img.paste(region, (width/2, 0,width,height))
            val={"img":base64.encodestring(img.tostring("jpeg",img.mode))}
            if kw.get("etx",""):
                val["except_note"]=kw.get("etx")

            obj.write(cr,request.uid,id,val,context={'lang': "zh_CN",'tz': "Asia/Shanghai","name":kw.get("no")})
            if val.has_key("except_note") or kw.get("is_confirm")=="true":
                o=obj.browse(cr,request.uid,id,context={'lang': "zh_CN",'tz': "Asia/Shanghai"})
                if o.state=="draft":
                    if val.has_key("except_note"):
                        obj.action_state_except(cr,request.uid,id,context={'lang': "zh_CN",'tz': "Asia/Shanghai"})
                    elif kw.get("is_confirm")=="true":
                        obj.action_state_confirm(cr,request.uid,id,context={'lang': "zh_CN",'tz': "Asia/Shanghai"})


            return "OK"

    @http.route("/web/rhwl_gene/get/",type="http",auth="user")
    def get_detail(self,**kw):
        registry = RegistryManager.get(request.session.db)
        obj = registry.get("rhwl.easy.genes")
        sexdict={'T':u'男','F':u'女'}
        with registry.cursor() as cr:
            id = obj.search(cr,request.uid,[("name","=",kw.get("no"))])
            if not id:
                data={}
            else:
                res = obj.browse(cr,request.uid,id,context={'lang': "zh_CN",'tz': "Asia/Shanghai"})
                data={
                    "batch_no":res.batch_no,
                    "name":res.name,
                    "date":res.date,
                    "cust_name":res.cust_name,
                    "sex": sexdict.get(res.sex,""),
                    "identity":res.identity and res.identity or "",
                    "mobile":res.mobile and res.mobile or "",
                    "birthday":res.birthday and res.birthday or "",
                }

        response = request.make_response(json.dumps(data,ensure_ascii=False), [('Content-Type', 'application/json')])
        return response.make_conditional(request.httprequest)

    @http.route("/web/rhwl_gene/images/",type="http",auth="user")
    def index(self,**kw):
        fname = os.path.join(os.path.split(os.path.split(__file__)[0])[0],"static/webcam.html")
        f=open(fname,"r")
        html=f.readlines()
        f.close()
        return ''.join(html)
        return """<html><head><script>
                    window.location = '/rhwl_gene/static/webcam.html';
                </script></head></html>
                """

    @http.route("/web/api/genes/risk/",type="http",auth="none")
    def _get_rhwl_genes_risk(self,**kw):
        res = self.check_userinfo(kw)
        data = {}
        if res.get('statu')==200:
            registry = RegistryManager.get(request.session.db)
            with registry.cursor() as cr:
                risk = registry.get("rhwl.easy.gene.risk")
                id = risk.search(cr,SUPERUSER_ID,[("genes_id.name","=",res.get("params").get("id"))])
                if id:
                    for r in risk.browse(cr,SUPERUSER_ID,id):
                        data[r.disease_id.name]= r.risk
        else:
            data=res

        response = request.make_response(json.dumps(data,ensure_ascii=False), [('Content-Type', 'application/json')])
        return response.make_conditional(request.httprequest)

    @http.route("/web/api/genes/weixin/",type="http",auth="none")
    def _get_rhwl_api_weixin(self,**kw):
        res = self.check_userinfo(kw)
        data = {}
        if res.get('statu')==200:
            registry = RegistryManager.get(request.session.db)
            with registry.cursor() as cr:
                sample = registry.get("rhwl.easy.genes")
                log = registry.get("rhwl.easy.genes.log")
                id = sample.search(cr,SUPERUSER_ID,[("name","=",res.get("params").get("id"))])
                if id:
                    obj = sample.browse(cr,SUPERUSER_ID,id,context=self.CONTEXT)

                    data["name"] = obj.name.encode('utf-8')
                    data["stateList"]=[
                        ["收件","等待中",""],
                        ["送检","等待中",""],
                        ["质检","等待中",""],
                        ["出实验结果","等待中",""],
                        ["报告分析","等待中",""],
                		["出报告","等待中",""]
                    ]

                    log_id=registry.get("rhwl.easy.genes.batch").search(cr,SUPERUSER_ID,[("name","=",obj.batch_no)])
                    if log_id:
                        log_obj = registry.get("rhwl.easy.genes.batch").browse(cr,SUPERUSER_ID,log_id,context=self.CONTEXT)
                        if log_obj:
                            if log_obj.post_date:
                                data["stateList"][0][1]="完成"
                                data["stateList"][0][2]=log_obj.post_date.replace("-","/")
                            if log_obj.lib_date:
                                data["stateList"][1][1]="完成"
                                data["stateList"][1][2]=log_obj.lib_date.replace("-","/")
                    else:
                        log_id=log.search(cr,SUPERUSER_ID,[("genes_id","=",id[0]),("data","in",['except','except_confirm','confirm','img'])],order="date")
                        if log_id:
                            log_obj=log.browse(cr,SUPERUSER_ID,log_id[0],context=self.CONTEXT)
                            data["stateList"][0][1]="完成"
                            data["stateList"][0][2]=(datetime.datetime.strptime(log_obj.date,"%Y-%m-%d %H:%M:%S") + datetime.timedelta(hours=8)).strftime("%Y/%m/%d %H:%M:%S")

                    log_id=log.search(cr,SUPERUSER_ID,[("genes_id","=",id[0]),("data","in",['dna_except','dna_ok'])],order="date")
                    if log_id:
                        log_obj=log.browse(cr,SUPERUSER_ID,log_id[0],context=self.CONTEXT)
                        data["stateList"][2][1]="完成"
                        data["stateList"][2][2]=(datetime.datetime.strptime(log_obj.date,"%Y-%m-%d %H:%M:%S") + datetime.timedelta(hours=8)).strftime("%Y/%m/%d %H:%M:%S")

                    log_id=log.search(cr,SUPERUSER_ID,[("genes_id","=",id[0]),("data","in",['ok'])],order="date")
                    if log_id:
                        log_obj=log.browse(cr,SUPERUSER_ID,log_id[0],context=self.CONTEXT)
                        data["stateList"][3][1]="完成"
                        data["stateList"][3][2]=(datetime.datetime.strptime(log_obj.date,"%Y-%m-%d %H:%M:%S") + datetime.timedelta(hours=8)).strftime("%Y/%m/%d %H:%M:%S")

                    log_id=log.search(cr,SUPERUSER_ID,[("genes_id","=",id[0]),("data","in",['report'])],order="date")
                    if log_id:
                        log_obj=log.browse(cr,SUPERUSER_ID,log_id[0],context=self.CONTEXT)
                        data["stateList"][4][1]="完成"
                        data["stateList"][4][2]=(datetime.datetime.strptime(log_obj.date,"%Y-%m-%d %H:%M:%S") + datetime.timedelta(hours=8)).strftime("%Y/%m/%d %H:%M:%S")
                    log_id=log.search(cr,SUPERUSER_ID,[("genes_id","=",id[0]),("data","in",['report_done','result_done','deliver','done'])],order="date")
                    if log_id:
                        log_obj=log.browse(cr,SUPERUSER_ID,log_id[0],context=self.CONTEXT)
                        data["stateList"][5][1]="完成"
                        data["stateList"][5][2]=(datetime.datetime.strptime(log_obj.date,"%Y-%m-%d %H:%M:%S") + datetime.timedelta(hours=8)).strftime("%Y/%m/%d %H:%M:%S")
                cr.commit()
        else:
            data=res

        response = request.make_response(json.dumps(data,ensure_ascii=False), [('Content-Type', 'application/json')])
        return response.make_conditional(request.httprequest)

    @http.route("/web/api/genes/weixin/content/",type="http",auth="none")
    def _get_rhwl_api_weixin_content(self,**kw):
        res = self.check_userinfo(kw)
        data = {}
        tit=""
        if res.get('statu')==200:
            registry = RegistryManager.get(request.session.db)
            with registry.cursor() as cr:
                sample = registry.get("rhwl.easy.genes")
                id = sample.search(cr,SUPERUSER_ID,[("name","=",res.get("params").get("id"))])
                if id:
                    obj=sample.browse(cr,SUPERUSER_ID,id)
                    if obj.sex=="T":
                        data = content_m.get(str(res.get("params").get("seq")))
                        tit = content_m_title.get(str(res.get("params").get("seq")))
                    elif obj.sex=='F':
                        data = content_f.get(str(res.get("params").get("seq")))
                        tit = content_f_title.get(str(res.get("params").get("seq")))
        else:
            data=res

        response = request.make_response(json.dumps([tit,data],ensure_ascii=False), [('Content-Type', 'application/json')])
        return response.make_conditional(request.httprequest)

    @http.route("/web/api/genes/report/img/",type="http",auth="none")
    def _get_rhwl_api_report_img(self,**kw):
        res = self.check_userinfo(kw)
        data = []
        if res.get('statu')==200:
            registry = RegistryManager.get(request.session.db)
            with registry.cursor() as cr:
                sample = registry.get("rhwl.easy.genes")
                id = sample.search(cr,SUPERUSER_ID,[("name","=",res.get("params").get("id"))])
                if id:
                    obj=sample.browse(cr,SUPERUSER_ID,id)
                    png_path = os.path.join("/data/odoo/file/report",obj.name)
                    if not os.path.exists(png_path):
                        os.mkdir(png_path)
                    ps=int(res.get("params").get("ps"))
                    pe=int(res.get("params").get("pe"))
                    for i in range(ps,pe+1):
                        if not os.path.exists(os.path.join(png_path,"pg_"+str(i).zfill(4)+".pdf")):
                            shutil.copy(os.path.join("/data/odoo/file/report",obj.name+".pdf"),os.path.join(png_path,obj.name+".pdf"))
                            os.system("cd "+png_path+";pdftk "+obj.name+".pdf burst")
                        if not os.path.exists(os.path.join(png_path,"pg_"+str(i).zfill(4)+".png")):
                            os.system("cd "+png_path+";convert -density 100 pg_"+str(i).zfill(4)+".pdf pg_"+str(i).zfill(4)+".png")
                        data.append("/rhwl_gene/static/local/report/"+obj.name.encode("utf-8")+"/pg_"+str(i).zfill(4)+".png")

        else:
            data=res

        response = request.make_response(json.dumps(data,ensure_ascii=False), [('Content-Type', 'application/json')])
        return response.make_conditional(request.httprequest)

    @http.route("/web/view/pdf/",type="http",auth="user")
    def _view_pdf(self,**kw):
        fname = os.path.join(os.path.split(os.path.split(__file__)[0])[0],u"4-4_H_3499995128_黄斌_4-4_H_3499995412_白亚博_M.pdf")
        f=open(fname,"rb")
        html=f.read()
        f.close()

        response =  request.make_response(html, headers=[('Content-Type', 'application/pdf'), ('Content-Length', len(html))])
        response.headers.add('Content-Disposition', 'inline; filename=%s.pdf;' % "123")
        return response
# assume data contains your decoded image


