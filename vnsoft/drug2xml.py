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

not_export_id=['Elavil','Tryptanol','Endep','Elatrol','Tryptizol','Trepiline','Laroxyl']

def str2trans(s):
    if not s:return ""
    return s.replace("%","{\%}").replace("\n","\n\n").replace("Ⅰ","I").replace("Ⅲ","III").replace("Ⅱ","II").replace("Ⅳ","IV").replace("Ⅵ","VI").replace("Ⅶ","VII").replace("Ⅸ","IX").replace("β","beta")
    
def lang2file(name,d):
    lang = etree.Element(name)
    diagnose=etree.SubElement(lang,"desc")
    etree.SubElement(diagnose,"header").text=str2trans(d.get("desc",{}).get("header"))
    etree.SubElement(diagnose,"description").text=str2trans(d.get("desc",{}).get("description"))
    nutrition=etree.SubElement(lang,"note")
    etree.SubElement(nutrition,"header").text=str2trans(d.get("note",{}).get("header"))
    etree.SubElement(nutrition,"description").text=str2trans(d.get("note",{}).get("description"))

    generelations=etree.SubElement(lang,"generelations")
    etree.SubElement(generelations,"description").text=str2trans(d.get("generelations",{}).get("description"))

    pic=etree.SubElement(lang,"pic")
    pic.text=d.get("pic",{}).get("base64","")
    title=etree.SubElement(lang,"title")
    title.text=str2trans(d.get("title"))

    return lang

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
    new=f.split(".")[0]+".jpg"
    targetImg.save(new, "jpeg")
    return new

def dict2file(d):
    if not d.has_key("_id"):return

    if not_export_id.count(d.get("_id"))>0:return

    opt = etree.Element("opt")
    id = etree.SubElement(opt, "id").text=d.get("_id")
    
    for l in ["CN","EN"]:
        if not d.get(l,{}).get("desc",{}).get("description"):continue
        if not d.get(l,{}).get("note",{}).get("description"):continue
        lang=lang2file(l,d.get(l,{}))
        pic=lang.findall("pic")
        if pic and pic[0].text:
            pic_base64 = pic[0].text
            imgname=l+"/pic/section_"+d.get("_id").replace("'","").replace("`","").replace(" ","").replace("/","_")+"."+(d.get(l).get("pic").get("mimetype").split("/")[1])
            fimg = open(imgname,"wb")
            #base64.decode(pic_base64,fimg)
            fimg.write(pic_base64.decode('base64','strict'))
            fimg.close()

            pic[0].text=image_resize(imgname).split('/')[2]
        opt.insert(0,lang)

        f=open(l+"/section/section_"+d.get("_id").replace("'","").replace("`","").replace(" ","").replace("/","_")+".xml","w")
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
    db = conn.medicine
    content = db.medicine.find()
    for i in content:
        dict2file(i)
