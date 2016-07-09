import train_classifier 
import predict_folders
from bookmark_db import database
from time import time
from Tkinter import *
import ttk
import datetime
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


class smart(object):
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
	    	w = Tk()
	    	id =  self.tree.item(curItem)['tags'][1]
	    	w.destroy()

	def selecteditem(self,a):
	    curItem = self.tree.focus()
	    if self.tree.item(curItem)['tags'][0] == "url":
	    	self.current = (1,self.tree.item(curItem)['tags'][1])
	    else:
	    	self.current = (0,self.tree.item(curItem)['text'])
	    print self.current


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
		print "predicted :",predictions[0]
		print "\n".join(predictions[1:])
		print "enter option"
		inp = int(raw_input())
		folder = predictions[inp]
		sql = "insert into bookmarks(folder,name,url) values(?,?,?)"
		self.db.sql(sql,(folder,name,url))
		self.update_tree()


	def edit(self):
		print "edit was pushed"
		if self.current[0]==0:
			#folder
			print "new folder"
			newval = str(raw_input())
			sql = "update bookmarks set folder = ? where folder = ?"
			self.db.sql(sql,(newval,self.current[1]))
		else:
			#url
			sql = "select * from bookmarks where id = ?"
			bookm = bookmark(self.db.sqlselect(sql,(self.current[1],))[0])
			print bookm.id
			print "enter name"
			bookm.name = str(raw_input())
			print "enter url"
			bookm.url = str(raw_input())
			print "enter folder"
			bookm.folder = str(raw_input())
			sql = "update bookmarks set folder = ?, name = ?, url = ? where id = ?"
			self.db.sql(sql,(bookm.folder,bookm.name,bookm.url,self.current[1]))
		self.update_tree()



	def delete(self):
		print "delete was pushed"
		if self.current[0]==0:
			#folder
			print "folder to delete " + self.current[1]
			sql = "delete from bookmarks where folder = ?"
			self.db.sql(sql,(self.current[1],))
			print "deleted"
		else:
			#url
			sql = "select * from bookmarks where id = ?"
			bookm = bookmark(self.db.sqlselect(sql,(self.current[1],))[0])
			print "delete ",bookm.name,bookm.id
			sql = "delete from bookmarks where id = ?"
			self.db.sql(sql,(self.current[1],))
			print "deleted"
		self.update_tree()

	def update_tree(self):
		self.tree.destroy()
		self.read()
		self.build_tktree()
		self.tree.pack()
		

	
	def read(self):
		self.bmbar = {}
		a = self.db.sqlselect("select * from bookmarks order by folder asc")
		for bm in a:
			bookm = bookmark(bm)
			if bookm.folder not in self.bmbar.keys():
				self.bmbar[bookm.folder] = []
			self.bmbar[bookm.folder].append(bookm)
		print len(self.bmbar)


	def build_tktree(self):
		self.tree = ttk.Treeview(self.ft,height = 20) 
		self.tree.column("#0",minwidth=500,width=1000,stretch = True)
		self.tree.bind('<Double-Button-1>', self.selectedurl)
		self.tree.bind('<ButtonRelease-1>', self.selecteditem)
		for key in sorted(self.bmbar.keys()):
			id = self.tree.insert("","end",text = key,tags = "folder")
			for bookm in self.bmbar[key]:
				self.tree.insert(id,"end",text = bookm.name,tags = ["url",bookm.id])
		print "time taken ",time()-self.t0


	def create_layout(self):
		self.root = Tk()
		self.ft = Frame(self.root)
		bt = Frame(self.root)
		tt = Frame(self.root)
		b1 = Button(bt,text="ADD")
		b2 = Button(bt,text="EDIT")
		b3 = Button(bt,text="DELETE")
		b1.configure(command = self.add)
		b2.configure(command = self.edit)
		b3.configure(command = self.delete)
		b1.pack(side = LEFT,padx = 10,pady =5)
		b2.pack(side = LEFT,padx = 10,pady =5)
		b3.pack(side = LEFT,padx = 10,pady =5)
		self.build_tktree()
		self.tree.pack()
		self.ft.pack()
		tt.pack()
		bt.pack()

	def start(self):
		self.create_layout()
		self.root.mainloop()

		
app = smart()
app.start()