#!coding=utf-8
import SimpleHTTPServer 
import SocketServer 
import cgi 
import webbrowser

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
        print form
        SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self) 
 
Handler = ServerHandler 
 
httpd = SocketServer.TCPServer(("", PORT), Handler) 
 
print "serving at port", PORT 
webbrowser.open("http://localhost:8800")
httpd.serve_forever() 
