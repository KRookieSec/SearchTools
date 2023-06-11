# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import csv
import os
import datetime
import base64
import yaml
import requests

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    #读取配置信息
    def read_config(self,arg):
        curPath = os.path.dirname(os.path.realpath(__file__))
        yamlPath = os.path.join(curPath, "config.yaml")
        f = open(yamlPath, 'r', encoding='utf-8')
        cfg = f.read()
        d = yaml.load(cfg,Loader=yaml.FullLoader)
        return d[arg]

    #fofa api调用
    def fofa_search(self,query,proxy):
        fofa_config = self.read_config('fofa')
        email = fofa_config['email']
        api_key = fofa_config['api_key']
        size = fofa_config['size']
        arg = query
        sbase64 = (base64.b64encode(arg.encode('utf-8'))).decode('utf-8')
        api = r'https://fofa.info/api/v1/search/all?email={}&key={}&qbase64={}&size={}'    
        respone = requests.get(api.format(email,api_key,sbase64,size),proxy)
        results = respone.json()["results"]
        print("共搜索到{}条记录！".format(len(results)))
        return results

    def create_widgets(self):
        #创建查询框
        self.query_label = tk.Label(self, text="查询语句：")
        self.query_label.grid(row=0, column=0, sticky="w")
        self.query_entry = tk.Entry(self, width=100)
        self.query_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=5)

        #创建提交按钮
        self.submit_button = tk.Button(self, text="提交", command=self.submit_query)
        self.submit_button.grid(row=0, column=3, padx=5, pady=5)

        #创建表格显示框
        self.table = ttk.Treeview(self, columns=("ID","URL", "IP","PORT"), show="headings")
        self.table.heading("ID", text="ID")
        self.table.heading("URL", text="URL")
        self.table.heading("IP", text="IP")
        self.table.heading("PORT", text="PORT")
        self.table.grid(row=1, column=0, columnspan=4, padx=5, pady=5)
        
        #创建滚动条
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.table.yview)
        self.scrollbar.grid(row=1, column=4, sticky="ns")
        self.table.configure(yscrollcommand=self.scrollbar.set)

        #创建导出按钮
        self.export_button = tk.Button(self, text="导出", command=self.export_data)
        self.export_button.grid(row=2, column=0, padx=5, pady=5)

        #创建清空按钮
        self.clear_button = tk.Button(self, text="清空", command=self.clear_data)
        self.clear_button.grid(row=2, column=3, padx=5, pady=5)

    def submit_query(self):
        #获取查询语句
        query = self.query_entry.get()
        #调用fofa api获取结果
        config = self.read_config('http')
        proxy = config['proxy']
        results = self.fofa_search(query, proxy)
        #清空表格
        self.table.delete(*self.table.get_children())
        id = 1
        #将结果添加到表格中
        for addr in results:
            URL = addr[0]
            ip = addr[1]
            port = addr[2]
            self.table.insert("", "end", values=(id,URL, ip,port))
            id = id + 1

    def export_data(self):
        #获取当前时间
        now = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        #设置文件名
        filename = "fofa_{}.csv".format(now)
        #打开文件对话框，选择保存路径
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile=filename)
        #如果用户选择了保存路径，则将数据保存到文件中
        if file_path:
            with open(file_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["ID","URL", "IP","PORT"])
                for child in self.table.get_children():
                    values = self.table.item(child)["values"]
                    writer.writerow(values)

    def clear_data(self):
        #清空表格
        self.table.delete(*self.table.get_children())    

root = tk.Tk()
root.title("SearchTools")
app = Application(master=root)
app.mainloop()







