from Tkinter import *
import Tkinter as tk
import ttk
from bmedit import bookmark
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