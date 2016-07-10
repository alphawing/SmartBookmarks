import train_classifier 
import predict_folders
from bookmark_db import database
from time import time
from Tkinter import *
import ttk
import datetime
import os
import  shutil
from tkFileDialog import askopenfilename
import tkMessageBox

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



	def add(self):
		print "add was pushed"
		print "enter url"
		url = str(raw_input())
		(urlfeatures,name) = predict_folders.url_features(url)
		if name == "":
			print "url not reachable enter name manually"
			name = str(raw_input())
		predicted,pred_folder = predict_folders.predict(urlfeatures,self.clf,self.vectorizer)
		a = predicted[0]
		predictions = [str(a)]
		for x in pred_folder:
			predictions.append(str(x))
		print "predicted :\n",predictions[0]
		print "\n".join(predictions[1:])
		print "enter option"
		inp = int(raw_input())
		if inp == 5:
			print "enter folder"
			folder = str(raw_input())
		else:
			folder = predictions[inp]
		sql = "insert into bookmarks(folder,name,url) values(?,?,?)"
		self.db.sql(sql,(folder,name,url))
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
		self.root.geometry("1020x550+50+50")
		self.ft = Frame(self.root)
		self.tt = Frame(self.root)
		self.textd = display_url(self.tt)
		bt = Frame(self.root)
		b1 = Button(bt,text="Copy Url")
		b2 = Button(bt,text="submit")
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


	def start(self):
		self.create_layout()
		self.root.mainloop()

class search(object):
	def __init__(self,db):
		self.db = db
		self.swindow = Tk()
		self.st = Frame(self.swindow)
		ff = StringVar();
		self.e2 = Entry(self.st,textvariable = ff,width = 30)
		self.e2.pack(side =LEFT)
		b1 = Button(self.st,text="Search",padx = 5,pady = 5)
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
		bt = Frame(self.swindow,padx = 5,pady = 5)
		b1 = Button(bt,text="Close",padx = 5,pady = 5)
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
		#l1 = Label(tt,text = "Name",pady = 5,padx = 5).pack(side = LEFT)
		#self.e1 = Entry(tt,textvariable = self.nn,width = 30)
		#self.e1.pack(side =LEFT)
		l2 = Label(tt,text = "Url",pady = 5,padx = 5).pack(side = LEFT)
		self.e2 = Entry(tt,textvariable = self.uu,width = 60)
		self.e2.pack(side =LEFT)
	def show(self,url):
		#self.e1.insert(0, name)
		self.e2.delete(0, 'end')
		self.e2.insert(0, url)

class edit(object):
	def __init__(self,current,db):
		self.current = current
		#self.newval = ""
		self.ttt = Tk()
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
		l1 = Label(self.ttt,text = "Name",pady = 5,padx = 5).pack(side = LEFT)
		self.e1 = Entry(self.ttt,textvariable = nn,width = 30)
		self.e1.insert(0, bookm.name)
		self.e1.pack(side =LEFT)
		l2 = Label(self.ttt,text = "Folder",pady = 5,padx = 5).pack(side = LEFT)
		self.e2 = Entry(self.ttt,textvariable = ff,width = 30)
		self.e2.insert(0, bookm.folder)
		self.e2.pack(side =LEFT)
		l3 = Label(self.ttt,text = "Url",pady = 5,padx = 5).pack(side = LEFT)
		self.e3 = Entry(self.ttt,textvariable = uu,width = 60)
		self.e3.insert(0, bookm.url)
		self.e3.pack()
		b1 = Button(self.ttt,text="Submit",padx = 5,pady = 5)
		b1.configure(command = self.thisfuncb)
		b1.pack(side = BOTTOM)
		self.ttt.mainloop()

	def get_folder(self,ttt):
		self.ttt = ttt
		ff = StringVar();
		l2 = Label(self.ttt,text = "Folder",pady = 5,padx = 5).pack(side = LEFT)
		self.e2 = Entry(self.ttt,textvariable = ff,width = 30)
		self.e2.pack(side =LEFT)
		b1 = Button(self.ttt,text="Submit",padx = 5,pady = 5)
		b1.configure(command = self.thisfuncf)
		b1.pack(side = LEFT)
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


load_file()
app = mainui()
app.start()
app.db.con.commit()