from Tkinter import *
import Tkinter as tk
import ttk
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