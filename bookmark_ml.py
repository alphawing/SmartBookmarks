import train_classifier 
import predict_folders
from bookmark_db import database
from time import time
from Tkinter import *
import Tkinter as tk
import ttk
import datetime
import os
import  shutil
from tkFileDialog import askopenfilename
import tkMessageBox
import webbrowser

def load_file():
	if not os.path.exists("data"):
		os.makedirs("data")
	dest = "data/"
	if not os.path.exists("data/Bookmarks"):
		openfilewin = Tk()
		bmfile = askopenfilename(parent = openfilewin,filetypes = (("Chrome bookmark file", "Bookmarks"),))
		shutil.copy(os.path.abspath(bmfile),os.path.abspath(dest))
		openfilewin.withdraw()

class bookmark(object):
	def __init__(self,tup = None):
		self.id = 0
		self.folder = ""
		self.name = ""
		self.url = ""
		self.date = 0
		if tup:
			self.id = tup[0]
			self.folder = tup[1]
			self.name = tup[2]
			self.url = tup[3]
			self.date = tup[4]
	def getforview(self):
		tup = (self.id,self.folder,self.name,self.url,self.get_date(self.date))
		return tup

	def get_date(self):
		t = self.convert_time(self.date)
		return t.strftime('%H:%M:%S %Y-%m-%d')
	def convert_time(self,d):
		seconds, micros = divmod(d, 1000000)
		days, seconds = divmod(seconds, 86400)
		return datetime.datetime(1601, 1, 1) + datetime.timedelta(days, seconds, micros)


class mainui(object):
	def __init__(self):
		self.dpath = "./data/test.db"
		self.fpath = "./data/Bookmarks"
		self.currurl = ""
		self.db = database(self.dpath,self.fpath)
		self.t0 = time()
		self.db.get_features()
		self.clf,self.vectorizer,self.Training_error = train_classifier.train()
		self.bmbar = {}
		self.read()

	def selectedurl(self,a):
	    curItem = self.tree.focus()
	    if self.tree.item(curItem)['tags'][0] == "url":
	    	id =  self.tree.item(curItem)['tags'][1]
	    	self.openinbrowser()

	def selecteditem(self,a):
	    curItem = self.tree.focus()
	    if self.tree.item(curItem)['tags'][0] == "url":
	    	self.current = (1,self.tree.item(curItem)['tags'][1])
	    	sql = "select * from bookmarks where id = ?"
	    	bookm = bookmark(self.db.sqlselect(sql,(self.current[1],))[0])
	    	self.textd.show(bookm.url)	
	    	self.currurl = bookm.url    	
	    else:
	    	self.current = (0,self.tree.item(curItem)['text'])
	    #print self.current



	def add(self):
		a = add(self.db,self.clf,self.vectorizer,self)
		self.update_tree()

	def edit(self):
		e = edit(self.current,self.db)
		self.update_tree()


	def search(self):
		s = search(self.db)


	def delete(self):
		if self.current[0]==0:
			#folder
			sql = "delete from bookmarks where folder = ?"
			self.db.sql(sql,(self.current[1],))
		else:
			#url
			sql = "select * from bookmarks where id = ?"
			bookm = bookmark(self.db.sqlselect(sql,(self.current[1],))[0])
			sql = "delete from bookmarks where id = ?"
			self.db.sql(sql,(self.current[1],))
		self.update_tree()

	def update_tree(self):
		self.tree.destroy()
		self.read()
		self.build_tktree()
		self.tree.pack(side = LEFT)
		self.S.configure(command=self.tree.yview)
		self.tree.configure(yscroll=self.S.set,height = 20)
		

	
	def read(self):
		self.bmbar = {}
		a = self.db.sqlselect("select * from bookmarks order by folder asc")
		for bm in a:
			bookm = bookmark(bm)
			if bookm.folder not in self.bmbar.keys():
				self.bmbar[bookm.folder] = []
			self.bmbar[bookm.folder].append(bookm)


	def build_tktree(self):
		self.tree = ttk.Treeview(self.ft,height = 20) 
		self.tree.column("#0",minwidth=500,width=1000,stretch = True)
		self.tree.heading('#0', text="Bookmarks", anchor='w')
		self.tree.bind('<Double-Button-1>', self.selectedurl)
		self.tree.bind('<ButtonRelease-1>', self.selecteditem)
		for key in sorted(self.bmbar.keys()):
			id = self.tree.insert("","end",text = key,tags = "folder")
			for bookm in self.bmbar[key]:
				self.tree.insert(id,"end",text = bookm.name,tags = ["url",bookm.id])


	def create_layout(self):
		self.root = Tk()
		self.root.title("Smart Bookmarks")
		self.root.geometry("1020x550+50+50")
		self.ft = Frame(self.root)
		self.tt = Frame(self.root)
		self.textd = display_url(self.tt)
		bt = Frame(self.root)
		b1 = Button(bt,text="Copy Url",command = self.toclipboard)
		b2 = Button(bt,text="Browse",command = self.openinbrowser)
		menubar = Menu(self.root)
		menubar.add_command(label = "Add",command = self.add)
		menubar.add_command(label = "Edit",command = self.edit)
		menubar.add_command(label = "Delete",command = self.delete)
		menubar.add_command(label = "Search",command = self.search)
		self.root.config(menu = menubar)
		#b1.configure(command = self.copyurl)
		#b2.configure(command = self.submit)
		b1.pack(side = LEFT,padx = 10,pady =5)
		b2.pack(side = LEFT,padx = 10,pady =5)
		#b3.pack(side = LEFT,padx = 10,pady =5)
		self.build_tktree()
		self.S = Scrollbar(self.ft, command=self.tree.yview)
		self.tree.configure(yscroll=self.S.set,height = 20)
		self.tree.pack(side = LEFT)
		self.S.pack(side = RIGHT,fill = BOTH)
		self.ft.pack()
		self.tt.pack()
		bt.pack()

	def toclipboard(self):
		root = Tk()
		root.withdraw()
		root.clipboard_clear()
		root.clipboard_append(self.currurl)
		root.destroy()
	def openinbrowser(self):
		try:
			webbrowser.open_new_tab(self.currurl)
		except:
			print "error opening default browser"


	def start(self):
		self.create_layout()
		self.root.mainloop()

