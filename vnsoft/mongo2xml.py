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
import Image
def str2trans(s):
    return s and s.replace("%","{\%}").replace("\n","\n\n") or ""
    
def lang2file(name,d):
    lang = etree.Element(name)
    diagnose=etree.SubElement(lang,"diagnose")
    etree.SubElement(diagnose,"header").text=str2trans(d.get("diagnose",{}).get("header"))
    etree.SubElement(diagnose,"description").text=str2trans(d.get("diagnose",{}).get("description"))
    nutrition=etree.SubElement(lang,"nutrition")
    etree.SubElement(nutrition,"header").text=str2trans(d.get("nutrition",{}).get("header"))
    etree.SubElement(nutrition,"description").text=str2trans(d.get("nutrition",{}).get("description"))
    for i in d.get("nutrition",{}).get("compound",[]):
        compound=etree.SubElement(nutrition,"compound")
        etree.SubElement(compound,"header").text=str2trans(i.get("name"))
        etree.SubElement(compound,"function").text=str2trans(i.get("function"))

    pic=etree.SubElement(lang,"pic")
    pic.text=d.get("pic",{}).get("base64","")
    title=etree.SubElement(lang,"title")
    title.text=str2trans(d.get("title"))
    ngenetic=etree.SubElement(lang,"ngenetic")
    etree.SubElement(ngenetic,"header").text=str2trans(d.get("ngenetic",{}).get("header"))
    etree.SubElement(ngenetic,"description").text=str2trans(d.get("ngenetic",{}).get("description"))

    genetic=etree.SubElement(lang,"genetic")
    etree.SubElement(genetic,"header").text=str2trans(d.get("genetic",{}).get("header"))
    etree.SubElement(genetic,"description").text=str2trans(d.get("genetic",{}).get("description"))

    clinical=etree.SubElement(lang,"clinical")
    etree.SubElement(clinical,"header").text=str2trans(d.get("clinical",{}).get("header"))
    etree.SubElement(clinical,"description").text=str2trans(d.get("clinical",{}).get("description"))

    suggestion=etree.SubElement(lang,"suggestion")
    etree.SubElement(suggestion,"header").text=str2trans(d.get("suggestion",{}).get("header"))
    etree.SubElement(suggestion,"description").text=str2trans(d.get("suggestion",{}).get("description"))
    report=etree.SubElement(lang,"report")
    etree.SubElement(report,"header").text=str2trans(d.get("report",{}).get("header"))
    etree.SubElement(report,"level0").text=str2trans(d.get("report",{}).get("level0"))
    etree.SubElement(report,"level1").text=str2trans(d.get("report",{}).get("level1"))
    etree.SubElement(report,"level2").text=str2trans(d.get("report",{}).get("level2"))
    etree.SubElement(report,"level3").text=str2trans(d.get("report",{}).get("level3"))
    etree.SubElement(report,"level4").text=str2trans(d.get("report",{}).get("level4"))
    desc=etree.SubElement(lang,"desc")
    etree.SubElement(desc,"header").text=str2trans(d.get("desc",{}).get("header"))
    etree.SubElement(desc,"description").text=str2trans(d.get("desc",{}).get("description"))
    
    return lang

def image_resize(f):
    img = Image.open(f)
    width,height = img.size
    if width>220:
        targetImg = img.resize(
                           (220, 220 * height / width),
                           Image.ANTIALIAS
                           )
    else:
        targetImg = img.resize((width,height),Image.ANTIALIAS)

    os.remove(f)
    new=f.split(".")[0]+".jpg"
    targetImg.save(new, "jpeg")
    return new

def dict2file(d):
    if not d.has_key("_id"):return
    opt = etree.Element("opt")
    id = etree.SubElement(opt, "id").text=d.get("_id")
    
    for l in ["CN","EN"]:
        if not d.get(l,{}).get("desc",{}).get("description"):continue
        lang=lang2file(l,d.get(l,{}))
        pic=lang.findall("pic")
        if pic and pic[0].text:
            pic_base64 = pic[0].text
            imgname=l+"/pic/section_"+d.get("_id").replace("'","").replace("`","").replace(" ","")+"."+(d.get(l).get("pic").get("mimetype").split("/")[1])
            fimg = open(imgname,"wb")
            #base64.decode(pic_base64,fimg)
            fimg.write(pic_base64.decode('base64','strict'))
            fimg.close()

            pic[0].text=image_resize(imgname).split('/')[2]
        opt.insert(0,lang)

        f=open(l+"/section/section_"+d.get("_id").replace("'","").replace("`","").replace(" ","")+".xml","w")
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
    os.system("rm -Rf CN/pic/*.*")
    os.system("rm -Rf CN/section/*.*")
    os.system("rm -Rf EN/pic/*.*")
    os.system("rm -Rf EN/section/*.*")
            
if __name__=="__main__":
    check_dir()
    conn = pymongo.Connection("10.0.0.8",27017)
    db = conn.disease 
    content = db.disease.find()
    for i in content:
        dict2file(i)
