#!coding=utf-8
import SimpleHTTPServer 
import SocketServer 
import cgi 
import webbrowser
import os,shutil
import xlrd
import xlwt

PORT = 8800 
 
class ServerHandler(SimpleHTTPServer.SimpleHTTPRequestHandler): 
 
    def do_GET(self): 
        SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self) 

    def do_POST(self):
        page = self.path.split("?")[-1].split("=")[-1]
        if page=="1":
            self.do_page1()
        elif page=="2":
            self.do_page2()

    def do_page1(self):
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
                     'CONTENT_TYPE':self.headers['Content-Type'],
                     })
        d={}

        for i in form:
            d[i]=form.getvalue(i)

        if not d.get("source_dir"):
            self.wfile.write("请指定来源数据文件夹。")
            return
        if not d.get("target_dir"):
            self.wfile.write("请指定目标数据文件夹。")
            return
        if not os.path.exists(d.get("source_dir")):
            self.wfile.write("来源数据文件夹不存在。")
            return
        if not os.path.exists(d.get("target_dir")):
            self.wfile.write("目标数据文件夹不存在。")
            return
        for p,dd,f in os.walk(d.get("source_dir")):
            if not f:continue
            for l in f:
                if len(l.split("_"))!=4:
                    self.wfile.write("文件名称格式不正确:"+os.path.join(p,l))
                    return
                if d.get("data_format")=="wh":
                    dname=l.split("_")[1]
                else:
                    dname=l.split("_")[2]

                if not os.path.exists(os.path.join(d.get("target_dir"),dname)):
                    os.mkdir(os.path.join(d.get("target_dir"),dname))
                if os.path.exists(os.path.join(os.path.join(d.get("target_dir"),dname),l)):
                    os.remove(os.path.join(os.path.join(d.get("target_dir"),dname),l))
                shutil.copy(os.path.join(p,l),os.path.join(os.path.join(d.get("target_dir"),dname),l))
        SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self) 

    def do_page2(self):
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
                     'CONTENT_TYPE':self.headers['Content-Type'],
                     })
        d={}

        for i in form:
            d[i]=form.getvalue(i)

        if not d.get("source_dir"):
            self.wfile.write("请指定Excel来源数据文件。")
            return
        source_file = d.get("source_dir")
        if not os.path.exists(source_file):
            self.wfile.write("指定的来源数据文件不存在。")
            return
        try:
            bk = xlrd.open_workbook(source_file)
            sh = bk.sheet_by_index(0)
        except:
           self.wfile.write("请确认文件格式是否为正确的报告标准格式。")
           return

        nrows = sh.nrows
        ncols = sh.ncols
        data={}
        header_list=[]
        for i in range(1,nrows):
            k = sh.cell_value(i,5)
            if isinstance(k,(float,)):
                k = k.__trunc__()
            if not data.has_key(k):
                data[k]={}
            k1 = sh.cell_value(i,4)
            if k1=="deletion":
                Orig_GT = sh.cell_value(i,7)

                if header_list.count("GSTT1")==0:
                    header_list.append("GSTT1")
                if header_list.count("GSTM1")==0:
                    header_list.append("GSTM1")
                if Orig_GT=="VIC/VIC":
                    data[k]["GSTT1"] = "P"
                    data[k]["GSTM1"] = "D"
                if Orig_GT=="VIC/FAM":
                    data[k]["GSTT1"] = "P"
                    data[k]["GSTM1"] = "P"
                if Orig_GT=="FAM/FAM":
                    data[k]["GSTT1"] = "D"
                    data[k]["GSTM1"] = "P"
                if Orig_GT=="U":
                    Flags = sh.cell_value(i,9)
                    u_tip=""
                    if Flags!="NoAmplification":
                        u_tip = "("+Flags+")"
                    data[k]["GSTT1"] = "D"+u_tip
                    data[k]["GSTM1"] = "D"+u_tip

            else:
                if isinstance(k1,(float,)):
                    k1 = k1.__trunc__()
                if header_list.count(k1)==0:
                    header_list.append(k1)
                data[k][k1] = sh.cell_value(i,8)

        w = xlwt.Workbook(encoding='utf-8')
        ws = w.add_sheet("Sheet1")
        header_list.sort()
        ws.write(0,0,"Sample id")
        ws.write(0,1,"Unknown Count")
        col_count=2
        for i in header_list:
            ws.write(0,col_count,i)
            col_count+=1

        row_count=1
        for k,v in data.items():
            ws.write(row_count,0,str(k))
            u_count = 0
            for i in header_list:
                ws.write(row_count,header_list.index(i)+2,v.get(i,""))
                if v.get(i,"")=="U":
                    u_count += 1
            ws.write(row_count,1,str(u_count))
            row_count+=1
        w.save(os.path.join(os.path.split(source_file)[0],u"芯片数据.xls"))
        SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

Handler = ServerHandler 
 
httpd = SocketServer.TCPServer(("", PORT), Handler) 
 
print "serving at port", PORT 
webbrowser.open("http://localhost:8800")
httpd.serve_forever() 
