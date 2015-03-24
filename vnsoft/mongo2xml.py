#!/usr/bin/python
# -*- coding: utf-8 -*-
#from lxml import etree
import pymongo
try:
    import xml.etree.cElementTree as etree
except ImportError:
    import xml.etree.ElementTree as etree
import os
import base64

def str2trans(s):
    return s and s.replace("%","{\%}").replace("\n","\n\n") or ""
    
def lang2file(name,d):
    lang = etree.Element(name)
    if d.get("diagnose",{}).get("header")>"" or d.get("diagnose",{}).get("description")>"":
        diagnose=etree.SubElement(lang,"diagnose")
    if d.get("diagnose",{}).get("header")>"":
        etree.SubElement(diagnose,"header").text=str2trans(d.get("diagnose",{}).get("header"))
    if d.get("diagnose",{}).get("description")>"":
        etree.SubElement(diagnose,"description").text=str2trans(d.get("diagnose",{}).get("description"))

    if d.get("nutrition",{}).get("header") or d.get("nutrition",{}).get("description") or d.get("nutrition",{}).get("compound",[]):
        nutrition=etree.SubElement(lang,"nutrition")
    if d.get("nutrition",{}).get("header"):
        etree.SubElement(nutrition,"header").text=str2trans(d.get("nutrition",{}).get("header"))
    if d.get("nutrition",{}).get("description"):
        etree.SubElement(nutrition,"description").text=str2trans(d.get("nutrition",{}).get("description"))
    if d.get("nutrition",{}).get("compound",[]):
        for i in d.get("nutrition",{}).get("compound",[]):
            if i.get("name") or i.get("function"):
                compound=etree.SubElement(nutrition,"compound")
            if i.get("name"):
                etree.SubElement(compound,"header").text=str2trans(i.get("name"))
            if i.get("function"):
                etree.SubElement(compound,"function").text=str2trans(i.get("function"))
    if d.get("pic",{}).get("base64",""):
        pic=etree.SubElement(lang,"pic")
        pic.text=d.get("pic",{}).get("base64","")
    if d.get("title"):
        title=etree.SubElement(lang,"title")
        title.text=str2trans(d.get("title"))
    if d.get("ngenetic",{}).get("header") or d.get("ngenetic",{}).get("description"):
        ngenetic=etree.SubElement(lang,"ngenetic")
        if d.get("ngenetic",{}).get("header"):
            etree.SubElement(ngenetic,"header").text=str2trans(d.get("ngenetic",{}).get("header"))
        if d.get("ngenetic",{}).get("description"):
            etree.SubElement(ngenetic,"description").text=str2trans(d.get("ngenetic",{}).get("description"))
    if d.get("genetic",{}).get("header") or d.get("genetic",{}).get("description"):
        genetic=etree.SubElement(lang,"genetic")
    if d.get("genetic",{}).get("header"):
        etree.SubElement(genetic,"header").text=str2trans(d.get("genetic",{}).get("header"))
    if d.get("genetic",{}).get("description"):
        etree.SubElement(genetic,"description").text=str2trans(d.get("genetic",{}).get("description"))
    if d.get("clinical",{}).get("header") or d.get("clinical",{}).get("description"):
        clinical=etree.SubElement(lang,"clinical")
    if d.get("clinical",{}).get("header"):
        etree.SubElement(clinical,"header").text=str2trans(d.get("clinical",{}).get("header"))
    if d.get("clinical",{}).get("description"):
        etree.SubElement(clinical,"description").text=str2trans(d.get("clinical",{}).get("description"))
    if d.get("suggestion",{}).get("header") or d.get("suggestion",{}).get("description"):
        suggestion=etree.SubElement(lang,"suggestion")
    if d.get("suggestion",{}).get("header"):
        etree.SubElement(suggestion,"header").text=str2trans(d.get("suggestion",{}).get("header"))
    if d.get("suggestion",{}).get("description"):
        etree.SubElement(suggestion,"description").text=str2trans(d.get("suggestion",{}).get("description"))
    if d.get("report",{}).get("header") or d.get("report",{}).get("level0") or d.get("report",{}).get("level1") or d.get("report",{}).get("level2") or d.get("report",{}).get("level3") or d.get("report",{}).get("level4"):
        report=etree.SubElement(lang,"report")
    if d.get("report",{}).get("header"):
        etree.SubElement(report,"header").text=str2trans(d.get("report",{}).get("header"))
    if d.get("report",{}).get("level0"):
        etree.SubElement(report,"level0").text=str2trans(d.get("report",{}).get("level0"))
    if d.get("report",{}).get("level1"):
        etree.SubElement(report,"level1").text=str2trans(d.get("report",{}).get("level1"))
    if d.get("report",{}).get("level2"):
        etree.SubElement(report,"level2").text=str2trans(d.get("report",{}).get("level2"))
    if d.get("report",{}).get("level3"):
        etree.SubElement(report,"level3").text=str2trans(d.get("report",{}).get("level3"))
    if d.get("report",{}).get("level4"):
        etree.SubElement(report,"level4").text=str2trans(d.get("report",{}).get("level4"))
    if d.get("desc",{}).get("header") or d.get("desc",{}).get("description"):
        desc=etree.SubElement(lang,"desc")
    if d.get("desc",{}).get("header"):
        etree.SubElement(desc,"header").text=str2trans(d.get("desc",{}).get("header"))
    if d.get("desc",{}).get("description"):
        etree.SubElement(desc,"description").text=str2trans(d.get("desc",{}).get("description"))
    
    return lang


def dict2file(d):
    if not d.has_key("_id"):return
    opt = etree.Element("opt")
    id = etree.SubElement(opt, "id").text=d.get("_id")
    
    for l in ["CN","EN"]:
        if not d.get(l,{}):continue
        lang=lang2file(l,d.get(l,{}))
        pic=lang.findall("pic")
        if pic and pic[0].text:
            pic_base64 = pic[0].text
            imgname=l+"/pic/section_"+d.get("_id").replace(" ","")+"."+(d.get(l).get("pic").get("mimetype").split("/")[1])
            fimg = open(imgname,"wb")
            #base64.decode(pic_base64,fimg)
            fimg.write(pic_base64.decode('base64','strict'))
            fimg.close()
            pic[0].text=imgname.split('/')[2]
        opt.insert(0,lang)

        f=open(l+"/section/section_"+d.get("_id").replace(" ","")+".xml","w")
        f.write(etree.tostring(opt, encoding="utf-8", method="xml"))
        f.close()
        opt.remove(lang)
    
    
    
def check_dir():
    if not os.path.exists("EN"):
        os.mkdir("EN")
        os.mkdir("EN/pic")
        os.mkdir("EN/section")
    else:
        if not os.path.exists("EN/pic"):
            os.mkdir("EN/pic")
        if not os.path.exists("EN/section"):
            os.mkdir("EN/section")
    if not os.path.exists("CN"):
        os.mkdir("CN")
        os.mkdir("CN/pic")
        os.mkdir("CN/section")
    else:
        if not os.path.exists("CN/pic"):
            os.mkdir("CN/pic")
        if not os.path.exists("CN/section"):
            os.mkdir("CN/section")

            
if __name__=="__main__":
    check_dir()
    conn = pymongo.Connection("10.0.0.8",27017)
    db = conn.disease 
    content = db.disease.find()
    for i in content:
        dict2file(i)
