#!coding=utf-8
import SimpleHTTPServer 
import SocketServer 
import cgi 
import webbrowser
import os,shutil

PORT = 8800 
 
class ServerHandler(SimpleHTTPServer.SimpleHTTPRequestHandler): 
 
    def do_GET(self): 
        SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self) 
 
    def do_POST(self): 
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
 
Handler = ServerHandler 
 
httpd = SocketServer.TCPServer(("", PORT), Handler) 
 
print "serving at port", PORT 
webbrowser.open("http://localhost:8800")
httpd.serve_forever() 