class search(object):
	def __init__(self,db):
		self.db = db
		self.swindow = Tk()
		self.swindow.wm_title("Search Bookmarks")
		self.swindow.geometry("1020x550+100+100")
		self.st = Frame(self.swindow)
		ff = StringVar();
		self.e2 = Entry(self.st,textvariable = ff,width = 30)
		self.e2.pack(side =LEFT)
		b1 = Button(self.st,text="Search",padx = 8,pady = 7)
		b1.configure(command = self.dosearch)
		b1.pack(side = LEFT)
		self.st.pack()

	def dosearch(self):
		text = self.e2.get()
		self.ft = Frame(self.swindow)
		self.r=0
		tt = Frame(self.swindow)
		self.textd = display_url(tt)
		self.searchnow(text)
		bt = Frame(self.swindow,padx = 8,pady = 7)
		b1 = Button(bt,text="Close",padx = 8,pady = 7)
		b1.configure(command = self.swindow.destroy,)
		b1.pack(side = LEFT)
		self.ft.pack()
		tt.pack()
		bt.pack()
		if self.r==1:
			self.swindow.destroy()
			tkMessageBox.showinfo("Search Error", "No results found ,try seaching with words in different sequence ")

	def addstar(self,text):
		text =  "*".join(text.split(" "))
		text = "".join(["*",text,"*"])
		return text
		
	def searchnow(self,text):
		text = self.addstar(text)
		results = self.db.search(text)
		if len(results)!=0:
			self.search_read(results)
			self.search_tktree()
			self.tree.pack(side = LEFT)
			S = Scrollbar(self.ft, command=self.tree.yview)
			self.tree.configure(yscroll=S.set,height = 20)
			self.tree.pack(side = LEFT)
			S.pack(side = RIGHT,fill = BOTH)
		else:
			self.r=1
	def selectedurl(self,a):
		curItem = self.tree.focus()
		if self.tree.item(curItem)['tags'][0] == "url":
			id =  self.tree.item(curItem)['tags'][1]

	def selecteditem(self,a):
	    curItem = self.tree.focus()
	    if self.tree.item(curItem)['tags'][0] == "url":
	    	self.current = (1,self.tree.item(curItem)['tags'][1])
	    	sql = "select * from bookmarks where id = ?"
	    	bookm = bookmark(self.db.sqlselect(sql,(self.current[1],))[0])
	    	self.textd.show(bookm.url)	    	
	    else:
	    	self.current = (0,self.tree.item(curItem)['text'])
	    #print self.current

	def search_tktree(self):
		self.tree = ttk.Treeview(self.ft,height = 20)
		self.tree.column("#0",minwidth=500,width=1000,stretch = True)
		self.tree.heading('#0', text="Search Results", anchor='w')
		#self.tree.bind('<Double-Button-1>', self.selectedurl)
		self.tree.bind('<ButtonRelease-1>', self.selecteditem)
		for key in sorted(self.bmbar.keys()):
			id = self.tree.insert("","end",text = key,tags = "folder")
			for bookm in self.bmbar[key]:
				self.tree.insert(id,"end",text = bookm.name,tags = ["url",bookm.id])


	def search_read(self,a):
		self.bmbar = {}
		for bm in a:
			bookm = bookmark(bm)
			if bookm.folder not in self.bmbar.keys():
				self.bmbar[bookm.folder] = []
			self.bmbar[bookm.folder].append(bookm)


