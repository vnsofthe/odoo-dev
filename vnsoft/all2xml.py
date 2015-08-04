#!/usr/bin/python
# -*- coding: utf-8 -*-
#from lxml import etree
import pymongo
try:
    import xml.etree.cElementTree as etree
except ImportError:
    import xml.etree.ElementTree as etree
import os,sys
import base64
import Image
import re
def str2trans(s):
    if not s:return ""
    if isinstance(s,(long,int,float)):s=str(s)
    s = s.replace("%","{\%}").replace("\n","\n\n").replace(u"Ⅰ","\\RNum{1}").replace(u"Ⅱ","\\RNum{2}").replace(u"Ⅲ","\\RNum{3}").replace(u"Ⅳ","\\RNum{4}").replace(u"Ⅴ","\\RNum{5}").replace(u"Ⅵ","\\RNum{6}").replace(u"Ⅶ","\\RNum{7}").replace(u"Ⅷ","\\RNum{8}").replace(u"Ⅸ","\\RNum{9}").replace(u"Ⅹ","\\RNum{10}").replace(u"Ⅺ","\\RNum{11}").replace(u"Ⅻ","\\RNum{12}").replace(u"ⅩⅢ","\\RNum{13}").replace(u"α", "\\textalpha ").replace(u"β", "\\textbeta ").replace(u"γ", "\\textgamma ").replace(u"μ", "\\textmu ").replace(u"δ", "\\textdelta ").replace(u"κ", "\\textkappa ").replace(u"≥","$\\geq$").replace(u"≤", "$\\leq$").replace(u"~", "\\textasciitilde ")
    rgx = re.findall("\^(\D+)", s)
    for rg in rgx:
        s = s.replace("^", "\\^{}")
    rgx = re.findall("\^(\d+)", s)
    for rg in rgx:
        ori = "^" + rg
        nwi = "$^{" + rg + "}$"
#        print ori
#        print nwi
        s = s.replace(ori, nwi)
    return s
	#.replace("%","{\%}").replace("\n","\n\n").replace(u"Ⅰ","\\RNum{1}").replace(u"Ⅱ","\\RNum{2}").replace(u"Ⅲ","\\RNum{3}").replace(u"Ⅳ","\\RNum{4}").replace(u"Ⅴ","\\RNum{5}").replace(u"Ⅵ","\\RNum{6}").replace(u"Ⅶ","\\RNum{7}").replace(u"Ⅷ","\\RNum{8}").replace(u"Ⅸ","\\RNum{9}").replace(u"Ⅹ","\\RNum{10}").replace(u"Ⅺ","\\RNum{11}").replace(u"Ⅻ","\\RNum{12}").replace(u"ⅩⅢ","\\RNum{13}").replace(u"α", "\\textalpha ").replace(u"β", "\\textbeta ").replace(u"γ", "\\textgamma ").replace(u"μ", "\\textmu ").replace(u"δ", "\\textdelta ").replace(u"κ", "\\textkappa ").replace(u"≥","$\\geq$").replace(u"≤", "$\\leq$").replace(u"~", "\\textasciitilde ").replace(u"10^9/L", "10$^{9}$/L").replace(u"^2", "$^{2}$").replace(u"^3", "$^{3}$")
	#.replace(u"Ⅰ","I").replace(u"Ⅲ","III").replace(u"Ⅱ","II").replace(u"Ⅳ","IV").replace(u"Ⅵ","VI").replace(u"Ⅶ","VII").replace(u"Ⅸ","IX").replace(u"Ⅺ","XI").replace(u"β","beta")
    
def image_resize(f):
    img = Image.open(f)
    width,height = img.size
    if width>250 or height>250:
        if width>height:
            newbox=(250, 250 * height / width)
        else:
            newbox=(250*width/height, 250)
        targetImg = img.resize(
                           newbox,
                           Image.ANTIALIAS
                           )
    else:
        targetImg = img.resize((width,height),Image.ANTIALIAS)

    os.remove(f)
    new=".".join(f.split(".")[:-1])+".jpg"
    if f.split(".")[-1]=='gif':targetImg =targetImg.convert("RGB")
    targetImg.save(new, "jpeg")
    return new

def dict2file(pd,pm,lang):
    if not pd.has_key("_id"):return
    opt = etree.Element("opt")
    etree.SubElement(opt, "id").text=pd.get("_id")
    lang_element = etree.SubElement(opt, lang)
    check_dir(os.path.join(sys.argv[5],pd["category"]))
    l_path = check_dir(os.path.join(os.path.join(sys.argv[5],pd["category"]),lang)) #判断目录是否存在

    for l in pm:
        for k,v in l.items():
            if k=="sex":
                etree.SubElement(lang_element,k).text=str2trans(pd[k])
            elif k=="pic":
                pic_path= os.path.join(l_path,"pic")
                check_dir(pic_path)
                if  pd.get(lang).get("pic",{}).get("base64"):
                    imgname= pic_path+"/section_"+pd.get("_id").replace("'","").replace("`","").replace(" ","")+"."+(pd.get(lang).get("pic").get("mimetype").split("/")[1])
                    fimg = open(imgname,"wb")
                    pic_base64 = pd.get(lang).get("pic").get("base64")
                    fimg.write(pic_base64.decode('base64','strict'))
                    fimg.close()
                    etree.SubElement(lang_element,"pic").text=image_resize(imgname).split('/')[-1]
                else:
                    etree.SubElement(lang_element,"pic")
            elif isinstance(v,(type(u""),)):
                etree.SubElement(lang_element,k).text=str2trans(pd[lang][k])
            elif isinstance(v,(list,)):
                ele = etree.SubElement(lang_element,k)
                for e in v:
                    if e.has_key("node"):continue
                    etree.SubElement(ele,e.keys()[0]).text = str2trans(pd.get(lang,{}).get(k,{}).get(e.keys()[0],""))
    xml_path= os.path.join(l_path,"section")
    check_dir(xml_path)
    f=open(xml_path+"/section_"+pd.get("_id").replace("'","").replace("`","").replace(" ","")+".xml","w")
    f.write(etree.tostring(opt, encoding="utf-8", method="xml"))
    f.close()

    
def check_dir(path_name):
    if not os.path.exists(path_name):
        os.makedirs(path_name)
    return path_name

if __name__=="__main__":
    if(len(sys.argv)!=6):
        print "参数不正确。\n格式：命令 客户 语言 套系 套餐 输出目录"
        sys.exit(-1)

    conn = pymongo.Connection("10.0.0.8",27021)
    db = conn.susceptibility
    content = db.products.find({"belongsto":sys.argv[1].decode("utf-8")})

    for i in content:

        if not i.get(sys.argv[2].decode("utf-8")):
            continue #如果语言不匹配，则不处理
        if(i[sys.argv[2].decode("utf-8")]["name"]!=sys.argv[3].decode("utf-8")):
            continue #如果套系名称不匹配，则不处理
        for k,v in i[sys.argv[2].decode("utf-8")]["sets"].items():
            if(v["name"]!=sys.argv[4].decode("utf-8")):
                continue#如果套餐不匹配，则不处理
            for k1,v1 in v["list"].items():
                pd = db.prodata.find_one({"_id":v1})
                pagemode = pd.get("pagemode")
                pm = db.pagemodes.find_one({"_id":pagemode})
                dict2file(pd,pm.get("itms"),sys.argv[2].decode("utf-8"))

