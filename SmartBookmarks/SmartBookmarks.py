from time import time
import datetime
import os
import  shutil
import webbrowser
import argparse
import ttk
from Tkinter import *
import Tkinter as tk
from tkFileDialog import askopenfilename
import tkMessageBox
import train_classifier 
import predict_folders
from bookmark_db import database
from ml_add import add
from bmedit import edit
from bmsearch import *


def load_file(custom_path):
	if not os.path.exists("data"):
		os.makedirs("data")
	dest = "data/"
	filepath = os.path.expanduser("~/.config/google-chrome/Default/Bookmarks")
	if not os.path.exists("data/Bookmarks"):
		if custom_path == 1:
			openfilewin = Tk()
			openfilewin.withdraw()
			bmfile = askopenfilename(parent = openfilewin,filetypes = (("Chrome bookmark file", "Bookmarks"),))
			shutil.copy(os.path.abspath(bmfile),os.path.abspath(dest))
			openfilewin.destroy()
		else:
			shutil.copy(filepath,os.path.abspath(dest))


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
				self.tree.insert(id,"end",text = "".join([ch for ch in bookm.name if ord(ch)<= 128]),tags = ["url",bookm.id])


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










parser = argparse.ArgumentParser(description='Smart Bookmarks.')
parser.add_argument('--custom-file', dest='custom', action='store_const',const=1, default=0,help='chose a custom chrome bookmarks file')
#args = sys.argsgv[1:]
args = parser.parse_args()
load_file(args.custom)
app = mainui()
app.start()
app.db.con.commit()