class display_url(object):
	def __init__(self,tt):
		self.nn = StringVar();
		self.uu = StringVar();
		self.tt =tt
		#l1 = Label(tt,text = "Name",pady = 7,padx = 8).pack(side = LEFT)
		#self.e1 = Entry(tt,textvariable = self.nn,width = 30)
		#self.e1.pack(side =LEFT)
		l2 = Label(tt,text = "Url",pady = 7,padx = 8).pack(side = LEFT)
		self.e2 = Entry(tt,textvariable = self.uu,width = 60)
		self.e2.pack(side =LEFT)
	def show(self,url):
		#self.e1.insert(0, name)
		self.e2.delete(0, 'end')
		self.e2.insert(0, url)

class edit(object):
	def __init__(self,current,db):
		self.current = current
		self.newval = ""
		self.ttt = Tk()
		self.ttt.wm_title("Edit Bookmarks")
		self.ttt.geometry("+90+90")
		self.a =1
		if self.current[0]==0:
			#folder
			self.get_folder(self.ttt)
			sql = "update bookmarks set folder = ? where id in (select id from bookmarks where folder = ?)"
			db.sql(sql,(self.newval,self.current[1]))
			db.con.commit()
		else:
			#url
			sql = "select * from bookmarks where id = ?"
			self.bookm = bookmark(db.sqlselect(sql,(self.current[1],))[0])
			self.get_bookm(self.ttt,self.bookm)
			sql = "update bookmarks set folder = ?, name = ?, url = ? where id = ?"
			db.sql(sql,(self.bookm.folder,self.bookm.name,self.bookm.url,self.current[1]))
			db.con.commit()

	def get_bookm(self,ttt,bookm):
		self.ttt = ttt
		nn = StringVar();
		ff = StringVar();
		uu = StringVar();
		l1 = Label(self.ttt,text = "Name",pady = 7,padx = 8).grid(row = 0,column = 0,sticky = W)
		self.e1 = Entry(self.ttt,textvariable = nn,width = 30)
		self.e1.insert(0, bookm.name)
		self.e1.grid(row = 0,column = 1,sticky = W)
		l2 = Label(self.ttt,text = "Folder",pady = 7,padx = 8).grid(row = 1,column = 0,sticky = W)
		self.e2 = Entry(self.ttt,textvariable = ff,width = 30)
		self.e2.insert(0, bookm.folder)
		self.e2.grid(row = 1,column = 1,sticky = W)
		l3 = Label(self.ttt,text = "Url",pady = 7,padx = 8).grid(row = 2,column = 0)
		self.e3 = Entry(self.ttt,textvariable = uu,width = 60)
		self.e3.insert(0, bookm.url)
		self.e3.grid(row = 2,column = 1)
		b1 = Button(self.ttt,text="Submit",padx = 8,pady = 7)
		b1.configure(command = self.thisfuncb)
		b1.grid(row = 3,column = 1)
		self.ttt.mainloop()

	def get_folder(self,ttt):
		self.ttt = ttt
		ff = StringVar();
		l2 = Label(self.ttt,text = "Folder",pady = 7,padx = 8).grid(row = 0,column = 0)
		self.e2 = Entry(self.ttt,textvariable = ff,width = 30)
		self.e2.grid(row = 0,column = 1)
		b1 = Button(self.ttt,text="Submit",padx = 8,pady = 7)
		b1.configure(command = self.thisfuncf)
		b1.grid(row = 1,column = 1)
		self.ttt.mainloop()
	

	def thisfuncf(self):
		self.newval = self.e2.get()
		self.ttt.quit()
		self.ttt.destroy()
	def thisfuncb(self):
		self.bookm.name = self.e1.get()
		self.bookm.folder = self.e2.get()
		self.bookm.url = self.e3.get()
		self.ttt.quit()
		self.ttt.destroy()


