#coding:utf-8

import Tkinter # import the Tkinter module

def printReturn(event):
    print '<Return>',sel.get()
    sel.delete(0,Tkinter.END)

root = Tkinter.Tk() # create a root window
root.title("人和未来收货扫码系统")
sel = Tkinter.Entry(root,font=(u"宋体","24","bold"))
sel.pack()
root.lift()
# Return事件处理函数

sel.bind('<Return>',printReturn)
sel.focus()
root.mainloop() # create an event loop