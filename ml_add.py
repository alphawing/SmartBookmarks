from Tkinter import *
import Tkinter as tk
import ttk
import predict_folders
import tkMessageBox

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
		#print "showing get url"
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
		#print "get url frame created"
		self.pack()
		#self.tkraise()


	def thisfuncu(self):
		#print "im in here"
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
		#print "in geturl"
		uu = StringVar(self);
		
		self.l1 = Label(self,text = "Unable to reach url , enter name manually",pady = 7,padx = 8).grid(row = 0,column = 0,columnspan = 2,sticky = W+E)
		self.l2 = Label(self,text = "Name",pady = 7,padx = 8).grid(row = 1,column = 0,sticky = W)
		self.e2 = Entry(self,textvariable = uu,width = 60)
		self.e2.grid(row = 1,column = 1)
		self.b1 = Button(self,text="Submit",padx = 8,pady = 7)
		self.b1.configure(command = self.thisfuncu)
		self.b1.grid(row = 1,column = 2)
		self.pack()
		self.tkraise()

	def thisfuncu(self):
		self.controller.name = self.e2.get()
		normalised_name = predict_folders.process_name(self.controller.name)
		self.controller.urlfeatures = "".join([normalised_name," ",self.controller.urlfeatures])
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
		l3 = Label(self,text = "The list on the right containes folders predicted using machine learning.\nThe Url and title (name) of the existing bookmarks are used to train a classifier according to which the new bookmarks are assigned a folder.The predictions are sorted in accordance to relevance.\nYou can select any predicted folder or write the folder name yourself !",pady = 7,padx = 8,wraplength = 275,justify = LEFT)
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