class add(tk.Tk):
	def __init__(self,db,c,v,par):
		tk.Tk.__init__(self)
		self.title("Smart Add Using Machine Learning")
		self.geometry("+60+90")
		self.db = db
		self.c = c
		self.v = v
		self.url = ""
		self.name = ""
		self.folder = ""
		self.predictions = []
		self.urlfeatures = ""
		self.u=0
		self.n=0
		self.f=0
		self.container = Frame(self)
		self.container.pack(side="top", fill="both", expand=True)
		self.frames = {}
		self.fortreeupd = par
		print "showing get url"
		frame = geturl(parent = self.container, controller = self)		
	def show_frame(self, cll):
		'''Show a frame for the given page name'''
		frame = cll(parent = self.container, controller = self)


class geturl(tk.Frame):
	def __init__(self,parent,controller):
		tk.Frame.__init__(self,parent)
		self.controller = controller
		self.get_url()


	def get_url(self):
		uu = StringVar(self);
		self.l2 = Label(self,text = "Url",pady = 7,padx = 8).grid(row = 0,column = 0)
		self.e2 = Entry(self,textvariable = uu,width = 60)
		self.e2.grid(row = 0,column = 1)
		self.b1 = Button(self,text="Submit",padx = 8,pady = 7)
		self.b1.configure(command = self.thisfuncu)
		self.b1.grid(row = 0,column = 2)
		self.l3 = Label(self,text = "Press Submit to retreive webpage title from the web.",pady = 7,padx = 8,justify = LEFT)
		self.l3.grid(row = 1,column = 0,columnspan = 3)
		print "get url frame created"
		self.pack()
		#self.tkraise()


	def thisfuncu(self):
		print "im in here"
		self.controller.url = self.e2.get()
		(self.urlfeatures,self.name) = predict_folders.url_features(self.controller.url)
		self.controller.urlfeatures = self.urlfeatures
		self.controller.name = self.name
		self.b1.destroy()
		self.l3.destroy()
		if self.name == "":
			#self.controller.show_frame("getname")
			self.controller.show_frame(getname)
		else:
			self.controller.name = self.name
			predicted,pred_folder = predict_folders.predict(self.controller.urlfeatures,self.controller.c,self.controller.v)
			a = predicted[0]
			predictions = [str(a)]
			for x in pred_folder:
				predictions.append(str(x))
			self.controller.predictions =predictions
			self.controller.show_frame(getfolder)

