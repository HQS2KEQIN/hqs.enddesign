from tkinter import *
from PIL import Image, ImageTk
import tkinter as tk
from enddesign import download
from tkinter import  ttk
from tkinter.filedialog import askdirectory
import tkinter.messagebox as msgbox
import threading,time
class basedesk():
    def __init__(self, master):
        self.root = master
        self.root.config()
        self.root.title('Arxiv论文下载器')
        self.root.geometry('549x640')
        initface(self.root)

class initface():
    def __init__(self, master):
        self.master = master
        self.master.config(bg='#F0FFF0')
        # 基准界面initface
        self.initface = tk.Frame(self.master,bg='#F0FFF0')
        self.initface.pack()
        self.path = tk.StringVar()
        img=Image.open("../enddesign/data/zhuye.png")
        imgzhuye=ImageTk.PhotoImage(img)
        self.img=Label(self.initface,image=imgzhuye)
        self.image=imgzhuye
        self.img.pack()
        self.title=Label(self.initface,text="A R X I V 下 载 器",font=("黑体",20,'italic','bold'),fg='#0066CC',bg='#F0FFF0').pack(side='top')
        self.frame1=Frame(self.initface,bg='#A6FFFF',height=5,width=549).pack()
        file = open("data1.txt", encoding='utf-8')
        with open("data1.txt", "a+", encoding="utf-8") as f:
            file2 = [x.strip() for x in file.readlines() if x.strip() != '']
        self.label1 = Label(self.initface, text="下载内容", font=("宋体",12,'bold'), fg="black",bg='#F0FFF0').pack(side='top')
        self.entry1 = ttk.Combobox(self.initface)
        self.entry1['value']=[i for i in file2]
        self.entry1.pack(side='top')
        self.label2 = Label(self.initface, text="下载数量", font=("宋体", 12,'bold'), fg="black",bg='#F0FFF0').pack(side='top')
        self.entry2 = Entry(self.initface, font=("宋体", 12), fg="black")
        self.entry2.pack(side='top')
        self.label3 = Label(self.initface, text="保存地址", font=("宋体", 12,'bold'), fg="black",bg='#F0FFF0').pack(side='top')
        self.entry3 = ttk.Combobox(self.initface,textvariable=self.path)
        self.entry3['value']=['C:/','D:/','F:/']
        self.entry3.pack(side='top')
        self.button = Button(self.initface, text="路径选择", font=("宋体", 10,'bold'), fg="blue", command=self.selectPath).pack(anchor=E,padx=120)
        self.button1 = Button(self.initface, text="下载", font=("宋体", 14,'bold'), fg="blue", command=self.fun1).pack(side='top')
        self.frame2=Frame(self.initface,bg='#A6FFFF',height=5,width=549).pack()

    def fun1(self):
        # 获取输入框的值
        if msgbox.askquestion('确认操作', '确认下载这些论文吗？')=='yes':
            query = self.entry1.get()
            num = self.entry2.get()
            path = self.entry3.get()
            if download.dload(query,num, path)==1:
                return msgbox.showerror("无法下载",f"{query}没有结果")
            elif download.dload(query,num, path)[0]==0:
                return msgbox.showerror("无法下载",f"只能找到{download.dload(query,num, path)[1]}篇")
            else:
                download.dload(query, num, path)


    def selectPath(self):
        path_ = askdirectory()
        self.path.set(path_)

if __name__ == '__main__':
    root = tk.Tk()
    basedesk(root)
    root.mainloop()