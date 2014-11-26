#coding:utf-8

import Tkinter as Tk# import the Tkinter module
import xmlrpclib
import tkMessageBox
import datetime
import ImageTk

class MyApp(object):
    def __init__(self, parent):
        """Constructor"""
        self.root = parent
        self.root.title("Main frame")
        self.frame = Tk.Frame(parent)
        self.centerWindow(self.root,320,180)
        self.root.title("人和未来收货扫码系统")
        Tk.Label(self.root,text="帐号：",font=(u"宋体","14","bold")).grid(row=0)
        Tk.Label(self.root).grid(row=1)
        Tk.Label(self.root,text="密码：",font=(u"宋体","14","bold")).grid(row=2)

        #Tkinter.Entry(root,font=(u"宋体","24","bold"))
        self.sel1 = Tk.Entry(self.root,font=(u"宋体","14","bold"))
        self.sel1.grid(row=0,column=1)
        self.sel2 = Tk.Entry(self.root,font=(u"宋体","14","bold"),show="*")
        self.sel2.grid(row=2,column=1)
        Tk.Label(self.root).grid(row=3)
        self.btn = Tk.Button(self.root,font=(u"宋体","14","bold"),text="  登录  ",command=self.login)
        self.btn.grid(row=4,column=0,columnspan=2)
        self.sel1.focus()
        self.data=[]
        self.count1 = 0
        self.count2 = 0

    def openFrame(self):
        """"""
        self.root.withdraw()
        self.otherFrame = Tk.Toplevel()

        self.centerWindow(self.otherFrame,520,200)
        self.otherFrame.title("扫描收货")
        #handler = lambda: self.onCloseOtherFrame(otherFrame)
        self.btn = Tk.Entry(self.otherFrame,font=(u"宋体","34","bold"))
        self.label1 = Tk.Label(self.otherFrame,text="已扫描快递单数量：")
        self.label1.grid(row=1)
        self.labval1 = Tk.Entry(self.otherFrame,width=3)
        self.labval1.grid(row=1,column=1,sticky=Tk.W)
        self.label2 = Tk.Label(self.otherFrame,text="已扫描样品数量：")
        self.label2.grid(row=2)
        self.labval2 = Tk.Entry(self.otherFrame,width=3)
        self.labval2.grid(row=2,column=1,sticky=Tk.W)
        self.btn.grid(row=0,columnspan=2)
        Tk.Label(self.otherFrame,text="-------------------------------------------------------------------------------------------------------").grid(row=3,columnspan=2,sticky=Tk.W)
        Tk.Label(self.otherFrame,text="1.扫描收货时，请注意当前窗口是在激活状态，光标停留在上面的输入框。").grid(row=4,columnspan=2,sticky=Tk.W)
        Tk.Label(self.otherFrame,text="2.收货时，先扫描快递单号码，再依次扫描里面的样品标签号。").grid(row=5,columnspan=2,sticky=Tk.W)
        Tk.Label(self.otherFrame,text="3.一个包裹中的样品全部扫码完成以后，扫描一个特定的结束标签码。").grid(row=6,columnspan=2,sticky=Tk.W)

        photo = Tk.PhotoImage(file='barcode.gif')
        label = Tk.Label(image=photo)
        label.grid(row=7, column=0, columnspan=2, rowspan=2, sticky=Tk.W+Tk.E+Tk.N+Tk.S, padx=50, pady=50)
        self.btn.bind("<Return>",self.printReturn)
        self.btn.focus()
        self.otherFrame.protocol('WM_DELETE_WINDOW',self.printProtocol)

    def centerWindow(self,win,w,h):

        sw = win.winfo_screenwidth()
        sh = win.winfo_screenheight()

        x = (sw - w)/2
        y = (sh - h)/2
        win.geometry('%dx%d+%d+%d' % (w,h,x,y))

    def printProtocol(self):
        self.root.destroy()
# 使用protocol将WM_DELETE_WINDOW与printProtocol绑定

    def printReturn(self,event):
        no = self.btn.get()
        if no.__len__()==0:return
        if self.data:
            if no=="0000000000":
                self.write(self.data)
                self.data=[]
            else:
                self.count2 += 1
                self.labval2.delete(0,Tk.END)
                self.labval2.insert(0, str(self.count2))
                self.data.append(no)
        else:
            if no=="0000000000":return
            self.count1 += 1
            self.labval1.delete(0,Tk.END)

            self.labval1.insert(0,str(self.count1))
            self.data.append(no)

        self.btn.delete(0,Tk.END)

    def login(self):
        self.username = self.sel1.get()
        self.pwd = self.sel2.get()
        self.db="test"
        self.url = 'http://127.0.0.1:8069'
        s_sock_common = xmlrpclib.ServerProxy(self.url+'/xmlrpc/common')
        self.s_uid = s_sock_common.login(self.db, self.username, self.pwd)
        if not self.s_uid:
            tkMessageBox.showerror("错误", "帐号、密码不能通过验证，请重新输入。")
            return True
        else:
            self.openFrame()
            self.otherFrame.focus()

    def write(self,vals):
        s_sock = xmlrpclib.ServerProxy(self.url + '/xmlrpc/object')
        data = {
            "receiv_real_qty":vals.__len__() - 1,
            "product_qty": vals.__len__() - 1,
            "deliver_partner":1,
            "receiv_partner":self.s_uid,
            "num_express":vals[0],
            "receiv_user":self.s_uid,
            "receiv_real_user":self.s_uid,
            "state":"done"
            #"receiv_real_date":datetime.datetime.now(),
        }

        #print data
        id = s_sock.execute(self.db, self.s_uid, self.pwd, 'stock.picking.express','search',[('num_express','=',vals[0])])
        if not id:
            id = s_sock.execute(self.db, self.s_uid, self.pwd, 'stock.picking.express', 'create',data)
        else:
            s_sock.execute(self.db, self.s_uid, self.pwd, 'stock.picking.express','write',id,{"receiv_real_qty":vals.__len__() - 1,"receiv_real_user":self.s_uid,})
        if isinstance(id,(list,tuple)):
            id = id[0]
        ids=[]
        for i in vals[1:]:
            detail = s_sock.execute(self.db, self.s_uid, self.pwd, 'stock.picking.express.detail','search',[('parent_id','=',id),('number_seq','=',i)])
            if detail:
                s_sock.execute(self.db, self.s_uid, self.pwd, 'stock.picking.express.detail','write',detail,{"in_flag":True})
                ids.append(detail)
            else:
                ids.append( s_sock.execute(self.db, self.s_uid, self.pwd, 'stock.picking.express.detail','create',{"parent_id":id,"number_seq":i,"in_flag":True}))
        s_sock.execute(self.db, self.s_uid, self.pwd, 'stock.picking.express', 'write',id,{"detail_ids":[[6,False,ids]]})

if __name__ == "__main__":
    root = Tk.Tk()
    #root.geometry("800x600")
    app = MyApp(root)
    root.mainloop()