class getname(tk.Frame):
	def __init__(self,parent,controller):
		tk.Frame.__init__(self,parent)
		self.controller =controller
		self.get_name()
		self.par = parent

	def get_name(self):
		print "in geturl"
		uu = StringVar(self);
		self.l2 = Label(self,text = "Name",pady = 7,padx = 8).grid(row = 0,column = 0)
		self.e2 = Entry(self,textvariable = uu,width = 60)
		self.e2.grid(row = 0,column = 1)
		self.b1 = Button(self,text="Submit",padx = 8,pady = 7)
		self.b1.configure(command = self.thisfuncu)
		self.b1.grid(row = 0,column = 2)
		self.pack()
		self.tkraise()

	def thisfuncu(self):
		self.controller.name = self.e2.get()
		predicted,pred_folder = predict_folders.predict(self.controller.urlfeatures,self.controller.c,self.controller.v)
		a = predicted[0]
		predictions = [str(a)]
		for x in pred_folder:
			predictions.append(str(x))
		self.controller.predictions =predictions
		self.destroy()
		self.controller.show_frame(getfolder)


class getfolder(tk.Frame):
	def __init__(self,parent,controller):
		tk.Frame.__init__(self,parent)
		self.controller =controller
		self.par = parent
		self.predictions = self.controller.predictions
		self.get_folder()

	def get_folder(self):
		ff = StringVar(self);
		nn = StringVar(self);
		self.l1 = Label(self,text = "Name",pady = 7,padx = 8).grid(row = 1,column = 0,sticky =W)
		self.e1 = Entry(self,textvariable = nn,width = 25)
		self.e1.grid(row = 1,column = 0,sticky =E)
		self.e1.insert("0",self.controller.name)
		l2 = Label(self,text = "Folder",pady = 7,padx = 8).grid(row = 2,column = 0,sticky =W)
		self.e2 = Entry(self,textvariable = ff,width = 25)
		self.e2.insert("0",self.predictions[0])
		self.e2.grid(row = 2,column = 0,sticky =E)
		self.Lb1 = Listbox(self)
		self.Lb1.insert(0, self.predictions[0])
		self.Lb1.insert(1,self.predictions[1])
		self.Lb1.insert(2, self.predictions[2])
		self.Lb1.insert(3, self.predictions[3])
		self.Lb1.insert(4, self.predictions[4])
		self.Lb1.grid(row = 2,column = 1,sticky = E+S,rowspan = 2)
		self.Lb1.bind('<<ListboxSelect>>', self.listselect)
		l3 = Label(self,text = "Predicting folders using machine learning.\nThe Url and title (name) of the existing bookmarks are used to train a classifier according to which the new bookmarks are assigned a folder.The predictions are sorted in accordance to relevance.\nYou can select any predicted folder or write the folder name yourself !",pady = 7,padx = 8,wraplength = 275,justify = LEFT)
		l3.grid(row = 3,column = 0,sticky =W)
		b1 = Button(self,text="Submit",padx = 8,pady = 7)
		b1.configure(command = self.thisfuncf)
		b1.grid(row = 4,columnspan =1)
		self.pack()
		self.tkraise()
	def listselect(self,event):
		index = self.Lb1.curselection()[0]
		value = self.Lb1.get(index)
		self.e2.delete(0, 'end')
		self.e2.insert(0, value)

	def thisfuncf(self):
		self.folder = self.e2.get()
		sql = "insert into bookmarks(folder,name,url) values(?,?,?)"
		self.controller.db.sql(sql,(self.folder,self.controller.name,self.controller.url))
		self.controller.db.con.commit()
		self.controller.fortreeupd.update_tree()
		self.controller.destroy()



load_file()
app = mainui()
app.start()
app.db.con.commit()