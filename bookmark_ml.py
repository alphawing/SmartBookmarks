import train_classifier 
import predict_folders
from bookmark_db import database
from time import time
from Tkinter import *
import ttk
dpath = "./data/test.db"
fpath = "./data/Bookmarks"
db = database(dpath,fpath)
t0 = time()
db.get_features()
clf,vectorizer,Training_error = train_classifier.train()
def selectItem(a):
    curItem = tree.focus()
    print tree.item(curItem)
def add():
	print "add was pushed"
	e = Entry(master)
	e.pack()
	e.focus_set()
	
	predicted,pred_folder = predict_folders.predict(clf,vectorizer)
	print "predicted :",predicted
	print "\n".join(pred_folder)
def edit():
	print "edit was pushed"
def delete():
	print "delete was pushed"

a = db.sqlselect("select * from bookmarks")
bmbar = {}
for bm in a:
	if bm[1] not in bmbar.keys():
		bmbar[bm[1]] = []
	bmbar[bm[1]].append((bm[0],bm[2],bm[3],bm[4]))
print len(bmbar)
#for key in bmbar.keys():
#	print "folder                  ",key
#	raw_input()
#	for item in bmbar[key]:
#		print item 
#		raw_input()
#	raw_input()
root = Tk() 
ft = Frame(root)
bt = Frame(root)
b1 = Button(bt,text="ADD")
b2 = Button(bt,text="EDIT")
b3 = Button(bt,text="DELETE")
tree = ttk.Treeview(ft) 
tree["columns"]=("name","date")
tree.column("name", width=200)
tree.column("date", width=200)
tree.heading("name", text="title")
tree.heading("date", text="date added")
 
#tree.insert("" , 0,    text="Line 1", values=("1A","1b"))
 
#id2 = tree.insert("", 1, "dir2", text="Dir 2")
#tree.insert(id2, "end", "dir 2", text="sub dir 2", values=("2A","2B"))
 
##alternatively:
#tree.insert("", 3, "dir3", text="Dir 3")
#tree.insert("dir3", 3, text=" sub dir 3",values=("3A"," 3B"))
tree.bind('<ButtonRelease-1>', selectItem)
for key in bmbar.keys():
	id = tree.insert("","end",text = key,tags = "folder")
	for item in bmbar[key]:
		tree.insert(id,"end",text = item[1],values = (item[2],item[3]),tags = "url")
print "time taken ",time()-t0
b1.configure(command = add)
b2.configure(command = edit)
b3.configure(command = delete)
tree.pack()
b1.pack(side = LEFT,padx = 10,pady =5)
b2.pack(side = LEFT,padx = 10,pady =5)
b3.pack(side = LEFT,padx = 10,pady =5)
ft.pack()
bt.pack()
root.mainloop()
