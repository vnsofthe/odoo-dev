#coding:utf-8
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.platypus import *
from reportlab.lib.units import inch,mm
from reportlab.lib.enums import TA_JUSTIFY,TA_LEFT, TA_CENTER,TA_RIGHT
import copy
import reportlab.rl_config
reportlab.rl_config.warnOnMissingFontGlyphs = 0
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import fonts,colors

class rhwl(object):
    def export_pdf(self,risk_name,datas,footer_name,file_name):
        pdfmetrics.registerFont(TTFont('hei', '/usr/share/fonts/winfont/simkai.ttf'))

        fonts.addMapping('hei', 0, 0, 'hei')
        fonts.addMapping('hei', 0, 1, 'hei')

        stylesheet=getSampleStyleSheet()
        elements = []

        doc = SimpleDocTemplate(file_name,pagesize=A4,leftMargin=5*mm, rightMargin=5*mm,topMargin=0.5*inch,bottomMargin=0.5*inch)

        vnsoft_style1=copy.deepcopy(stylesheet["Heading1"])
        vnsoft_style1.fontSize=24
        elements.append(Paragraph('<font name="hei">%s</font>'%(risk_name,),vnsoft_style1))
        elements.append(Spacer(1,12))

        vnsoft_style = copy.deepcopy(stylesheet["Heading1"])
        vnsoft_style.fontSize=24
        vnsoft_style.alignment = TA_RIGHT
        data = [['序号','箱号','编号','姓名','性别']]
        for i in datas:
            data.append(i)

        #ts = [('ALIGN',(0,0),(-1,-1),'CENTER'),('FONT', (0,0), (-1,-1), 'hei')]
        ts=[
            ('FONT', (0,0), (-1,-1), 'hei'),

            ("ALIGN",(0,0),(1,-1),"CENTER"),
            ("ALIGN",(-1,0),(-1,-1),"CENTER"),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("LEADING",(0,0),(-1,-1),24),
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
            ('BOX', (0,0), (-1,-1), 0.25, colors.black),
            ("FONTSIZE",(0,0),(-1,-1),20),
            ]
        #TableStyle()
        table = Table(data, 0.8*inch, 0.64*inch, ts)
        table._argW[2]=1.8*inch
        table._argW[3]=3.5*inch
        elements.append(table)

        elements.append(Paragraph('<font name="hei">%s</font>'%(footer_name,),vnsoft_style))
        elements.append(Spacer(1,12))

        doc.build(elements)
